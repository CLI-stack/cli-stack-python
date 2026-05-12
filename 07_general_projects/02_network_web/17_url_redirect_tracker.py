"""
Project: URL Redirect Tracker
What it does: Follows a URL through all its redirects and shows each hop.
Many URLs redirect: short URLs (bit.ly), HTTP → HTTPS upgrades, www. rewrites.
Understanding redirect chains is important for SEO, debugging, and security.

Example chain: http://bit.ly/abc → https://bit.ly/abc → https://example.com/page

Install: pip install requests
Run: python 17_url_redirect_tracker.py
Run: python 17_url_redirect_tracker.py --url http://github.com
"""

import argparse
import time

try:
    import requests

    # HTTP status codes that indicate a redirect
    REDIRECT_CODES = {
        301: "Moved Permanently",      # permanent redirect (SEO-friendly)
        302: "Found (Temporary)",      # temporary redirect
        303: "See Other",              # POST → GET redirect
        307: "Temporary Redirect",     # like 302 but preserves HTTP method
        308: "Permanent Redirect",     # like 301 but preserves HTTP method
    }

    def trace_redirects(start_url):
        """
        Follow a URL step by step through all redirects.
        Returns a list of each hop with URL, status code, and timing.

        We use allow_redirects=False so we can see each individual redirect
        instead of following them all automatically.
        """
        hops    = []
        current = start_url
        visited = set()   # track visited URLs to detect redirect loops
        headers = {"User-Agent": "Mozilla/5.0 RedirectTracer/1.0"}

        print(f"Tracing: {start_url}\n")

        for step in range(20):  # limit to 20 redirects to prevent infinite loops
            if current in visited:
                hops.append({
                    "step":   step + 1,
                    "url":    current,
                    "status": "LOOP",
                    "desc":   "Redirect loop detected!",
                    "time_ms":0,
                })
                break

            visited.add(current)

            try:
                start_time = time.time()

                # allow_redirects=False: stop at this redirect, don't follow it
                response = requests.get(current, headers=headers,
                                        allow_redirects=False, timeout=10)

                elapsed_ms = (time.time() - start_time) * 1000

                status  = response.status_code
                desc    = REDIRECT_CODES.get(status, f"HTTP {status}")

                # Check if response has a Location header (where to redirect to)
                next_url = response.headers.get("Location", "")

                hop = {
                    "step":    step + 1,
                    "url":     current,
                    "status":  status,
                    "desc":    desc,
                    "time_ms": elapsed_ms,
                    "next":    next_url,
                    "server":  response.headers.get("Server", ""),
                }
                hops.append(hop)

                # If it's a redirect status, follow to the next URL
                if status in REDIRECT_CODES and next_url:
                    # Handle relative redirect URLs
                    if next_url.startswith("/"):
                        from urllib.parse import urlparse
                        parsed  = urlparse(current)
                        current = f"{parsed.scheme}://{parsed.netloc}{next_url}"
                    else:
                        current = next_url
                else:
                    # Not a redirect — we've reached the final destination
                    break

            except requests.exceptions.SSLError as e:
                hops.append({"step": step+1, "url": current, "status": "SSL_ERROR",
                             "desc": str(e)[:60], "time_ms": 0})
                break
            except Exception as e:
                hops.append({"step": step+1, "url": current, "status": "ERROR",
                             "desc": str(e)[:60], "time_ms": 0})
                break

        return hops


    def print_redirect_chain(hops):
        """Display the redirect chain in a readable format."""
        GREEN = "\033[92m"
        RED   = "\033[91m"
        YEL   = "\033[33m"
        RST   = "\033[0m"

        redirect_count = sum(1 for h in hops if h["status"] in REDIRECT_CODES)

        print(f"{'='*70}")
        print(f"  REDIRECT CHAIN ANALYSIS")
        print(f"{'='*70}")
        print(f"  Total hops:      {len(hops)}")
        print(f"  Redirects:       {redirect_count}")
        print(f"  Total time:      {sum(h.get('time_ms',0) for h in hops):.0f} ms\n")

        for hop in hops:
            step   = hop["step"]
            url    = hop["url"]
            status = hop["status"]
            desc   = hop["desc"]
            ms     = hop.get("time_ms", 0)

            # Color-code based on status
            if str(status).startswith("2"):       color = GREEN
            elif str(status).startswith("3"):     color = YEL
            elif status in ("ERROR", "SSL_ERROR","LOOP"): color = RED
            else:                                  color = RED

            print(f"  Hop {step}: {color}{status}{RST}  {desc}")
            print(f"    URL  : {url[:80]}")
            if ms:
                print(f"    Time : {ms:.0f} ms")
            if hop.get("server"):
                print(f"    Server: {hop['server']}")
            if hop.get("next"):
                print(f"    → Next: {hop['next'][:80]}")
            print()

        # Final verdict
        last = hops[-1]
        if str(last.get("status", "")).startswith("2"):
            print(f"  {GREEN}Final destination reached successfully.{RST}")
        else:
            print(f"  {RED}Did not reach a successful (2xx) destination.{RST}")


    # ── Main ─────────────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description="Trace URL redirects step by step")
    parser.add_argument("--url", default="http://github.com",
                        help="Starting URL to trace")
    args = parser.parse_args()

    print("=== URL Redirect Tracker ===\n")
    hops = trace_redirects(args.url)
    print_redirect_chain(hops)

except ImportError:
    print("Install: pip install requests")
