"""
Script: Requests Session and Authentication
What it does: Uses a Session to persist headers and cookies across requests.
Sessions are important when you need to stay logged in across multiple requests.

Install: pip install requests
"""

try:
    import requests

    # --- Session: reuse connection and headers ---
    print("=== Using a Session ===")

    # A Session object keeps settings (like headers) across all requests
    session = requests.Session()

    # Set headers once — they apply to all session requests
    session.headers.update({
        "User-Agent": "MyPythonApp/1.0",
        "Accept": "application/json",
    })

    # All requests now use these headers automatically
    r1 = session.get("https://httpbin.org/headers")
    print("Headers sent:")
    for key, value in r1.json()["headers"].items():
        print(f"  {key}: {value}")

    # --- Basic Authentication ---
    print("\n=== Basic Authentication ===")
    # Some APIs require username + password
    response = requests.get(
        "https://httpbin.org/basic-auth/alice/secret123",
        auth=("alice", "secret123")  # (username, password)
    )
    print(f"Auth response: {response.status_code}")
    if response.status_code == 200:
        print(f"Authenticated: {response.json()}")

    # --- Bearer Token Authentication (common for APIs) ---
    print("\n=== Bearer Token Auth ===")
    token = "my-secret-api-token-12345"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://httpbin.org/bearer", headers=headers)
    print(f"Token auth: {response.status_code}")
    if response.status_code == 200:
        print(response.json())

    # --- Cookies ---
    print("\n=== Working with Cookies ===")
    # Set a cookie
    response = requests.get("https://httpbin.org/cookies/set/session_id/abc123")
    # httpbin sets the cookie and redirects; requests follows redirects by default
    cookies = response.cookies
    print(f"Cookies: {dict(cookies)}")

    session.close()  # always close sessions when done

except ImportError:
    print("Install: pip install requests")
