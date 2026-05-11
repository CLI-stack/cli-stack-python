"""
Script: HTTP Session Handling and Authentication
What it does: Shows how to use sessions, cookies, and authentication headers.
Sessions let you make multiple requests while maintaining login state.

Install: pip install requests
"""

try:
    import requests

    # --- Using a Session (reuses connection, shares cookies/headers) ---
    print("=== Using a Requests Session ===")

    # Without session: each request is independent
    # With session: headers, cookies, and auth are shared across all requests

    session = requests.Session()

    # Set default headers for all requests in this session
    session.headers.update({
        "User-Agent": "MyPythonApp/1.0",
        "Accept": "application/json",
    })

    # All requests through this session use the headers above
    response = session.get("https://httpbin.org/headers")
    if response.status_code == 200:
        headers_sent = response.json()["headers"]
        print("Headers sent to server:")
        for key, value in headers_sent.items():
            print(f"  {key}: {value}")

    # --- Basic Authentication ---
    print("\n=== Basic Authentication ===")
    # Some APIs require a username and password
    auth_response = requests.get(
        "https://httpbin.org/basic-auth/user/pass",
        auth=("user", "pass")  # (username, password)
    )
    print(f"Auth status: {auth_response.status_code}")
    if auth_response.status_code == 200:
        print(f"Authenticated: {auth_response.json()['authenticated']}")

    # --- Bearer Token Authentication ---
    print("\n=== Bearer Token Authentication ===")
    token = "my-secret-api-token"
    headers = {"Authorization": f"Bearer {token}"}
    token_response = requests.get("https://httpbin.org/bearer", headers=headers)
    print(f"Token auth status: {token_response.status_code}")
    if token_response.status_code == 200:
        print(f"Authenticated: {token_response.json()['authenticated']}")

    # --- Cookies ---
    print("\n=== Cookies ===")
    # Set a cookie and send it
    cookies = {"session_id": "abc123", "user_pref": "dark_mode"}
    cookie_response = requests.get("https://httpbin.org/cookies", cookies=cookies)
    if cookie_response.status_code == 200:
        print(f"Cookies sent: {cookie_response.json()['cookies']}")

    session.close()  # close the session when done

except ImportError:
    print("Install: pip install requests")
except Exception as e:
    print(f"Error: {e}")
