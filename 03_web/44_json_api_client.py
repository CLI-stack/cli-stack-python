"""
Script: JSON API Client
What it does: Fetches and displays data from a public REST API.
Shows how to work with real-world API responses (pagination, nested data).

Install: pip install requests
"""

try:
    import requests

    BASE_URL = "https://jsonplaceholder.typicode.com"
    # JSONPlaceholder is a free fake API for testing and prototyping

    # --- Fetch a list of users ---
    print("=== Fetching Users ===")
    response = requests.get(f"{BASE_URL}/users")
    users = response.json()  # list of user dictionaries

    for user in users[:5]:  # show first 5
        print(f"  ID: {user['id']} | {user['name']} | {user['email']} | {user['address']['city']}")

    # --- Fetch posts by a specific user ---
    user_id = 1
    print(f"\n=== Posts by User {user_id} ===")
    response = requests.get(f"{BASE_URL}/posts", params={"userId": user_id})
    posts = response.json()

    for post in posts[:3]:
        print(f"  [{post['id']}] {post['title'][:50]}")

    # --- Fetch a single post and its comments ---
    post_id = 1
    print(f"\n=== Post {post_id} ===")
    post = requests.get(f"{BASE_URL}/posts/{post_id}").json()
    print(f"Title: {post['title']}")
    print(f"Body:  {post['body'][:100]}...")

    print(f"\n=== Comments on Post {post_id} ===")
    comments = requests.get(f"{BASE_URL}/comments", params={"postId": post_id}).json()
    for comment in comments[:3]:
        print(f"  From: {comment['email']}")
        print(f"  {comment['body'][:80]}...\n")

    # --- Create a simple API wrapper class ---
    class JSONPlaceholderClient:
        def __init__(self):
            self.base = "https://jsonplaceholder.typicode.com"

        def get_user(self, user_id):
            return requests.get(f"{self.base}/users/{user_id}").json()

        def get_todos(self, user_id):
            return requests.get(f"{self.base}/todos", params={"userId": user_id}).json()

    client = JSONPlaceholderClient()
    user = client.get_user(2)
    todos = client.get_todos(2)
    completed = sum(1 for t in todos if t["completed"])
    print(f"=== {user['name']}'s Progress ===")
    print(f"  Completed {completed}/{len(todos)} todos")

except ImportError:
    print("Install: pip install requests")
