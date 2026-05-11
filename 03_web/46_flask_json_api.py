"""
Script: Flask JSON REST API
What it does: Creates a complete REST API with Flask that supports
GET, POST, PUT, and DELETE operations (CRUD: Create, Read, Update, Delete).
This is how backend APIs for mobile apps and websites are built.

Install: pip install flask
Run: python 46_flask_json_api.py
Test with: curl http://localhost:5000/tasks
"""

try:
    from flask import Flask, jsonify, request

    app = Flask(__name__)

    # In-memory "database" (a list of dictionaries)
    tasks = [
        {"id": 1, "title": "Learn Python",    "done": True},
        {"id": 2, "title": "Build a Flask API", "done": False},
        {"id": 3, "title": "Deploy to cloud",  "done": False},
    ]
    next_id = 4  # counter for new task IDs

    # --- GET all tasks ---
    @app.route("/tasks", methods=["GET"])
    def get_tasks():
        """Return all tasks as JSON"""
        return jsonify({"tasks": tasks, "count": len(tasks)})

    # --- GET a single task by ID ---
    @app.route("/tasks/<int:task_id>", methods=["GET"])
    def get_task(task_id):
        """Return one task by its ID"""
        task = next((t for t in tasks if t["id"] == task_id), None)
        if task is None:
            return jsonify({"error": "Task not found"}), 404  # 404 = Not Found
        return jsonify(task)

    # --- POST: create a new task ---
    @app.route("/tasks", methods=["POST"])
    def create_task():
        """Create a new task from JSON body"""
        global next_id
        body = request.get_json()  # parse the JSON body
        if not body or "title" not in body:
            return jsonify({"error": "title is required"}), 400  # 400 = Bad Request
        new_task = {"id": next_id, "title": body["title"], "done": False}
        tasks.append(new_task)
        next_id += 1
        return jsonify(new_task), 201  # 201 = Created

    # --- PUT: update a task ---
    @app.route("/tasks/<int:task_id>", methods=["PUT"])
    def update_task(task_id):
        """Mark a task as done or update its title"""
        task = next((t for t in tasks if t["id"] == task_id), None)
        if task is None:
            return jsonify({"error": "Task not found"}), 404
        body = request.get_json()
        task.update({k: v for k, v in body.items() if k in ["title", "done"]})
        return jsonify(task)

    # --- DELETE: remove a task ---
    @app.route("/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        global tasks
        original_count = len(tasks)
        tasks = [t for t in tasks if t["id"] != task_id]
        if len(tasks) == original_count:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"message": f"Task {task_id} deleted"}), 200

    if __name__ == "__main__":
        print("Flask API running at http://localhost:5000")
        print("Endpoints: GET/POST /tasks, GET/PUT/DELETE /tasks/<id>")
        app.run(debug=True)

except ImportError:
    print("Install: pip install flask")
