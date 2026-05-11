"""
Script: BeautifulSoup HTML Parser
What it does: Parses HTML and extracts specific content using CSS selectors
and tag searching. More advanced web scraping techniques.

Install: pip install requests beautifulsoup4
"""

try:
    from bs4 import BeautifulSoup

    # Sample HTML (in real use, you'd get this from requests.get(url).text)
    html = """
    <html>
    <head><title>Sample Store</title></head>
    <body>
        <div id="header">
            <h1>Welcome to Our Store</h1>
        </div>
        <div class="products">
            <div class="product" data-id="1">
                <h2>Laptop</h2>
                <span class="price">$1,200</span>
                <span class="rating">4.5</span>
                <p class="description">High performance laptop</p>
            </div>
            <div class="product" data-id="2">
                <h2>Smartphone</h2>
                <span class="price">$800</span>
                <span class="rating">4.8</span>
                <p class="description">Latest flagship phone</p>
            </div>
            <div class="product" data-id="3">
                <h2>Tablet</h2>
                <span class="price">$500</span>
                <span class="rating">4.2</span>
                <p class="description">Portable tablet device</p>
            </div>
        </div>
        <div id="footer">
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </div>
    </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")

    # --- Find by tag ---
    print("=== Page Title ===")
    print(soup.find("title").text)

    # --- Find by ID ---
    print("\n=== Header (by ID) ===")
    header = soup.find(id="header")
    print(header.find("h1").text)

    # --- Find all products (by class) ---
    print("\n=== All Products ===")
    products = soup.find_all("div", class_="product")
    for product in products:
        name = product.find("h2").text
        price = product.find("span", class_="price").text
        rating = product.find("span", class_="rating").text
        product_id = product.get("data-id")  # get HTML attribute
        print(f"  [{product_id}] {name} - {price} (Rating: {rating})")

    # --- CSS Selectors (more powerful) ---
    print("\n=== Using CSS Selectors ===")
    # Select all <a> tags inside #footer
    links = soup.select("#footer a")
    for link in links:
        print(f"  Link: {link.text} → {link.get('href')}")

    # --- Find by text content ---
    print("\n=== Finding by partial text ===")
    all_spans = soup.find_all("span", class_="price")
    prices = [float(s.text.replace("$", "").replace(",", "")) for s in all_spans]
    print(f"  Average price: ${sum(prices)/len(prices):,.2f}")

except ImportError:
    print("Install: pip install requests beautifulsoup4")
