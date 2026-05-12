"""
Script: API Client Class
What it does: Wraps API calls in a reusable class.
Instead of writing requests.get() everywhere, you create a clean interface.
This is how production code handles API integrations — all the URL building,
headers, and error handling live in one place, and callers just use simple methods.

Install: pip install requests
"""

try:
    import requests

    class JSONPlaceholderClient:
        """
        A client for the JSONPlaceholder API (https://jsonplaceholder.typicode.com).
        This class shows the 'wrapper' pattern: hide the complexity of HTTP
        requests inside methods, so the rest of your code stays simple.
        """

        # BASE_URL is a class variable — shared by all instances of this class
        BASE_URL = "https://jsonplaceholder.typicode.com"

        def __init__(self, timeout=10):
            # Session reuses the same TCP connection for multiple requests.
            # This is faster than opening a new connection for every request.
            self.session = requests.Session()

            # Store the timeout so every request uses the same limit
            self.timeout = timeout

            # Set headers once here — they are automatically sent with EVERY
            # request made through this session, so we don't repeat them.
            self.session.headers.update({
                "Content-Type": "application/json",  # we send JSON
                "Accept": "application/json"          # we expect JSON back
            })

        def _get(self, endpoint, params=None):
            """
            Internal helper for GET requests.
            The leading underscore (_) means 'private' — not meant to be called
            directly from outside the class. Use the public methods below instead.
            """
            # Build the full URL by joining the base URL with the endpoint path
            url = f"{self.BASE_URL}{endpoint}"

            response = self.session.get(url, params=params, timeout=self.timeout)

            # raise_for_status() automatically raises an exception if the server
            # returns an error code (4xx = client error, 5xx = server error).
            # Without this, a 404 or 500 would silently return a bad response.
            response.raise_for_status()

            # .json() parses the JSON response body into a Python dict/list
            return response.json()

        def _post(self, endpoint, data):
            """Internal helper for POST requests (sending data to create something)."""
            url = f"{self.BASE_URL}{endpoint}"
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()  # raise error if status code >= 400
            return response.json()

        # ── Public methods (these are the API your callers use) ───────────────

        def get_posts(self, user_id=None, limit=None):
            """Fetch a list of posts, optionally filtered by user_id and limited in count."""
            params = {}  # start with empty query parameters

            if user_id:
                params["userId"] = user_id   # add ?userId=X to the URL

            if limit:
                params["_limit"] = limit     # add ?_limit=N to the URL

            return self._get("/posts", params=params)

        def get_post(self, post_id):
            """Fetch a single post by its numeric ID."""
            return self._get(f"/posts/{post_id}")  # e.g. /posts/1

        def get_user(self, user_id):
            """Fetch a user's profile by their ID."""
            return self._get(f"/users/{user_id}")

        def create_post(self, title, body, user_id):
            """
            Create a new post by sending a POST request.
            Returns the created post with its new ID assigned by the server.
            """
            return self._post("/posts", {"title": title, "body": body, "userId": user_id})

    # ── Using the client ──────────────────────────────────────────────────────

    # Create one client instance — reuse it for all requests
    client = JSONPlaceholderClient()

    print("=== Get a single post ===")
    post = client.get_post(1)         # fetches /posts/1
    print(f"Title: {post['title']}")

    print("\n=== Get posts for user 1 (limit 3) ===")
    posts = client.get_posts(user_id=1, limit=3)  # fetches /posts?userId=1&_limit=3
    for p in posts:
        print(f"  [{p['id']}] {p['title'][:50]}")

    print("\n=== Create a post ===")
    new_post = client.create_post("Test Title", "Test body", user_id=1)
    print(f"Created post with ID: {new_post['id']}")
    # Note: JSONPlaceholder doesn't actually save it — it just pretends to

except ImportError:
    print("Install: pip install requests")
