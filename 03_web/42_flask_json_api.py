"""
Script: Flask JSON API
What it does: Creates a REST API that returns JSON data.
APIs like this are used by mobile apps and frontends to get data.

Install: pip install flask
Run: python 42_flask_json_api.py
Test: curl http://localhost:5000/api/users
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample in-memory database (list of dictionaries)
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
    {"id": 2, "name": "Bob",   "email": "bob@example.com",   "age": 25},
    {"id": 3, "name": "Charlie","email":"charlie@example.com","age": 35},
]

# --- GET all users ---
@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify({"users": users, "total": len(users)})

# --- GET a single user by ID ---
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    # Find user with matching ID
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404  # 404 = Not Found

# --- POST: create a new user ---
@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()  # parse JSON from request body
    new_user = {
        "id": len(users) + 1,
        "name": data.get("name"),
        "email": data.get("email"),
        "age": data.get("age")
    }
    users.append(new_user)
    return jsonify(new_user), 201  # 201 = Created

# --- DELETE a user ---
@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    global users
    users = [u for u in users if u["id"] != user_id]
    return jsonify({"message": f"User {user_id} deleted"})

if __name__ == "__main__":
    print("API running at http://localhost:5000/api/users")
    app.run(debug=True)
