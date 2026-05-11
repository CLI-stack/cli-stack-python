"""
Script: DateTime CLI Tool
What it does: A collection of date and time utilities.
Converts between timezones, formats dates, calculates differences.

Run: python 80_datetime_cli.py
"""

from datetime import datetime, timedelta, timezone
import time

print("=== Python DateTime Utilities ===\n")

# --- Current date and time ---
now = datetime.now()
utc_now = datetime.now(timezone.utc)

print("--- Current Date/Time ---")
print(f"Local time:  {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"UTC time:    {utc_now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"Unix timestamp: {int(time.time())}")

# --- Formatting dates ---
print("\n--- Date Formatting ---")
formats = {
    "ISO 8601":     "%Y-%m-%d",           # 2024-01-15
    "US format":    "%m/%d/%Y",           # 01/15/2024
    "UK format":    "%d/%m/%Y",           # 15/01/2024
    "Long format":  "%B %d, %Y",          # January 15, 2024
    "With time":    "%Y-%m-%d %H:%M:%S",  # 2024-01-15 14:30:00
    "Day name":     "%A, %B %d, %Y",      # Monday, January 15, 2024
}

for name, fmt in formats.items():
    print(f"  {name:<15}: {now.strftime(fmt)}")

# --- Parsing date strings ---
print("\n--- Parsing Date Strings ---")
date_strings = [
    ("2024-01-15", "%Y-%m-%d"),
    ("January 15, 2024", "%B %d, %Y"),
    ("15/01/2024", "%d/%m/%Y"),
]

for date_str, fmt in date_strings:
    parsed = datetime.strptime(date_str, fmt)
    print(f"  '{date_str}' → {parsed.date()}")

# --- Date arithmetic ---
print("\n--- Date Arithmetic ---")
today = datetime.today().date()
print(f"Today:        {today}")
print(f"Yesterday:    {today - timedelta(days=1)}")
print(f"Tomorrow:     {today + timedelta(days=1)}")
print(f"One week ago: {today - timedelta(weeks=1)}")
print(f"30 days from now: {today + timedelta(days=30)}")

# --- Calculate difference between dates ---
print("\n--- Date Differences ---")
start = datetime(2024, 1, 1)
end = datetime(2024, 12, 31)
diff = end - start
print(f"Days in 2024: {diff.days}")

birthday = datetime(1995, 6, 15)
age_days = (now - birthday).days
print(f"Days since June 15, 1995: {age_days:,} days")

# --- Day of week, week number ---
print("\n--- Date Properties ---")
print(f"Day of week: {now.strftime('%A')}")
print(f"Week number: {now.strftime('%W')}")
print(f"Day of year: {now.strftime('%j')}")
print(f"Is weekend:  {now.weekday() >= 5}")
