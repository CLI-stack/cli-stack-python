"""
Project: Mock REST API Server
What it does: Creates a lightweight fake REST API server for testing.
When building a frontend or testing API calls, you often need a server
that returns predictable data. This lets you test without a real backend.

Install: pip install flask
Run: python 18_mock_api_server.py
Test with: curl http://localhost:5001/api/users
           curl http://localhost:5001/api/products
           curl -X POST http://localhost:5001/api/users -H "Content-Type: application/json" -d '{"name":"Alice"}'
"""

import argparse

try:
    from flask import Flask, jsonify, request
    import time
    import random

    app = Flask(__name__)

    # ── In-memory data store (our fake database) ──────────────────────────────
    # In a real API, this would come from a database like PostgreSQL or MongoDB
    USERS = [
        {"id": 1, "name": "Alice Johnson",  "email": "alice@example.com",  "role": "admin",  "active": True},
        {"id": 2, "name": "Bob Smith",      "email": "bob@example.com",    "role": "user",   "active": True},
        {"id": 3, "name": "Charlie Brown",  "email": "charlie@example.com","role": "user",   "active": False},
    ]

    PRODUCTS = [
        {"id": 1, "name": "Laptop",   "price": 1200, "category": "Electronics", "stock": 50},
        {"id": 2, "name": "Phone",    "price": 800,  "category": "Electronics", "stock": 120},
        {"id": 3, "name": "Desk",     "price": 350,  "category": "Furniture",   "stock": 20},
        {"id": 4, "name": "Keyboard", "price": 80,   "category": "Electronics", "stock": 200},
    ]

    next_user_id = 4  # auto-increment ID counter for new users


    # ── Middleware: simulate network delay ────────────────────────────────────
    @app.before_request
    def add_delay():
        """Add a small random delay to simulate real network conditions."""
        time.sleep(random.uniform(0.01, 0.05))  # 10-50ms delay


    # ── Root endpoint ─────────────────────────────────────────────────────────
    @app.route("/")
    def root():
        """API documentation at the root endpoint."""
        return jsonify({
            "name":    "Mock API Server",
            "version": "1.0",
            "endpoints": {
                "GET  /api/users":            "List all users",
                "GET  /api/users/<id>":       "Get user by ID",
                "POST /api/users":            "Create a new user",
                "GET  /api/products":         "List all products",
                "GET  /api/products/<id>":    "Get product by ID",
                "GET  /api/health":           "Server health check",
            }
        })


    # ── User endpoints ─────────────────────────────────────────────────────────

    @app.route("/api/users", methods=["GET"])
    def get_users():
        """
        GET /api/users
        Optional query param: ?active=true (filter by active status)
        """
        active_filter = request.args.get("active")  # ?active=true or ?active=false

        if active_filter is not None:
            # Filter users based on active status
            active_bool = active_filter.lower() == "true"
            filtered    = [u for u in USERS if u["active"] == active_bool]
        else:
            filtered = USERS

        return jsonify({
            "users": filtered,
            "count": len(filtered),
            "total": len(USERS)
        })


    @app.route("/api/users/<int:user_id>", methods=["GET"])
    def get_user(user_id):
        """GET /api/users/<id> — Get a single user by their ID."""
        user = next((u for u in USERS if u["id"] == user_id), None)

        if user is None:
            # Return 404 with an error message (not found)
            return jsonify({"error": f"User {user_id} not found"}), 404

        return jsonify(user)


    @app.route("/api/users", methods=["POST"])
    def create_user():
        """POST /api/users — Create a new user from the JSON request body."""
        global next_user_id

        body = request.get_json()  # parse JSON from request body

        if not body:
            return jsonify({"error": "Request body must be JSON"}), 400

        if "name" not in body:
            return jsonify({"error": "Field 'name' is required"}), 400

        # Build the new user object
        new_user = {
            "id":     next_user_id,
            "name":   body["name"],
            "email":  body.get("email", f"user{next_user_id}@example.com"),
            "role":   body.get("role", "user"),
            "active": body.get("active", True),
        }

        USERS.append(new_user)
        next_user_id += 1

        # Return 201 Created with the new user object
        return jsonify(new_user), 201


    # ── Product endpoints ──────────────────────────────────────────────────────

    @app.route("/api/products", methods=["GET"])
    def get_products():
        """GET /api/products — List products, optionally filtered by category."""
        category = request.args.get("category")  # ?category=Electronics

        if category:
            filtered = [p for p in PRODUCTS if p["category"].lower() == category.lower()]
        else:
            filtered = PRODUCTS

        return jsonify({"products": filtered, "count": len(filtered)})


    @app.route("/api/products/<int:product_id>", methods=["GET"])
    def get_product(product_id):
        """GET /api/products/<id>"""
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        if product is None:
            return jsonify({"error": f"Product {product_id} not found"}), 404
        return jsonify(product)


    # ── Health check endpoint ──────────────────────────────────────────────────

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint — monitoring systems poll this to see if the server is up."""
        return jsonify({
            "status":  "healthy",
            "uptime":  "running",
            "users":   len(USERS),
            "products":len(PRODUCTS),
        })


    # ── Main ─────────────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description="Run a mock REST API server")
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()

    print("=== Mock REST API Server ===\n")
    print(f"Starting on http://localhost:{args.port}")
    print("\nAvailable endpoints:")
    print(f"  GET  http://localhost:{args.port}/api/users")
    print(f"  GET  http://localhost:{args.port}/api/products")
    print(f"  GET  http://localhost:{args.port}/api/health")
    print("\nPress Ctrl+C to stop\n")

    app.run(port=args.port, debug=False)

except ImportError:
    print("Install: pip install flask")
