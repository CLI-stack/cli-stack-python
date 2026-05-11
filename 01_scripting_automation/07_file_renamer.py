"""
Script: File Renamer
What it does: Renames files — one at a time or in bulk.
Useful for organizing files, fixing naming conventions, etc.
"""

import os

# Create some test files to rename
test_files = ["report_jan.txt", "report_feb.txt", "report_mar.txt"]
for filename in test_files:
    with open(filename, "w") as f:
        f.write(f"Content of {filename}")

print("Test files created:", test_files)

# --- Rename a single file ---
os.rename("report_jan.txt", "report_january.txt")
print("\nRenamed: report_jan.txt → report_january.txt")

# --- Rename files in bulk ---
# Example: rename all "report_" files by adding "2024_" prefix
print("\n=== Bulk rename: add '2024_' prefix ===")
for filename in os.listdir("."):
    if filename.startswith("report_") and filename.endswith(".txt"):
        new_name = "2024_" + filename  # build the new name
        os.rename(filename, new_name)
        print(f"  {filename} → {new_name}")

# --- Rename by replacing part of the name ---
print("\n=== Replace 'report' with 'summary' ===")
for filename in os.listdir("."):
    if filename.startswith("2024_report_"):
        new_name = filename.replace("report", "summary")
        os.rename(filename, new_name)
        print(f"  {filename} → {new_name}")

# List current files to verify
print("\n=== Current files ===")
for filename in os.listdir("."):
    if "summary" in filename:
        print(" -", filename)
        os.remove(filename)  # clean up
