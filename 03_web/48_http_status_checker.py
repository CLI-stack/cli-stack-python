"""
Script: HTTP Status Checker
What it does: Checks whether a list of websites are up or down.
Useful for monitoring websites and detecting downtime.

Install: pip install requests
"""

try:
    import requests
    import time

    # List of websites to check
    websites = [
        "https://www.google.com",
        "https://www.github.com",
        "https://www.python.org",
        "https://httpbin.org",
        "https://www.nonexistent-fake-site-xyz.com",  # this should fail
    ]

    def check_website(url, timeout=5):
        """
        Check if a website is reachable.
        Returns (status_code, response_time, is_up)
        """
        try:
            start = time.time()
            response = requests.get(url, timeout=timeout)
            elapsed = time.time() - start  # response time in seconds

            is_up = response.status_code < 400  # < 400 means success
            return response.status_code, elapsed, is_up

        except requests.exceptions.ConnectionError:
            return None, None, False  # can't connect
        except requests.exceptions.Timeout:
            return None, None, False  # took too long

    # --- Check all websites ---
    print(f"{'Website':<40} {'Status':<8} {'Time':<10} {'Result'}")
    print("-" * 70)

    results = []
    for url in websites:
        status_code, response_time, is_up = check_website(url)

        if is_up:
            status_str = str(status_code)
            time_str = f"{response_time:.2f}s"
            result_str = "UP"
        else:
            status_str = str(status_code) if status_code else "N/A"
            time_str = "N/A"
            result_str = "DOWN"

        domain = url.replace("https://", "").replace("http://", "")
        print(f"{domain:<40} {status_str:<8} {time_str:<10} {result_str}")
        results.append(is_up)

    # --- Summary ---
    up_count = sum(results)
    print(f"\nSummary: {up_count}/{len(websites)} sites are UP")

except ImportError:
    print("Install: pip install requests")
