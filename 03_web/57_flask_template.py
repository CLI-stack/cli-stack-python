"""
Script: Flask with HTML Templates
What it does: Shows how to render HTML pages using Jinja2 templates.
Templates let you build dynamic HTML pages where data changes each request.

Install: pip install flask
Run: python 57_flask_template.py
Visit: http://localhost:5000
"""

from flask import Flask, render_template_string

app = Flask(__name__)

# In real projects, templates go in a 'templates/' folder as .html files
# Here we embed them as strings for simplicity

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ page_title }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
        .badge { padding: 3px 8px; border-radius: 3px; font-size: 12px; }
        .active { background: #d4edda; color: #155724; }
        .inactive { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>{{ heading }}</h1>
    <p>Total users: <strong>{{ users|length }}</strong></p>

    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Role</th>
            <th>Status</th>
        </tr>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.role }}</td>
            <td>
                <span class="badge {{ 'active' if user.active else 'inactive' }}">
                    {{ 'Active' if user.active else 'Inactive' }}
                </span>
            </td>
        </tr>
        {% endfor %}
    </table>

    {% if show_footer %}
    <hr>
    <p><small>Generated at: {{ generated_at }}</small></p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def user_list():
    from datetime import datetime
    users = [
        {"id": 1, "name": "Alice",   "role": "Admin",     "active": True},
        {"id": 2, "name": "Bob",     "role": "Developer", "active": True},
        {"id": 3, "name": "Charlie", "role": "Designer",  "active": False},
        {"id": 4, "name": "Diana",   "role": "Manager",   "active": True},
    ]
    return render_template_string(
        BASE_TEMPLATE,
        page_title="User Dashboard",
        heading="User List",
        users=users,
        show_footer=True,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

if __name__ == "__main__":
    print("Running at http://localhost:5000")
    app.run(debug=True)
