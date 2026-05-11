"""
Script: Flask Form Handling
What it does: Creates a web form that accepts user input and processes it.
Forms are how users submit data to a website (login, signup, search, etc.)

Install: pip install flask
Run: python 53_flask_form.py
Visit: http://localhost:5000
"""

from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML template embedded as a string (in real apps, use separate .html files)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Contact Form</title></head>
<body>
    <h1>Contact Us</h1>
    {% if message %}
        <p style="color: green; font-weight: bold;">{{ message }}</p>
    {% endif %}
    <form method="POST" action="/submit">
        <label>Name: <input type="text" name="name" required></label><br><br>
        <label>Email: <input type="email" name="email" required></label><br><br>
        <label>Message:<br>
            <textarea name="message" rows="4" cols="40" required></textarea>
        </label><br><br>
        <button type="submit">Send</button>
    </form>
</body>
</html>
"""

THANK_YOU = """
<!DOCTYPE html>
<html>
<body>
    <h1>Thank You, {{ name }}!</h1>
    <p>We received your message:</p>
    <blockquote>{{ message }}</blockquote>
    <p>We'll reply to {{ email }} soon.</p>
    <a href="/">← Submit another message</a>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def show_form():
    return render_template_string(HTML_TEMPLATE, message=None)

@app.route("/submit", methods=["POST"])
def handle_form():
    # request.form contains all submitted form data
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    # In a real app: validate input, save to database, send email, etc.
    print(f"New submission: {name} ({email}) — {message[:50]}")

    return render_template_string(THANK_YOU, name=name, email=email, message=message)

if __name__ == "__main__":
    print("Form app running at http://localhost:5000")
    app.run(debug=True)
