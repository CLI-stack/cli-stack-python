"""
Project: Data Validator
What it does: Validates data rows against a set of rules before importing
into a database or processing further. Catches bad data early — wrong types,
missing fields, out-of-range values, invalid email formats, etc.

This is a critical step in any data pipeline. "Garbage in, garbage out."

Run: python 05_data_validator.py
"""

import re        # for regex-based pattern validation
import json      # for loading data from JSON
from datetime import datetime


# ── Define validation rules ───────────────────────────────────────────────────
# Each rule is: field_name → list of (rule_function, error_message) pairs
# The rule function takes the value and returns True (valid) or False (invalid)

VALIDATION_RULES = {
    "name": [
        (lambda v: isinstance(v, str) and len(v) >= 2,
         "Name must be a string of at least 2 characters"),
        (lambda v: all(c.isalpha() or c in " '-" for c in str(v)),
         "Name may only contain letters, spaces, hyphens, apostrophes"),
    ],
    "age": [
        (lambda v: isinstance(v, int),
         "Age must be an integer"),
        (lambda v: 0 <= int(v) <= 130,
         "Age must be between 0 and 130"),
    ],
    "email": [
        (lambda v: bool(re.match(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$", str(v))),
         "Email must be a valid email address (e.g. user@example.com)"),
    ],
    "salary": [
        (lambda v: isinstance(v, (int, float)),
         "Salary must be a number"),
        (lambda v: float(v) >= 0,
         "Salary cannot be negative"),
        (lambda v: float(v) <= 10_000_000,
         "Salary seems unrealistically high (> $10M)"),
    ],
    "department": [
        (lambda v: str(v).strip() != "",
         "Department cannot be empty"),
        (lambda v: str(v) in ["Engineering", "Sales", "Marketing", "HR", "Finance"],
         "Department must be one of: Engineering, Sales, Marketing, HR, Finance"),
    ],
}

# Fields that MUST be present (cannot be None or missing)
REQUIRED_FIELDS = ["name", "age", "email"]


# ── Sample data with intentional errors ───────────────────────────────────────
SAMPLE_DATA = [
    {"name": "Alice Johnson", "age": 30,   "email": "alice@company.com",
     "salary": 75000, "department": "Engineering"},          # valid

    {"name": "Bob",           "age": 25,   "email": "bob@company.com",
     "salary": 60000, "department": "Sales"},                # valid

    {"name": "C",             "age": 28,   "email": "charlie@co.com",
     "salary": 70000, "department": "Engineering"},          # FAIL: name too short

    {"name": "Diana",         "age": -5,   "email": "diana@co.com",
     "salary": 65000, "department": "Marketing"},            # FAIL: negative age

    {"name": "Eve",           "age": 35,   "email": "not-an-email",
     "salary": 80000, "department": "HR"},                   # FAIL: bad email

    {"name": "Frank",         "age": 40,   "email": "frank@company.com",
     "salary": -1000, "department": "Finance"},              # FAIL: negative salary

    {"name": None,            "age": 22,   "email": "noname@co.com",
     "salary": 50000, "department": "Sales"},                # FAIL: missing name

    {"name": "Grace",         "age": 29,   "email": "grace@company.com",
     "salary": 72000, "department": "Unknown"},              # FAIL: invalid department
]


def validate_row(row, row_number):
    """
    Validate a single data row against all rules.
    Returns a list of error messages (empty list = all valid).
    """
    errors = []

    # ── Check 1: Required fields must not be None ──────────────────────────
    for field in REQUIRED_FIELDS:
        value = row.get(field)        # .get() returns None if field is missing
        if value is None:
            errors.append(f"Required field '{field}' is missing or None")
            # Skip further validation for this field since it's None
            continue

    # ── Check 2: Apply validation rules for each field ────────────────────
    for field, rules in VALIDATION_RULES.items():
        value = row.get(field)

        if value is None:
            continue  # already caught above if required

        for rule_func, error_message in rules:
            try:
                if not rule_func(value):
                    errors.append(f"[{field}={value!r}] {error_message}")
            except (TypeError, ValueError):
                # The rule function crashed — the value type is completely wrong
                errors.append(f"[{field}={value!r}] Cannot validate — unexpected type")

    return errors


def validate_dataset(data):
    """Validate all rows and collect results."""
    results   = []
    valid_rows = []
    error_rows = []

    for i, row in enumerate(data, start=1):  # enumerate gives (index, value) pairs
        errors = validate_row(row, i)
        result = {
            "row":    i,
            "data":   row,
            "valid":  len(errors) == 0,  # True if no errors found
            "errors": errors,
        }
        results.append(result)

        if result["valid"]:
            valid_rows.append(row)
        else:
            error_rows.append(result)

    return results, valid_rows, error_rows


def print_validation_report(results, valid_rows, error_rows):
    """Print a formatted validation report."""
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    total = len(results)
    print("=" * 60)
    print("  DATA VALIDATION REPORT")
    print("=" * 60)
    print(f"\n  Total rows  : {total}")
    print(f"  {GREEN}Valid rows   : {len(valid_rows)}{RST}")
    print(f"  {RED}Invalid rows : {len(error_rows)}{RST}")
    print(f"  Pass rate   : {len(valid_rows)/total*100:.1f}%")

    if error_rows:
        print(f"\n  {RED}Rows with errors:{RST}")
        for r in error_rows:
            name = r["data"].get("name", "?")
            print(f"\n  Row {r['row']} — {name}")
            for error in r["errors"]:
                print(f"    ✗ {error}")

    print(f"\n  {GREEN}Valid rows (ready for import):{RST}")
    for row in valid_rows:
        print(f"    ✓ {row['name']:<20} {row['email']}")


# ── Main ─────────────────────────────────────────────────────────────────────
print("=== Data Validator ===\n")
results, valid_rows, error_rows = validate_dataset(SAMPLE_DATA)
print_validation_report(results, valid_rows, error_rows)
