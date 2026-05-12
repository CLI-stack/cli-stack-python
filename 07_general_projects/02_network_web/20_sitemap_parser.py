"""
Project: Sitemap Parser
What it does: Downloads and parses a website's sitemap.xml file.
A sitemap tells search engines (like Google) about all the pages on a website.
This script extracts all URLs, filters by content type, and shows page priorities.

Install: pip install requests
Run: python 20_sitemap_parser.py
Run: python 20_sitemap_parser.py --url https://python.org/sitemap.xml
"""

import argparse
import re

try:
    import requests
    from xml.etree import ElementTree as ET  # built-in XML parser

    # Sitemaps use XML namespaces — we need to include them in tag searches
    # The namespace is declared in the sitemap's root element
    SITEMAP_NS    = "http://www.sitemaps.org/schemas/sitemap/0.9"
    IMAGE_NS      = "http://www.google.com/schemas/sitemap-image/1.1"
    VIDEO_NS      = "http://www.google.com/schemas/sitemap-video/1.1"

    def fetch_sitemap(url):
        """Download a sitemap.xml and return its XML content."""
        headers = {"User-Agent": "Mozilla/5.0 SitemapParser/1.0"}
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.content  # return raw bytes for XML parsing
        except Exception as e:
            print(f"Error fetching sitemap: {e}")
            return None


    def parse_sitemap(xml_content):
        """
        Parse sitemap XML and extract URL entries.
        Sitemaps can be either:
          1. URL lists (regular sitemap) — contains <url> elements
          2. Sitemap indexes — contains <sitemap> elements that point to other sitemaps
        """
        try:
            # Parse the XML bytes into an ElementTree object
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            print(f"XML parse error: {e}")
            return [], []

        urls     = []  # regular URL entries
        sitemaps = []  # sub-sitemap references (sitemap index)

        # Check if this is a sitemap index (contains links to other sitemaps)
        for sitemap_elem in root.findall(f"{{{SITEMAP_NS}}}sitemap"):
            loc = sitemap_elem.find(f"{{{SITEMAP_NS}}}loc")
            if loc is not None:
                sitemaps.append(loc.text.strip())

        # Parse regular URL entries
        for url_elem in root.findall(f"{{{SITEMAP_NS}}}url"):
            url_data = {}

            # <loc> — the actual URL (required)
            loc = url_elem.find(f"{{{SITEMAP_NS}}}loc")
            if loc is not None:
                url_data["url"] = loc.text.strip()

            # <lastmod> — when the page was last modified (optional)
            lastmod = url_elem.find(f"{{{SITEMAP_NS}}}lastmod")
            if lastmod is not None:
                url_data["lastmod"] = lastmod.text.strip()

            # <changefreq> — how often the page changes (optional)
            changefreq = url_elem.find(f"{{{SITEMAP_NS}}}changefreq")
            if changefreq is not None:
                url_data["changefreq"] = changefreq.text.strip()

            # <priority> — importance from 0.0 to 1.0 (optional, default 0.5)
            priority = url_elem.find(f"{{{SITEMAP_NS}}}priority")
            if priority is not None:
                url_data["priority"] = float(priority.text.strip())
            else:
                url_data["priority"] = 0.5  # default priority

            if "url" in url_data:
                urls.append(url_data)

        return urls, sitemaps


    def analyze_urls(urls):
        """Analyze the URL patterns to categorize pages."""
        from collections import Counter

        # Extract the path structure from each URL
        # e.g., "https://example.com/blog/post-1" → path="/blog/post-1"
        paths = [url["url"].split("/", 3)[3] if url["url"].count("/") >= 3 else ""
                 for url in urls]

        # Get the top-level sections (first path segment)
        sections = Counter()
        for path in paths:
            section = path.split("/")[0] if path else "root"
            sections[section] += 1

        return sections


    def print_sitemap_report(urls, sitemaps, source_url):
        """Display the sitemap analysis."""
        print(f"\n{'='*60}")
        print(f"  SITEMAP ANALYSIS")
        print(f"  Source: {source_url}")
        print(f"{'='*60}")

        if sitemaps:
            print(f"\n  This is a Sitemap INDEX ({len(sitemaps)} sitemaps):")
            for sm in sitemaps:
                print(f"    → {sm}")

        print(f"\n  Total URLs: {len(urls)}")

        if not urls:
            return

        # Priority distribution
        high_priority = [u for u in urls if u.get("priority", 0.5) >= 0.8]
        print(f"  High priority (≥0.8): {len(high_priority)}")

        # Change frequency distribution
        from collections import Counter
        freq_counts = Counter(u.get("changefreq", "unspecified") for u in urls)
        if any(v != "unspecified" for v in freq_counts):
            print(f"\n  Update frequency:")
            for freq, count in sorted(freq_counts.items()):
                print(f"    {freq:<15} {count}")

        # URL sections
        sections = analyze_urls(urls)
        if sections:
            print(f"\n  Site sections (top URL path segments):")
            for section, count in sections.most_common(10):
                bar = "█" * min(count, 20)
                print(f"    {'/' + section:<25} {count:>4}  {bar}")

        # Sample of highest priority URLs
        top_urls = sorted(urls, key=lambda u: u.get("priority", 0.5), reverse=True)
        print(f"\n  Top priority URLs (first 10):")
        print(f"  {'PRIORITY':>9}  {'LAST MODIFIED':<14}  URL")
        print("  " + "-" * 70)
        for u in top_urls[:10]:
            priority = u.get("priority", 0.5)
            lastmod  = u.get("lastmod", "N/A")[:10]
            print(f"  {priority:>9.1f}  {lastmod:<14}  {u['url'][:60]}")


    # Sample sitemap XML for demo (in case the network request fails)
    SAMPLE_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc><priority>1.0</priority><changefreq>daily</changefreq></url>
  <url><loc>https://example.com/about</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>
  <url><loc>https://example.com/blog</loc><priority>0.7</priority><changefreq>weekly</changefreq></url>
  <url><loc>https://example.com/blog/post-1</loc><priority>0.6</priority><lastmod>2024-01-15</lastmod></url>
  <url><loc>https://example.com/blog/post-2</loc><priority>0.6</priority><lastmod>2024-01-10</lastmod></url>
  <url><loc>https://example.com/contact</loc><priority>0.5</priority></url>
  <url><loc>https://example.com/products</loc><priority>0.8</priority><changefreq>daily</changefreq></url>
  <url><loc>https://example.com/products/laptop</loc><priority>0.7</priority></url>
</urlset>"""

    # ── Main ─────────────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description="Parse and analyze a website sitemap")
    parser.add_argument("--url", default="https://httpbin.org",
                        help="Website URL or direct sitemap URL")
    args = parser.parse_args()

    print("=== Sitemap Parser ===\n")

    # Try to find the sitemap URL
    url = args.url
    if not url.endswith(".xml"):
        url = url.rstrip("/") + "/sitemap.xml"

    print(f"Fetching: {url}")
    xml_content = fetch_sitemap(url)

    if not xml_content:
        print("Using built-in sample sitemap for demo.\n")
        xml_content = SAMPLE_SITEMAP.encode()

    urls, sitemaps = parse_sitemap(xml_content)
    print_sitemap_report(urls, sitemaps, url)

except ImportError:
    print("Install: pip install requests")
