"""
Script: Web Scraper
What it does: Downloads a web page and extracts information from its HTML.
Web scraping is useful for collecting data that isn't available through an API.
Note: Always check a website's Terms of Service before scraping.

Install: pip install requests beautifulsoup4
"""

try:
    import requests
    from bs4 import BeautifulSoup  # BeautifulSoup parses HTML

    # --- Scrape a simple webpage ---
    url = "https://books.toscrape.com/"  # a safe, legal practice scraping site
    print(f"Scraping: {url}\n")

    response = requests.get(url)
    print(f"Status: {response.status_code}")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    # "html.parser" is Python's built-in HTML parser

    # --- Extract the page title ---
    title = soup.find("title")  # find the <title> tag
    print(f"Page title: {title.text}")

    # --- Extract all book titles ---
    print("\n=== First 5 Books ===")
    books = soup.find_all("article", class_="product_pod")  # find all book cards
    for i, book in enumerate(books[:5]):  # limit to first 5
        # Extract the title from the <h3> inside each book card
        title_tag = book.find("h3").find("a")
        title = title_tag.get("title")  # get the 'title' attribute

        # Extract the price
        price = book.find("p", class_="price_color").text

        # Extract the star rating
        rating = book.find("p", class_="star-rating").get("class")[1]

        print(f"  {i+1}. {title}")
        print(f"     Price: {price} | Rating: {rating}")

    # --- Count total books ---
    total = soup.find("strong")  # finds the "1000 results" text
    if total:
        print(f"\nTotal books on site: {total.text}")

    # --- Extract links ---
    print("\n=== Navigation Links ===")
    nav = soup.find("ul", class_="nav")
    if nav:
        for link in nav.find_all("a")[:5]:
            print(f"  {link.text.strip()}")

except ImportError:
    print("Install: pip install requests beautifulsoup4")
