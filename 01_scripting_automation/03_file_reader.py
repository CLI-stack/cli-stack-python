"""
Script: File Reader
What it does: Opens a text file and reads its contents line by line.
Useful for processing logs, config files, or any plain text data.

How to test: Create a file called "sample.txt" with some text in it,
then run this script.
"""

import os  # os module helps us work with files and folders

# Define the file path (change this to your actual file)
file_path = "sample.txt"

# First, create a sample file so we have something to read
with open("sample.txt", "w") as f:
    f.write("Line 1: Hello from the file!\n")
    f.write("Line 2: Python makes file reading easy.\n")
    f.write("Line 3: This is the last line.\n")

# Now read the file
# "with open(...)" automatically closes the file when done (safe practice)
with open(file_path, "r") as file:  # "r" means read mode
    print("=== Reading entire file at once ===")
    content = file.read()  # reads the whole file as one string
    print(content)

# Read line by line (better for large files)
with open(file_path, "r") as file:
    print("=== Reading line by line ===")
    for line_number, line in enumerate(file, start=1):
        # strip() removes the newline character at the end of each line
        print(f"Line {line_number}: {line.strip()}")

# Clean up the sample file
os.remove("sample.txt")
print("\nDone reading!")
