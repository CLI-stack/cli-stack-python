"""
Script: Simple Flask Web App
What it does: Creates a basic web server with Flask.
When you run this script, you can visit http://localhost:5000 in your browser
and see "Hello, World!" displayed as a webpage.

Install: pip install flask
Run: python 45_flask_hello.py
Then open: http://localhost:5000
"""

try:
    from flask import Flask  # Flask is the main class

    # Create a Flask application
    app = Flask(__name__)
    # __name__ tells Flask the name of the current module

    # --- Define a route ---
    # A route maps a URL to a Python function
    @app.route("/")             # "/" means the root/home URL
    def home():
        """This function runs when someone visits http://localhost:5000/"""
        return "<h1>Hello, World!</h1><p>Welcome to my Flask app!</p>"

    @app.route("/about")        # maps to http://localhost:5000/about
    def about():
        return "<h1>About Page</h1><p>This is a beginner Flask example.</p>"

    @app.route("/greet/<name>") # <name> is a dynamic URL variable
    def greet(name):
        """This lets us do: http://localhost:5000/greet/Alice"""
        return f"<h1>Hello, {name}!</h1>"

    # Run the app only if this file is executed directly
    if __name__ == "__main__":
        print("Starting Flask server...")
        print("Visit: http://localhost:5000")
        print("Press Ctrl+C to stop")
        app.run(debug=True)
        # debug=True: auto-restarts server when code changes

except ImportError:
    print("Install: pip install flask")
    print("Then run: python 45_flask_hello.py")
