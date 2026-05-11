"""
Script: HTTP GET Requests
What it does: Makes HTTP GET requests to fetch data from web APIs.
GET is the most common HTTP method — it retrieves data without changing anything.

Install: pip install requests
"""

try:
    import requests
    import json

    # --- Basic GET request ---
    print("=== Basic GET Request ===")
    # JSONPlaceholder is a free fake API for testing
    url = "https://jsonplaceholder.typicode.com/posts/1"
    response = requests.get(url)

    print(f"Status code: {response.status_code}")  # 200 = success
    print(f"Content type: {response.headers['Content-Type']}")

    # Parse JSON response
    data = response.json()  # automatically converts JSON string to Python dict
    print(f"Post title: {data['title']}")
    print(f"Post body:  {data['body'][:60]}...")

    # --- GET with query parameters ---
    print("\n=== GET with Query Parameters ===")
    # Query params appear in the URL: ?userId=1
    params = {"userId": 1, "_limit": 3}  # limit to 3 results
    response = requests.get(
        "https://jsonplaceholder.typicode.com/posts",
        params=params  # requests automatically builds the query string
    )

    posts = response.json()
    print(f"Fetched {len(posts)} posts for userId=1:")
    for post in posts:
        print(f"  [{post['id']}] {post['title'][:50]}")

    # --- Check response details ---
    print("\n=== Response Details ===")
    print(f"Final URL: {response.url}")    # full URL with params
    print(f"Response time: {response.elapsed.total_seconds():.3f} seconds")
    print(f"Content length: {len(response.content)} bytes")

    # --- Error handling ---
    print("\n=== Error Handling ===")
    bad_response = requests.get("https://jsonplaceholder.typicode.com/posts/9999")
    print(f"Status for non-existent resource: {bad_response.status_code}")  # 404

    # Raise an exception for bad status codes
    try:
        bad_response.raise_for_status()
    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")

except ImportError:
    print("Install: pip install requests")
