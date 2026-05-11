"""
Script: Fetch and Process JSON from a Public API
What it does: Gets real data from a public API and processes/displays it.
Uses a free weather or data API — no API key required.

Install: pip install requests
"""

try:
    import requests
    import json

    # --- Fetch data from a public API (no key needed) ---
    # Using the REST Countries API — returns info about countries
    print("=== Fetching Country Data from REST Countries API ===")
    url = "https://restcountries.com/v3.1/region/asia?fields=name,capital,population,area"

    response = requests.get(url, timeout=10)
    countries = response.json()

    print(f"Fetched {len(countries)} countries in Asia\n")

    # Sort by population (largest first)
    countries_sorted = sorted(countries, key=lambda c: c.get("population", 0), reverse=True)

    print(f"{'Country':<25} {'Capital':<20} {'Population':>15} {'Area (km²)':>15}")
    print("-" * 80)

    for country in countries_sorted[:10]:  # show top 10
        name = country["name"]["common"]
        capital = country.get("capital", ["N/A"])[0] if country.get("capital") else "N/A"
        population = country.get("population", 0)
        area = country.get("area", 0)

        print(f"{name:<25} {capital:<20} {population:>15,} {area:>15,.0f}")

    # --- Calculate total population ---
    total_pop = sum(c.get("population", 0) for c in countries)
    print(f"\nTotal population (Asia): {total_pop:,}")

    # --- Fetch a random joke (just for fun!) ---
    print("\n=== Random Programming Joke ===")
    joke_response = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
    if joke_response.status_code == 200:
        jokes = joke_response.json()
        if jokes:
            joke = jokes[0]
            print(f"Q: {joke['setup']}")
            print(f"A: {joke['punchline']}")

except ImportError:
    print("Install: pip install requests")
except Exception as e:
    print(f"Error fetching data: {e}")
    print("(APIs may be temporarily unavailable)")
