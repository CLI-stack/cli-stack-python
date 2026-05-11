"""
Script: FastAPI CRUD API
What it does: Creates a full Create, Read, Update, Delete API.
CRUD covers the four fundamental operations for managing data.

Install: pip install fastapi uvicorn pydantic
Run: uvicorn 44_fastapi_crud:app --reload
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  # for request body validation
from typing import Optional

app = FastAPI(title="Task Manager API")

# --- Define the data model ---
class Task(BaseModel):
    """Pydantic model defines the shape of data we accept/return."""
    title: str
    description: str = ""  # optional, defaults to empty string
    done: bool = False

class TaskUpdate(BaseModel):
    """For updates, all fields are optional."""
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None

# In-memory storage (a dictionary: id → task)
tasks = {}
next_id = 1

# --- CREATE: POST /tasks ---
@app.post("/tasks", status_code=201)
def create_task(task: Task):
    global next_id
    task_dict = {"id": next_id, **task.dict()}  # add ID to task data
    tasks[next_id] = task_dict
    next_id += 1
    return task_dict

# --- READ ALL: GET /tasks ---
@app.get("/tasks")
def get_all_tasks():
    return {"tasks": list(tasks.values()), "count": len(tasks)}

# --- READ ONE: GET /tasks/{id} ---
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

# --- UPDATE: PUT /tasks/{id} ---
@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    task = tasks[task_id]
    # Only update fields that were provided
    for field, value in update.dict(exclude_none=True).items():
        task[field] = value
    return task

# --- DELETE: DELETE /tasks/{id} ---
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
    return {"message": f"Task {task_id} deleted"}
