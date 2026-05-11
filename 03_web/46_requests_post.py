"""
Script: HTTP POST, PUT, DELETE Requests
What it does: Sends data to an API using POST (create), PUT (update), DELETE (remove).
These are the requests that change data on a server.

Install: pip install requests
"""

try:
    import requests
    import json

    BASE_URL = "https://jsonplaceholder.typicode.com"

    # --- POST: Create new data ---
    print("=== POST Request (Create) ===")
    new_post = {
        "title": "My First Post",
        "body": "This is the post content. Python makes APIs easy!",
        "userId": 1
    }

    response = requests.post(
        f"{BASE_URL}/posts",
        json=new_post  # 'json=' automatically sets Content-Type: application/json
    )

    print(f"Status code: {response.status_code}")  # 201 = Created
    created = response.json()
    print(f"Created post ID: {created['id']}")
    print(f"Title: {created['title']}")

    # --- PUT: Update existing data ---
    print("\n=== PUT Request (Update) ===")
    updated_post = {
        "id": 1,
        "title": "Updated Title",
        "body": "Updated body text.",
        "userId": 1
    }

    response = requests.put(
        f"{BASE_URL}/posts/1",  # ID 1 in the URL
        json=updated_post
    )
    print(f"Status: {response.status_code}")
    print(f"Updated title: {response.json()['title']}")

    # --- PATCH: Partial update (only send what changed) ---
    print("\n=== PATCH Request (Partial Update) ===")
    response = requests.patch(
        f"{BASE_URL}/posts/1",
        json={"title": "Only title changed"}  # only update the title
    )
    print(f"Status: {response.status_code}")
    print(f"New title: {response.json()['title']}")

    # --- DELETE: Remove data ---
    print("\n=== DELETE Request ===")
    response = requests.delete(f"{BASE_URL}/posts/1")
    print(f"Status: {response.status_code}")  # 200 = OK
    print("Post deleted successfully")

    # --- POST with headers ---
    print("\n=== POST with Custom Headers ===")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer fake-token-123",  # typical auth header
    }
    response = requests.post(
        f"{BASE_URL}/posts",
        json={"title": "Auth test"},
        headers=headers
    )
    print(f"Status with auth header: {response.status_code}")

except ImportError:
    print("Install: pip install requests")
