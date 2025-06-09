from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Task Model
class Task(BaseModel):
    id: int
    title: str
    completed: bool = False

# In-memory storage
tasks: List[Task] = []

# Home Route
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI ToDo List!"}

# Get All Tasks
@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return tasks

# Create a Task
@app.post("/tasks", response_model=Task)
def create_task(task: Task):
    if any(t.id == task.id for t in tasks):
        raise HTTPException(status_code=400, detail="Task ID already exists.")
    tasks.append(task)
    return task

# Get Task by ID
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found.")

# Update Task
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks[index] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found.")

# Delete Task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(index)
            return {"message": f"Task {task_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found.")
