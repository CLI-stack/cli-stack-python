"""
Script: HTML Parser with BeautifulSoup
What it does: Demonstrates how to parse and navigate HTML structure.
BeautifulSoup is the most popular Python library for parsing HTML.

Install: pip install beautifulsoup4 requests
"""

try:
    from bs4 import BeautifulSoup
    import requests

    # --- Parse HTML string directly (no network needed) ---
    html = """
    <html>
    <head><title>Sample Page</title></head>
    <body>
        <h1 id="main-title">Welcome to Python Scraping</h1>
        <div class="container">
            <p class="intro">This is an introduction paragraph.</p>
            <ul id="skills-list">
                <li class="skill">Python</li>
                <li class="skill">HTML</li>
                <li class="skill">CSS</li>
                <li class="skill">JavaScript</li>
            </ul>
        </div>
        <div class="links">
            <a href="https://python.org">Python Docs</a>
            <a href="https://github.com">GitHub</a>
        </div>
        <table>
            <tr><th>Name</th><th>Score</th></tr>
            <tr><td>Alice</td><td>95</td></tr>
            <tr><td>Bob</td><td>87</td></tr>
        </table>
    </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")

    # --- Find single elements ---
    print("=== Finding Elements ===")
    title = soup.find("title")
    print(f"Page title: {title.text}")

    h1 = soup.find("h1")
    print(f"H1 text:    {h1.text}")
    print(f"H1 id:      {h1.get('id')}")  # get attribute value

    # --- Find by class ---
    intro = soup.find("p", class_="intro")
    print(f"Intro:      {intro.text}")

    # --- Find all matching elements ---
    print("\n=== All Skills ===")
    skills = soup.find_all("li", class_="skill")
    for skill in skills:
        print(f"  - {skill.text}")

    # --- Find all links ---
    print("\n=== All Links ===")
    links = soup.find_all("a")
    for link in links:
        print(f"  {link.text} → {link.get('href')}")

    # --- Parse a table ---
    print("\n=== Table Data ===")
    rows = soup.find("table").find_all("tr")
    for row in rows:
        cells = [cell.text for cell in row.find_all(["th", "td"])]
        print(f"  {cells}")

    # --- Navigate with CSS selectors ---
    print("\n=== CSS Selectors ===")
    container_p = soup.select_one(".container p")  # p inside .container
    print(f"Container paragraph: {container_p.text}")

except ImportError:
    print("Install: pip install beautifulsoup4 requests")
