"""
Script: File Upload via HTTP API
What it does: Uploads a file to a web server using Python.
File uploads use multipart/form-data encoding.

Install: pip install requests flask
"""

import os

# --- Part 1: Flask server that accepts file uploads ---
# (Uncomment and run separately to test the upload)

server_code = '''
from flask import Flask, request, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    size = os.path.getsize(filepath)
    return jsonify({
        "message": "File uploaded successfully",
        "filename": file.filename,
        "size": size
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
'''

print("=== Server Code ===")
print("(Save this as a separate file and run it first)")
print(server_code)

# --- Part 2: Client that uploads a file ---
print("\n=== Client Upload Code ===")

upload_code = '''
import requests
import os

# Create a test file to upload
with open("test_upload.txt", "w") as f:
    f.write("This is a test file for upload!\\nLine 2\\nLine 3")

# Upload the file
with open("test_upload.txt", "rb") as f:  # "rb" = read binary
    files = {"file": ("test_upload.txt", f, "text/plain")}
    response = requests.post("http://localhost:5001/upload", files=files)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Clean up
os.remove("test_upload.txt")
'''

print(upload_code)

# --- Demonstrate uploading to httpbin (echo service) ---
try:
    import requests

    print("=== Demo: Upload to httpbin.org ===")
    content = b"Hello from Python file upload!"
    files = {"file": ("hello.txt", content, "text/plain")}

    response = requests.post("https://httpbin.org/post", files=files)
    if response.status_code == 200:
        data = response.json()
        print(f"Upload successful!")
        print(f"Files received: {list(data.get('files', {}).keys())}")

except ImportError:
    print("Install: pip install requests flask")
