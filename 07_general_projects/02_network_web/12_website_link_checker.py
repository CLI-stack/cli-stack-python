"""
Project: Website Link Checker
What it does: Scans a webpage and checks whether every link on it is working
(returns HTTP 200) or broken (returns 404, 500, or fails to connect).
Also known as a "broken link checker" — essential for website maintenance.

Install: pip install requests beautifulsoup4
Run: python 12_website_link_checker.py
Run: python 12_website_link_checker.py --url https://example.com
"""

import argparse

try:
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse

    # Status code descriptions for common HTTP errors
    STATUS_DESCRIPTIONS = {
        200: "OK",
        301: "Moved Permanently (redirect)",
        302: "Found (temporary redirect)",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Server Error",
        503: "Service Unavailable",
    }

    def get_all_links(url):
        """
        Download a webpage and extract all hyperlinks from it.
        Returns a list of absolute URLs found on the page.
        """
        try:
            # Set a User-Agent header so servers don't block us as a bot
            headers = {"User-Agent": "Mozilla/5.0 LinkChecker/1.0"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # raise exception for 4xx/5xx
        except Exception as e:
            print(f"Cannot access page: {e}")
            return []

        # Parse the HTML to find all <a href="..."> tags
        soup  = BeautifulSoup(response.text, "html.parser")
        links = set()  # use a set to avoid checking the same URL twice

        for tag in soup.find_all("a", href=True):  # find all <a> tags with href attribute
            href = tag.get("href")  # get the href value

            # Skip non-HTTP links (mailto:, javascript:, etc.)
            if href.startswith(("mailto:", "javascript:", "tel:", "#")):
                continue

            # Convert relative URL to absolute URL
            # e.g. "/about" → "https://example.com/about"
            absolute_url = urljoin(url, href)
            links.add(absolute_url)

        return sorted(links)


    def check_link(url, timeout=5):
        """
        Send an HTTP HEAD request to check if a URL is accessible.
        HEAD request is like GET but the server only sends headers, not the body.
        This is faster and uses less bandwidth than a full GET request.
        """
        try:
            headers  = {"User-Agent": "Mozilla/5.0 LinkChecker/1.0"}
            response = requests.head(url, headers=headers, timeout=timeout,
                                     allow_redirects=True)  # follow redirects

            status    = response.status_code
            is_ok     = status < 400  # status < 400 means success
            desc      = STATUS_DESCRIPTIONS.get(status, f"HTTP {status}")

            return {"url": url, "status": status, "ok": is_ok, "desc": desc}

        except requests.exceptions.ConnectionError:
            return {"url": url, "status": 0, "ok": False, "desc": "Cannot connect"}
        except requests.exceptions.Timeout:
            return {"url": url, "status": 0, "ok": False, "desc": "Timed out"}
        except Exception as e:
            return {"url": url, "status": 0, "ok": False, "desc": str(e)[:50]}


    def check_all_links(page_url):
        """Check all links on a page and return results."""
        print(f"Fetching links from: {page_url}\n")

        links = get_all_links(page_url)
        if not links:
            print("No links found on the page.")
            return []

        print(f"Found {len(links)} unique links. Checking...\n")
        results = []

        for i, url in enumerate(links, 1):
            print(f"\r  Checking [{i:>3}/{len(links)}]: {url[:60]:<60}", end="", flush=True)
            result = check_link(url)
            results.append(result)

        print("\r" + " " * 80 + "\r")  # clear the progress line
        return results


    def print_report(results, page_url):
        """Display the link check results."""
        GREEN = "\033[92m"
        RED   = "\033[91m"
        YEL   = "\033[33m"
        RST   = "\033[0m"

        ok_links  = [r for r in results if r["ok"]]
        bad_links = [r for r in results if not r["ok"]]

        print(f"{'='*65}")
        print(f"  LINK CHECK REPORT: {page_url}")
        print(f"{'='*65}")
        print(f"\n  Total links checked : {len(results)}")
        print(f"  {GREEN}Working links       : {len(ok_links)}{RST}")
        print(f"  {RED}Broken links        : {len(bad_links)}{RST}")

        if bad_links:
            print(f"\n  {RED}Broken Links (need attention):{RST}")
            print(f"  {'STATUS':>7}  {'DESCRIPTION':<25}  URL")
            print("  " + "-" * 75)
            for r in bad_links:
                print(f"  {r['status']:>7}  {r['desc']:<25}  {r['url'][:50]}")

        if ok_links:
            print(f"\n  {GREEN}Working Links:{RST}")
            for r in ok_links[:10]:  # show first 10
                print(f"  [{r['status']}] {r['url'][:70]}")
            if len(ok_links) > 10:
                print(f"  ... and {len(ok_links) - 10} more")


    # ── Main ─────────────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description="Check all links on a webpage")
    parser.add_argument("--url", default="https://example.com",
                        help="URL of the webpage to check")
    args = parser.parse_args()

    print("=== Website Link Checker ===\n")
    results = check_all_links(args.url)
    if results:
        print_report(results, args.url)

except ImportError:
    print("Install: pip install requests beautifulsoup4")
