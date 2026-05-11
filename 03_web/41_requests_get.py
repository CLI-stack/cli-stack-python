"""
Script: HTTP GET Request
What it does: Fetches data from a web URL using HTTP GET.
This is how Python talks to websites and APIs on the internet.

Install: pip install requests
"""

try:
    import requests  # popular HTTP library

    # --- Basic GET request ---
    print("=== Basic GET Request ===")
    response = requests.get("https://httpbin.org/get")
    # httpbin.org is a public testing service for HTTP requests

    print(f"Status code: {response.status_code}")  # 200 = OK
    print(f"Content type: {response.headers['Content-Type']}")

    # --- Parse JSON response ---
    data = response.json()  # automatically parses JSON into a Python dict
    print(f"Your IP address: {data.get('origin')}")
    print(f"URL called: {data.get('url')}")

    # --- Send query parameters ---
    # This is like: https://httpbin.org/get?name=Alice&age=30
    print("\n=== GET with Parameters ===")
    params = {"name": "Alice", "age": 30, "city": "NYC"}
    response = requests.get("https://httpbin.org/get", params=params)
    data = response.json()
    print(f"Args sent: {data.get('args')}")

    # --- Fetch a simple API ---
    print("\n=== Fetch Public API ===")
    response = requests.get("https://catfact.ninja/fact")  # random cat fact API
    if response.status_code == 200:
        fact = response.json()
        print(f"Cat fact: {fact['fact']}")

    # --- Handle errors gracefully ---
    print("\n=== Error Handling ===")
    response = requests.get("https://httpbin.org/status/404")  # 404 = Not Found
    if response.status_code == 200:
        print("Success!")
    elif response.status_code == 404:
        print("Error 404: Page not found")
    elif response.status_code == 500:
        print("Error 500: Server error")
    else:
        print(f"Unexpected status: {response.status_code}")

    # --- Set timeout (don't wait forever) ---
    try:
        response = requests.get("https://httpbin.org/delay/1", timeout=5)
        print(f"\nRequest with timeout succeeded: {response.status_code}")
    except requests.exceptions.Timeout:
        print("Request timed out!")

except ImportError:
    print("Install: pip install requests")
