"""
Script: Flask Hello World Web App
What it does: Creates the simplest possible web application.
When you run this and visit http://localhost:5000 in your browser,
you'll see "Hello, World!" on the page.

Install: pip install flask
Run: python 41_flask_hello.py
"""

from flask import Flask  # Flask is a lightweight web framework

# Create the Flask application
# __name__ tells Flask which module this is
app = Flask(__name__)

# --- Define a route ---
# A route maps a URL to a Python function
@app.route("/")  # "/" means the homepage (http://localhost:5000/)
def home():
    """This function runs when someone visits the homepage."""
    return "Hello, World! Welcome to my Flask app!"

@app.route("/about")  # http://localhost:5000/about
def about():
    return "This is a simple Flask web application."

@app.route("/greet/<name>")  # <name> is a variable in the URL
def greet(name):
    # Whatever the user puts in the URL becomes the 'name' variable
    return f"Hello, {name}! Nice to meet you."

# This runs the development server
if __name__ == "__main__":
    print("Starting Flask server...")
    print("Visit: http://localhost:5000")
    print("Press CTRL+C to stop")
    app.run(debug=True)  # debug=True auto-reloads when code changes
