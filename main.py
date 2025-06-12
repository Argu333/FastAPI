from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import json, os, jwt, base64

app = FastAPI()
templates = Jinja2Templates(directory="templates")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

USERS_FILE = "users.json"
TASKS_FILE = "tasks.json"
token_blacklist = set()

def hash_password(password: str, salt: bytes) -> str:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100_000, backend=default_backend())
    return base64.urlsafe_b64encode(kdf.derive(password.encode())).decode()

def verify_password(password: str, hashed_password: str, salt: bytes) -> bool:
    return hash_password(password, salt) == hashed_password

def load_users():
    return json.load(open(USERS_FILE)) if os.path.exists(USERS_FILE) else {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_all_tasks():
    return json.load(open(TASKS_FILE)) if os.path.exists(TASKS_FILE) else {}

def save_all_tasks(task_data):
    with open(TASKS_FILE, "w") as f:
        json.dump(task_data, f, indent=2)

task_store = load_all_tasks()

class Task(BaseModel):
    id: int
    title: str
    completed: bool = False

def authenticate_user(username: str, password: str):
    users = load_users()
    user = users.get(username)
    if not user:
        return None
    salt = base64.b64decode(user["salt"])
    if not verify_password(password, user["hashed_password"], salt):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str):
    if token in token_blacklist:
        raise HTTPException(status_code=401, detail="Token has been invalidated")
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")
    users = load_users()
    user = users.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return username

def require_admin(username: str = Depends(get_current_user)):
    users = load_users()
    user = users.get(username)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return username

@app.post("/register")
def register(username: str, password: str):
    users = load_users()
    if username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    salt = os.urandom(16)
    users[username] = {
        "username": username,
        "salt": base64.b64encode(salt).decode(),
        "hashed_password": hash_password(password, salt),
        "is_admin": (username == "admin")
    }
    save_users(users)
    return {"message": "User registered successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    token_blacklist.add(token)
    return {"message": "Logged out successfully"}

@app.get("/users")
def list_users(admin: str = Depends(require_admin)):
    users = load_users()
    return list(users.keys())

@app.delete("/users/{username}")
def delete_user(username: str, admin: str = Depends(require_admin)):
    users = load_users()
    if username not in users:
        raise HTTPException(status_code=404, detail="User not found")
    if username == admin:
        raise HTTPException(status_code=403, detail="You cannot delete your own account")
    if users[username].get("is_admin"):
        raise HTTPException(status_code=403, detail="You cannot delete an admin user")
    del users[username]
    task_store.pop(username, None)
    save_users(users)
    save_all_tasks(task_store)
    return {"message": f"User '{username}' deleted"}

@app.get("/tasks", response_model=List[Task])
def get_tasks(user: str = Depends(get_current_user)):
    return task_store.get(user, [])

@app.post("/tasks", response_model=Task)
def create_task(task: Task, user: str = Depends(get_current_user)):
    user_tasks = task_store.setdefault(user, [])
    if any(t["id"] == task.id for t in user_tasks):
        raise HTTPException(status_code=400, detail="Task ID already exists.")
    user_tasks.append(task.dict())
    save_all_tasks(task_store)
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task, user: str = Depends(get_current_user)):
    user_tasks = task_store.get(user, [])
    for i, t in enumerate(user_tasks):
        if t["id"] == task_id:
            user_tasks[i] = updated_task.dict()
            save_all_tasks(task_store)
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found.")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, user: str = Depends(get_current_user)):
    user_tasks = task_store.get(user, [])
    for i, t in enumerate(user_tasks):
        if t["id"] == task_id:
            user_tasks.pop(i)
            save_all_tasks(task_store)
            return {"message": f"Task {task_id} deleted"}
    raise HTTPException(status_code=404, detail="Task not found.")

@app.get("/", response_class=HTMLResponse)
def serve_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def serve_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/tasks-view", response_class=HTMLResponse)
def serve_tasks(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request})
