"""
Script: API Client Class
What it does: Wraps API calls in a reusable class.
Instead of writing requests.get() everywhere, you create a clean interface.
This is how production code handles API integrations.

Install: pip install requests
"""

try:
    import requests

    class JSONPlaceholderClient:
        """A client for the JSONPlaceholder API."""

        BASE_URL = "https://jsonplaceholder.typicode.com"

        def __init__(self, timeout=10):
            # Create a session to reuse the connection (more efficient)
            self.session = requests.Session()
            self.timeout = timeout

            # Set default headers for all requests
            self.session.headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json"
            })

        def _get(self, endpoint, params=None):
            """Internal helper for GET requests."""
            url = f"{self.BASE_URL}{endpoint}"
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()  # raises error if status >= 400
            return response.json()

        def _post(self, endpoint, data):
            """Internal helper for POST requests."""
            url = f"{self.BASE_URL}{endpoint}"
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        # --- Public methods ---
        def get_posts(self, user_id=None, limit=None):
            params = {}
            if user_id:
                params["userId"] = user_id
            if limit:
                params["_limit"] = limit
            return self._get("/posts", params=params)

        def get_post(self, post_id):
            return self._get(f"/posts/{post_id}")

        def get_user(self, user_id):
            return self._get(f"/users/{user_id}")

        def create_post(self, title, body, user_id):
            return self._post("/posts", {"title": title, "body": body, "userId": user_id})

    # --- Use the client ---
    client = JSONPlaceholderClient()

    print("=== Get a single post ===")
    post = client.get_post(1)
    print(f"Title: {post['title']}")

    print("\n=== Get posts for user 1 (limit 3) ===")
    posts = client.get_posts(user_id=1, limit=3)
    for p in posts:
        print(f"  [{p['id']}] {p['title'][:50]}")

    print("\n=== Create a post ===")
    new_post = client.create_post("Test Title", "Test body", user_id=1)
    print(f"Created post with ID: {new_post['id']}")

except ImportError:
    print("Install: pip install requests")
