"""
Script: JSON Formatter and Validator
What it does: Formats (pretty-prints) JSON, validates it, and can query it.
Useful when working with raw API responses or config files.

Run: python 75_json_formatter.py
Run: echo '{"name":"Alice"}' | python 75_json_formatter.py
"""

import json
import sys
import argparse

def format_json(text, indent=2, sort_keys=False):
    """Parse and pretty-print JSON text."""
    try:
        data = json.loads(text)   # parse JSON string → Python object
        formatted = json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
        return formatted, None
    except json.JSONDecodeError as e:
        return None, str(e)       # return error message

def get_value(data, path):
    """Get a value from nested JSON using dot notation (e.g., 'user.name')."""
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return current

# --- Demo ---
sample_json = '{"name":"Alice","age":30,"address":{"city":"NYC","zip":"10001"},"hobbies":["reading","coding"]}'

print("=== JSON Formatter Demo ===\n")
print(f"Input (compact):\n{sample_json}\n")

formatted, error = format_json(sample_json)
if error:
    print(f"Invalid JSON: {error}")
else:
    print(f"Output (pretty):\n{formatted}")

# Sort keys
formatted_sorted, _ = format_json(sample_json, sort_keys=True)
print(f"\nWith sorted keys:\n{formatted_sorted}")

# Query nested values
data = json.loads(sample_json)
print("\n=== Querying Values ===")
for path in ["name", "age", "address.city", "hobbies.0"]:
    value = get_value(data, path)
    print(f"  {path} → {value}")

# Validate multiple JSON strings
print("\n=== JSON Validation ===")
test_cases = [
    '{"valid": true}',
    '{"invalid": }',
    '["list", "of", "values"]',
    'just a string',
    '{"nested": {"works": true}}',
]

for test in test_cases:
    _, error = format_json(test)
    status = "✓ Valid" if not error else f"✗ Invalid: {error}"
    print(f"  {test[:30]:<32} {status}")
