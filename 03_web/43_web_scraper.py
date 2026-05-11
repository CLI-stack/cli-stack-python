"""
Script: Web Scraper
What it does: Extracts information from a webpage by parsing its HTML.
Useful for collecting data from websites that don't have an API.

Install: pip install requests beautifulsoup4
Note: Always check a website's robots.txt and terms of service before scraping.
"""

try:
    import requests
    from bs4 import BeautifulSoup  # BeautifulSoup parses HTML

    # --- Scrape a simple public page ---
    url = "https://books.toscrape.com/"  # safe practice scraping site
    print(f"Scraping: {url}\n")

    response = requests.get(url)
    print(f"Status: {response.status_code}")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    # "html.parser" is Python's built-in HTML parser

    # --- Extract the page title ---
    title = soup.find("title")  # find the <title> tag
    print(f"Page title: {title.text.strip()}")

    # --- Extract all book titles ---
    print("\n=== First 10 Books ===")
    books = soup.find_all("article", class_="product_pod")
    # find_all() returns a list of all matching elements

    for i, book in enumerate(books[:10]):
        # Each book article contains an <h3> with the title
        title_tag = book.find("h3").find("a")
        title_text = title_tag.get("title")  # get the title attribute

        # Get price
        price = book.find("p", class_="price_color").text.strip()

        # Get rating (stored as a class name like "star-rating Three")
        rating_tag = book.find("p", class_="star-rating")
        rating = rating_tag.get("class")[1]  # gets "Three", "Four", etc.

        print(f"  {i+1}. {title_text[:40]:<40} {price}  Rating: {rating}")

    # --- Count total books on the page ---
    print(f"\nTotal books on page: {len(books)}")

    # --- Extract links ---
    print("\n=== Navigation Links ===")
    nav = soup.find("ul", class_="nav")
    if nav:
        links = nav.find_all("a")
        for link in links[:5]:
            print(f"  {link.text.strip()}: {link.get('href')}")

except ImportError:
    print("Install: pip install requests beautifulsoup4")
