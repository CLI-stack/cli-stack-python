"""
Script: FastAPI Hello World
What it does: Creates a modern, fast web API using FastAPI.
FastAPI is newer than Flask and automatically generates API documentation.
Visit http://localhost:8000/docs for an interactive API explorer!

Install: pip install fastapi uvicorn
Run: uvicorn 47_fastapi_hello:app --reload
Then open: http://localhost:8000 or http://localhost:8000/docs
"""

try:
    from fastapi import FastAPI
    from pydantic import BaseModel  # for data validation

    # Create the FastAPI app
    app = FastAPI(
        title="My First FastAPI",
        description="A beginner FastAPI example",
        version="1.0.0"
    )

    # --- Simple routes ---
    @app.get("/")
    def home():
        """Home endpoint"""
        return {"message": "Hello, World!", "status": "running"}

    @app.get("/about")
    def about():
        return {"app": "FastAPI Demo", "framework": "FastAPI", "python": True}

    # --- Route with path parameter ---
    @app.get("/greet/{name}")
    def greet(name: str):
        """Greet a user by name — visit /greet/Alice"""
        return {"greeting": f"Hello, {name}!", "name": name}

    # --- Route with query parameters ---
    @app.get("/search")
    def search(q: str = "", limit: int = 10):
        """Search endpoint — try /search?q=python&limit=5"""
        # FastAPI automatically validates types (limit must be an int)
        results = [f"Result {i} for '{q}'" for i in range(1, limit + 1)]
        return {"query": q, "limit": limit, "results": results}

    # --- POST with request body (Pydantic model) ---
    class Item(BaseModel):
        name: str
        price: float
        in_stock: bool = True  # default value

    @app.post("/items")
    def create_item(item: Item):
        """Create a new item — FastAPI validates the request body automatically"""
        return {
            "message": "Item created",
            "item": item.dict(),
            "total_value": item.price * (1 if item.in_stock else 0)
        }

    # To run: uvicorn 47_fastapi_hello:app --reload
    print("Run with: uvicorn 47_fastapi_hello:app --reload")
    print("Then visit: http://localhost:8000/docs")

except ImportError:
    print("Install: pip install fastapi uvicorn")
