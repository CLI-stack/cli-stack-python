"""
Project: HTTP Header Inspector
What it does: Sends HTTP requests to websites and displays all the response
headers. Headers contain important metadata about the server, caching,
security settings, and content type.

Common headers explained:
  Content-Type    : what type of data is returned (HTML, JSON, image)
  Server          : what web server software is running (nginx, Apache)
  Cache-Control   : how long the browser should cache the response
  X-Frame-Options : prevents the page being embedded in iframes (security)
  Strict-Transport-Security: forces HTTPS (security)
  Content-Length  : size of the response in bytes

Install: pip install requests
Run: python 16_http_header_inspector.py
Run: python 16_http_header_inspector.py --url https://github.com
"""

import argparse

try:
    import requests
    from datetime import datetime

    # Security headers to check for (important for web security)
    SECURITY_HEADERS = {
        "Strict-Transport-Security":  "Forces HTTPS — prevents downgrade attacks",
        "X-Frame-Options":            "Prevents clickjacking via iframes",
        "X-Content-Type-Options":     "Prevents MIME-type sniffing",
        "Content-Security-Policy":    "Controls which resources can be loaded",
        "X-XSS-Protection":           "Legacy XSS protection filter",
        "Referrer-Policy":            "Controls what URL info is sent in referrers",
        "Permissions-Policy":         "Controls browser feature access",
    }

    def inspect_headers(url):
        """
        Send an HTTP GET request and return all response headers.
        Also follows redirects and records the redirect chain.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 HeaderInspector/1.0",
            "Accept":     "*/*"
        }

        try:
            # allow_redirects=True follows redirects automatically
            # We also record history (the redirect chain)
            response = requests.get(url, headers=headers, timeout=10,
                                    allow_redirects=True)

            return {
                "url":           url,
                "final_url":     response.url,         # URL after redirects
                "status_code":   response.status_code,
                "headers":       dict(response.headers),
                "redirects":     len(response.history), # number of redirects
                "elapsed_ms":    response.elapsed.total_seconds() * 1000,
                "content_length":len(response.content),
            }

        except requests.exceptions.SSLError as e:
            return {"url": url, "error": f"SSL Error: {e}"}
        except requests.exceptions.ConnectionError:
            return {"url": url, "error": "Cannot connect to server"}
        except Exception as e:
            return {"url": url, "error": str(e)[:100]}


    def analyze_security(headers):
        """Check which security headers are present or missing."""
        present = []
        missing = []
        for header, description in SECURITY_HEADERS.items():
            if header in headers:
                present.append((header, headers[header][:60], description))
            else:
                missing.append((header, description))
        return present, missing


    def print_header_report(result):
        """Display headers in a formatted, categorized report."""
        GREEN = "\033[92m"
        RED   = "\033[91m"
        YEL   = "\033[33m"
        CYN   = "\033[36m"
        RST   = "\033[0m"

        if "error" in result:
            print(f"  Error: {result['error']}")
            return

        h = result["headers"]

        print(f"\n{'='*65}")
        print(f"  HTTP HEADER INSPECTOR")
        print(f"{'='*65}")
        print(f"\n  URL        : {result['url']}")
        if result["url"] != result["final_url"]:
            print(f"  Final URL  : {result['final_url']}  (after {result['redirects']} redirect(s))")
        print(f"  Status     : {result['status_code']}")
        print(f"  Response   : {result['elapsed_ms']:.0f} ms  | "
              f"{result['content_length']:,} bytes")

        # ── Server information ────────────────────────────────────────────────
        print(f"\n  {CYN}Server Information:{RST}")
        for key in ["Server", "X-Powered-By", "Via", "X-Served-By"]:
            if key in h:
                print(f"    {key:<30} {h[key]}")

        # ── Content information ───────────────────────────────────────────────
        print(f"\n  {CYN}Content:{RST}")
        for key in ["Content-Type", "Content-Encoding", "Content-Language",
                    "Content-Length", "Transfer-Encoding"]:
            if key in h:
                print(f"    {key:<30} {h[key]}")

        # ── Caching ───────────────────────────────────────────────────────────
        print(f"\n  {CYN}Caching:{RST}")
        for key in ["Cache-Control", "ETag", "Last-Modified", "Expires",
                    "Age", "Vary"]:
            if key in h:
                print(f"    {key:<30} {h[key][:60]}")

        # ── Security analysis ─────────────────────────────────────────────────
        present, missing = analyze_security(h)

        print(f"\n  Security Headers:")
        if present:
            print(f"  {GREEN}  Present:{RST}")
            for header, value, desc in present:
                print(f"    {GREEN}✓{RST} {header:<40} {value[:30]}")

        if missing:
            print(f"  {YEL}  Missing (consider adding):{RST}")
            for header, desc in missing:
                print(f"    {YEL}○{RST} {header:<40} — {desc}")

        security_score = len(present) / len(SECURITY_HEADERS) * 100
        color = GREEN if security_score >= 70 else (YEL if security_score >= 40 else RED)
        print(f"\n  Security Score: {color}{security_score:.0f}%{RST} "
              f"({len(present)}/{len(SECURITY_HEADERS)} headers present)")

        # ── All headers ────────────────────────────────────────────────────────
        print(f"\n  All Response Headers ({len(h)} total):")
        print("  " + "-" * 60)
        for key, value in sorted(h.items()):
            print(f"  {key:<35} {value[:50]}")


    # ── Main ─────────────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description="Inspect HTTP response headers")
    parser.add_argument("--url",   default="https://httpbin.org/get",
                        help="URL to inspect")
    args = parser.parse_args()

    print("=== HTTP Header Inspector ===")
    result = inspect_headers(args.url)
    print_header_report(result)

except ImportError:
    print("Install: pip install requests")
