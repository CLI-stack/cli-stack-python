"""
Script: RSS Feed Reader
What it does: Reads and parses RSS feeds to get the latest news/articles.
RSS is a format used by blogs and news sites to syndicate content.

Install: pip install feedparser requests
"""

try:
    import feedparser  # library for parsing RSS/Atom feeds

    def read_feed(url, limit=5):
        """Parse an RSS feed and return the latest entries."""
        print(f"Reading feed: {url}")
        feed = feedparser.parse(url)

        if feed.bozo:  # bozo=True means there was a parse error
            print("Warning: Feed may have issues")

        print(f"Feed title: {feed.feed.get('title', 'Unknown')}")
        print(f"Total entries: {len(feed.entries)}")

        entries = []
        for entry in feed.entries[:limit]:
            entries.append({
                "title": entry.get("title", "No title"),
                "link":  entry.get("link", ""),
                "published": entry.get("published", "Unknown date"),
                "summary": entry.get("summary", "")[:100]  # first 100 chars
            })
        return entries

    # --- Read Python news ---
    print("=== Python Official News ===")
    entries = read_feed("https://www.python.org/dev/peps/pep-0/")
    # (If URL doesn't work, try any RSS URL)

    # Try a working RSS feed
    entries = read_feed("https://realpython.com/atom.xml", limit=5)
    print()
    for i, entry in enumerate(entries, 1):
        print(f"{i}. {entry['title']}")
        print(f"   Published: {entry['published']}")
        print(f"   Link: {entry['link']}")
        print()

except ImportError:
    print("Install: pip install feedparser")

    # Show structure without library
    print("\nAlternatively, read RSS manually with requests:")
    try:
        import requests
        from xml.etree import ElementTree as ET

        response = requests.get("https://realpython.com/atom.xml")
        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        entries = root.findall("atom:entry", ns)[:3]
        for entry in entries:
            title = entry.find("atom:title", ns)
            if title is not None:
                print(f"  - {title.text}")
    except Exception as e:
        print(f"Error: {e}")
