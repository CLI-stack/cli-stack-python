"""
Script: Flask with HTML Templates
What it does: Serves HTML pages using Jinja2 templates.
Templates let you separate your HTML from your Python logic.
Flask automatically looks for templates in a "templates/" folder.

Install: pip install flask
Run: python 52_flask_template.py
Visit: http://localhost:5000
"""

try:
    from flask import Flask, render_template_string  # render_template_string for inline templates
    import datetime

    app = Flask(__name__)

    # --- HTML template as a string (normally saved in templates/index.html) ---
    # Jinja2 syntax: {{ variable }}, {% for %}, {% if %}
    HOME_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; }
            .card { background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .highlight { color: #007bff; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>
        <p>Hello, <span class="highlight">{{ username }}</span>!</p>
        <p>Today is: {{ current_date }}</p>

        <h2>Your Skills</h2>
        {% for skill in skills %}
            <div class="card">
                {{ loop.index }}. {{ skill }}
            </div>
        {% endfor %}

        {% if is_admin %}
            <p><strong>You have admin access.</strong></p>
        {% else %}
            <p>You are a regular user.</p>
        {% endif %}
    </body>
    </html>
    """

    @app.route("/")
    def home():
        # Pass variables to the template
        return render_template_string(HOME_TEMPLATE,
            title="My Flask App",
            username="Alice",
            current_date=datetime.date.today(),
            skills=["Python", "HTML", "CSS", "Flask"],
            is_admin=True
        )

    @app.route("/user/<name>")
    def user_page(name):
        return render_template_string(
            "<h1>Profile: {{ name }}</h1><p>Welcome back!</p>",
            name=name
        )

    if __name__ == "__main__":
        print("Visit: http://localhost:5000")
        app.run(debug=True)

except ImportError:
    print("Install: pip install flask")
