"""
Script: Rate Limiter for API Requests
What it does: Limits how many API requests are made per second to avoid
getting blocked or exceeding API quotas. Essential for scraping and API usage.

Install: pip install requests
"""

import time
import requests
from datetime import datetime

class RateLimitedRequester:
    """Makes HTTP requests but limits the rate to avoid being blocked."""

    def __init__(self, requests_per_second=1.0):
        # How long to wait between requests (in seconds)
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0  # timestamp of last request

    def get(self, url, **kwargs):
        """Make a GET request, waiting if necessary to respect the rate limit."""
        # Calculate how long to wait
        elapsed = time.time() - self.last_request_time
        wait_time = self.min_interval - elapsed

        if wait_time > 0:
            print(f"  (waiting {wait_time:.2f}s to respect rate limit)")
            time.sleep(wait_time)

        # Make the request
        self.last_request_time = time.time()
        return requests.get(url, **kwargs)

# --- Demo: Fetch multiple posts with rate limiting ---
requester = RateLimitedRequester(requests_per_second=2)  # max 2 per second

post_ids = [1, 2, 3, 4, 5]

print(f"Fetching {len(post_ids)} posts with rate limit (2/second)...\n")

results = []
for post_id in post_ids:
    start = datetime.now()
    response = requester.get(f"https://jsonplaceholder.typicode.com/posts/{post_id}")
    elapsed = (datetime.now() - start).total_seconds()

    post = response.json()
    results.append(post)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Post {post_id}: "
          f"'{post['title'][:40]}' ({elapsed:.3f}s)")

print(f"\nFetched {len(results)} posts successfully.")
print("Rate limiting prevents API bans and is respectful to servers.")
