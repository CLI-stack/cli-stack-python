"""
Script: CSV to JSON Converter
What it does: Converts a CSV file to JSON format.
A common data transformation task when moving data between systems.

Run: python 74_csv_to_json.py input.csv output.json
Run: python 74_csv_to_json.py input.csv --pretty
"""

import argparse
import csv
import json
import os
import sys

def csv_to_json(csv_filepath, json_filepath=None, pretty=True):
    """Read a CSV file and convert it to JSON."""
    rows = []

    with open(csv_filepath, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)  # DictReader uses first row as keys
        for row in reader:
            # Try to convert numbers automatically
            processed_row = {}
            for key, value in row.items():
                try:
                    processed_row[key] = int(value)         # try integer first
                except ValueError:
                    try:
                        processed_row[key] = float(value)   # then float
                    except ValueError:
                        processed_row[key] = value          # keep as string

            rows.append(processed_row)

    # Format the JSON output
    indent = 2 if pretty else None
    json_output = json.dumps(rows, indent=indent)

    # Write to file or print to screen
    if json_filepath:
        with open(json_filepath, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"Converted {len(rows)} rows to: {json_filepath}")
    else:
        print(json_output)

    return rows

# --- Demo: create a sample CSV and convert it ---
# First create a demo CSV file
sample_csv = """name,age,city,salary
Alice,30,New York,75000
Bob,25,London,60000
Charlie,35,Tokyo,90000
Diana,28,Sydney,70000
"""

with open("demo.csv", "w") as f:
    f.write(sample_csv)

print("=== Demo: Converting demo.csv to JSON ===\n")

# Parse arguments (but provide defaults for demo)
parser = argparse.ArgumentParser(description="Convert CSV file to JSON")
parser.add_argument("input", nargs="?", default="demo.csv", help="Input CSV file")
parser.add_argument("output", nargs="?", help="Output JSON file (optional)")
parser.add_argument("--pretty", action="store_true", default=True, help="Pretty print JSON")
parser.add_argument("--compact", action="store_true", help="Compact JSON output")

args = parser.parse_args()

rows = csv_to_json(
    args.input,
    args.output,
    pretty=not args.compact
)

print(f"\nConverted {len(rows)} rows")
print(f"Columns: {list(rows[0].keys()) if rows else []}")

# Clean up demo file
os.remove("demo.csv")
