"""
Script: Regular Expressions (Regex) Search
What it does: Searches for patterns in text using regular expressions.
Regex is a powerful mini-language for matching, extracting, and validating text.
"""

import re  # built-in regular expressions module

text = """
Contact us at support@example.com or sales@company.org
Call: +1-800-555-1234 or (555) 987-6543
Visit: https://www.example.com or http://blog.site.org
Order #12345 placed on 2024-01-15. Order #67890 placed on 2024-02-20.
"""

# --- Find email addresses ---
# Pattern: word chars + @ + word chars + . + letters
email_pattern = r"[\w.+-]+@[\w-]+\.[a-zA-Z]+"
emails = re.findall(email_pattern, text)  # findall returns a list of all matches
print("=== Email Addresses Found ===")
for email in emails:
    print(f"  {email}")

# --- Find phone numbers ---
phone_pattern = r"[\+\(]?[\d\s\-\(\)]{10,}"
phones = re.findall(phone_pattern, text)
print("\n=== Phone Numbers Found ===")
for phone in phones:
    print(f"  {phone.strip()}")

# --- Find URLs ---
url_pattern = r"https?://[^\s]+"  # starts with http:// or https://
urls = re.findall(url_pattern, text)
print("\n=== URLs Found ===")
for url in urls:
    print(f"  {url}")

# --- Find dates (YYYY-MM-DD format) ---
date_pattern = r"\d{4}-\d{2}-\d{2}"
dates = re.findall(date_pattern, text)
print("\n=== Dates Found ===")
for date in dates:
    print(f"  {date}")

# --- Validate an email address ---
def is_valid_email(email):
    pattern = r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

print("\n=== Email Validation ===")
test_emails = ["user@example.com", "invalid-email", "another@test.org", "bad@"]
for email in test_emails:
    valid = "✓ Valid" if is_valid_email(email) else "✗ Invalid"
    print(f"  {email}: {valid}")
