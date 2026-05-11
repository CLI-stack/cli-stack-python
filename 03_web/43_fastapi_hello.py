"""
Script: FastAPI Hello World
What it does: Creates a modern API with automatic documentation.
FastAPI is faster than Flask and auto-generates interactive API docs.

Install: pip install fastapi uvicorn
Run: uvicorn 43_fastapi_hello:app --reload
Visit docs: http://localhost:8000/docs  ← interactive API documentation!
"""

from fastapi import FastAPI  # FastAPI is a modern, fast web framework

# Create the FastAPI application
app = FastAPI(
    title="My First API",
    description="A beginner-friendly FastAPI example",
    version="1.0.0"
)

# --- Basic route ---
@app.get("/")  # GET request to "/"
def home():
    return {"message": "Hello from FastAPI!", "status": "running"}

# --- Route with path parameter ---
@app.get("/greet/{name}")
def greet(name: str):
    # FastAPI automatically validates that 'name' is a string
    return {"greeting": f"Hello, {name}!", "name": name}

# --- Route with query parameters ---
@app.get("/search")
def search(keyword: str, limit: int = 10):
    # URL: /search?keyword=python&limit=5
    # 'limit' has a default value of 10
    return {
        "keyword": keyword,
        "limit": limit,
        "message": f"Searching for '{keyword}' (max {limit} results)"
    }

# --- Route that returns a list ---
@app.get("/items")
def get_items():
    items = [
        {"id": 1, "name": "Laptop", "price": 1200},
        {"id": 2, "name": "Phone",  "price": 800},
        {"id": 3, "name": "Tablet", "price": 500},
    ]
    return {"items": items, "count": len(items)}

# Note: Run with: uvicorn 43_fastapi_hello:app --reload
# Then visit http://localhost:8000/docs for interactive documentation
