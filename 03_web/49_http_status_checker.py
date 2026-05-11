"""
Script: HTTP Status Checker
What it does: Checks whether websites are online and what their status is.
Useful for monitoring websites or checking if a list of URLs is reachable.

Install: pip install requests
"""

try:
    import requests
    from datetime import datetime

    # HTTP status code descriptions
    STATUS_DESCRIPTIONS = {
        200: "OK - Site is up!",
        201: "Created",
        301: "Moved Permanently (redirect)",
        302: "Found (temporary redirect)",
        400: "Bad Request",
        401: "Unauthorized (login required)",
        403: "Forbidden (access denied)",
        404: "Not Found",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable (site is down)",
    }

    def check_url(url, timeout=5):
        """Check if a URL is reachable and return status info."""
        try:
            start = datetime.now()
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            # allow_redirects=True follows redirects automatically
            elapsed = (datetime.now() - start).total_seconds()

            status = response.status_code
            description = STATUS_DESCRIPTIONS.get(status, "Unknown status")

            return {
                "url": url,
                "status": status,
                "description": description,
                "response_time": f"{elapsed:.3f}s",
                "online": status < 400
            }

        except requests.ConnectionError:
            return {"url": url, "status": "ERROR", "description": "Cannot connect", "online": False}
        except requests.Timeout:
            return {"url": url, "status": "TIMEOUT", "description": "Request timed out", "online": False}

    # --- Check multiple URLs ---
    urls_to_check = [
        "https://www.google.com",
        "https://www.python.org",
        "https://jsonplaceholder.typicode.com",
        "https://httpstat.us/404",   # returns 404 intentionally
        "https://httpstat.us/500",   # returns 500 intentionally
    ]

    print(f"Checking {len(urls_to_check)} URLs...\n")
    print(f"{'URL':<45} {'Status':<8} {'Time':<10} {'Description'}")
    print("-" * 90)

    for url in urls_to_check:
        result = check_url(url)
        icon = "✓" if result["online"] else "✗"
        print(f"{icon} {result['url']:<43} {str(result['status']):<8} "
              f"{result.get('response_time', 'N/A'):<10} {result['description']}")

except ImportError:
    print("Install: pip install requests")
