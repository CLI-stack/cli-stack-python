"""
Script: JSON Reader and Writer
What it does: Reads and writes JSON files.
JSON (JavaScript Object Notation) is widely used for storing and sharing data,
especially in web APIs and configuration files.
"""

import json  # built-in module for JSON handling
import os

# --- Create a sample JSON file ---
data = {
    "company": "TechCorp",
    "employees": [
        {"name": "Alice", "role": "Developer", "age": 30},
        {"name": "Bob", "role": "Designer", "age": 25},
        {"name": "Charlie", "role": "Manager", "age": 40}
    ],
    "active": True,
    "founded": 2010
}

# Write (dump) Python dictionary to a JSON file
with open("company.json", "w") as file:
    json.dump(data, file, indent=4)  # indent=4 makes it human-readable

print("JSON file created: company.json\n")

# --- Read (load) a JSON file ---
with open("company.json", "r") as file:
    loaded_data = json.load(file)  # converts JSON into Python dictionary

print("Company:", loaded_data["company"])
print("Founded:", loaded_data["founded"])
print("Active:", loaded_data["active"])

# Access nested data (list of employees)
print("\n=== Employees ===")
for employee in loaded_data["employees"]:
    print(f"  {employee['name']} - {employee['role']} (Age: {employee['age']})")

# --- Convert between JSON string and Python object ---
json_string = '{"city": "Paris", "population": 2161000}'
parsed = json.loads(json_string)  # string → Python dict
print(f"\nCity from string: {parsed['city']}")

back_to_string = json.dumps(parsed, indent=2)  # Python dict → string
print("Back to JSON string:\n", back_to_string)

os.remove("company.json")
