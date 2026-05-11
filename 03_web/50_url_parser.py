"""
Script: URL Parser and Builder
What it does: Breaks a URL into its components and builds new URLs.
Understanding URL structure is fundamental for web development.
"""

from urllib.parse import urlparse, urlencode, urljoin, urlunparse, parse_qs

# --- Parse a URL into its parts ---
url = "https://www.example.com:8080/search?q=python&page=2&lang=en#results"

parsed = urlparse(url)
print("=== Parsing URL ===")
print(f"Full URL:  {url}\n")
print(f"Scheme:    {parsed.scheme}")    # https
print(f"Netloc:    {parsed.netloc}")    # www.example.com:8080
print(f"Hostname:  {parsed.hostname}")  # www.example.com
print(f"Port:      {parsed.port}")      # 8080
print(f"Path:      {parsed.path}")      # /search
print(f"Query:     {parsed.query}")     # q=python&page=2&lang=en
print(f"Fragment:  {parsed.fragment}")  # results (the #part)

# --- Parse query string parameters ---
print("\n=== Query Parameters ===")
params = parse_qs(parsed.query)  # converts query string to dictionary
for key, value in params.items():
    print(f"  {key}: {value[0]}")

# --- Build a URL from parts ---
print("\n=== Building a URL ===")
base_url = "https://api.example.com"
endpoint = "/v1/users"
query_params = {
    "page": 1,
    "limit": 20,
    "sort": "name",
    "active": "true"
}

# urlencode converts dict to query string
query_string = urlencode(query_params)
full_url = f"{base_url}{endpoint}?{query_string}"
print(f"Built URL: {full_url}")

# --- Join relative and absolute URLs ---
print("\n=== URL Joining ===")
base = "https://www.example.com/products/"
relative = "../about"
joined = urljoin(base, relative)
print(f"Base:     {base}")
print(f"Relative: {relative}")
print(f"Joined:   {joined}")

# --- Validate a URL format ---
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

print("\n=== URL Validation ===")
test_urls = ["https://www.google.com", "not-a-url", "http://valid.org/path?q=1", "ftp://"]
for u in test_urls:
    print(f"  {u:<40} {'✓ Valid' if is_valid_url(u) else '✗ Invalid'}")
