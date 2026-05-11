"""
Script: HTTP POST Request
What it does: Sends data to a server using HTTP POST.
POST is used when submitting forms, creating records, or sending JSON data to APIs.

Install: pip install requests
"""

try:
    import requests
    import json

    # --- POST with form data (like submitting an HTML form) ---
    print("=== POST Form Data ===")
    form_data = {
        "username": "alice",
        "password": "secret123",
        "email": "alice@example.com"
    }
    response = requests.post("https://httpbin.org/post", data=form_data)
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Form data received: {result['form']}")

    # --- POST JSON data (most common for modern APIs) ---
    print("\n=== POST JSON Data ===")
    json_data = {
        "title": "Learn Python",
        "completed": False,
        "user_id": 1
    }
    response = requests.post(
        "https://httpbin.org/post",
        json=json_data  # automatically sets Content-Type: application/json
    )
    result = response.json()
    print(f"JSON sent: {result['json']}")

    # --- POST with custom headers ---
    print("\n=== POST with Headers ===")
    headers = {
        "Authorization": "Bearer my-secret-token",
        "Content-Type": "application/json",
        "X-Custom-Header": "MyApp/1.0"
    }
    response = requests.post(
        "https://httpbin.org/post",
        json={"action": "test"},
        headers=headers
    )
    result = response.json()
    print(f"Headers received: {list(result['headers'].keys())}")

    # --- POST to create a resource (JSONPlaceholder fake API) ---
    print("\n=== Create a TODO item ===")
    new_todo = {"title": "Buy groceries", "completed": False, "userId": 1}
    response = requests.post("https://jsonplaceholder.typicode.com/todos", json=new_todo)
    if response.status_code == 201:  # 201 = Created
        print(f"Created: {response.json()}")

except ImportError:
    print("Install: pip install requests")
