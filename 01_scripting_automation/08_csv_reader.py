"""
Script: CSV Reader
What it does: Reads a CSV (Comma-Separated Values) file.
CSV files are commonly used to store tabular data like spreadsheets.
"""

import csv  # built-in module for reading/writing CSV files
import os

# Create a sample CSV file to read
sample_data = """name,age,city,salary
Alice,30,New York,75000
Bob,25,London,60000
Charlie,35,Tokyo,90000
Diana,28,Sydney,70000
"""

with open("employees.csv", "w") as f:
    f.write(sample_data)

print("Sample CSV created: employees.csv\n")

# --- Read CSV as rows (list of lists) ---
print("=== Reading row by row ===")
with open("employees.csv", "r") as file:
    reader = csv.reader(file)  # creates a CSV reader object
    for row in reader:
        print(row)  # each row is a list of values

# --- Read CSV as dictionaries (easier to work with) ---
print("\n=== Reading as dictionary (column names as keys) ===")
with open("employees.csv", "r") as file:
    reader = csv.DictReader(file)  # first row becomes the column headers
    for row in reader:
        # Now you can access values by column name
        print(f"Name: {row['name']}, Age: {row['age']}, City: {row['city']}")

# --- Filter rows based on a condition ---
print("\n=== Employees with salary above 70000 ===")
with open("employees.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        if int(row["salary"]) > 70000:  # convert string to int for comparison
            print(f"  {row['name']} - ${row['salary']}")

os.remove("employees.csv")
