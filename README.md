<a href="https://api.render.com/deploy/srv-d13svemmcj7s738dqka0?key=w0cLzScxBew" target="_blank">
  <img src="https://img.shields.io/badge/Click%20here-blue?style=plastic&label=If%20the%20login%2Fregister%20takes%20too%20much%20time&labelColor=white" />
</a>

> ⚠ Please allow 3–4 minutes for the app to load when you open it initially. Render's free backend takes time to spin up cold instances (Those which havent been accessed in some time).

# 🚀 FastAPI ToDo App

A full-featured ToDo list app built with **FastAPI**, **vanilla JavaScript**, and a stunning animated launch screen.  
It supports **authentication**, **per-user task storage**, and a **secure admin panel** — all with a clean UI and blazing-fast backend.

---

## ✨ Features

- 🔐 JWT-based login system
- 📝 Per-user task creation, editing, and deletion
- ✅ Mark tasks complete/incomplete
- 🧑‍💼 Admin panel for managing users (only admins)
- 💾 Tasks and users stored in `.json` files
- 📱 Mobile-optimized glowing landing page with smooth trails
- 🔒 Admins cannot delete themselves or other admins
- 🧠 Smart frontend: live validation, dynamic updates, error alerts

---

## 🖼 Fancy Landing Page

The Github Page deployed opens a glowing animated page inspired by Windows' light trails.  
It works on both desktop and mobile, and launches the app which is hosted on Render.

---

## 🛠 Tech Stack

- **Backend**: FastAPI, Uvicorn, Cryptography, JWT
- **Frontend**: HTML, CSS, Vanilla JS, Jinja2
- **Storage**: users.json + tasks.json (per-user)

---

## 📁 Project Structure

```
FastAPI/
├── main.py              # FastAPI backend, auth, task, and admin logic
├── requirements.txt     # Dependencies (for Render + local)
├── templates/
│   ├── login.html       # Login form
│   ├── register.html    # Register form
│   └── tasks.html       # Task manager (SPA)
├── index.html       # Fancy animated launch page
├── users.json           # Stored users (admin & regular)
└── tasks.json           # Stored tasks per user
````

---

## ⚙️ Getting Started Locally

1. **Clone the Repository**

```bash
git clone https://github.com/Argu333/FastAPI.git
cd FastAPI
````

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the app**

```bash
uvicorn main:app --reload
```

4. **Visit the app**

```bash
Open your browser to http://127.0.0.1:8000
```

---

## 🚀 Deployment

### 📦 Render

* Make sure you have:

  * Nothing! I've already done everything so you can go right on in and use it at https://argu333.github.io/FastAPI/

---

## 💬 Credits

Crafted with ❤️ by ArGu
Designed for beauty, speed, and simplicity.
