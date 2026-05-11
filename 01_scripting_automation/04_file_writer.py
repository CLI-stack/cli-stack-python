"""
Script: File Writer
What it does: Creates a new file and writes text into it.
You can write one line at a time or all at once.
"""

import os

# --- Write mode ("w") --- creates a new file or overwrites existing
with open("output.txt", "w") as file:  # "w" = write mode
    file.write("This is the first line.\n")  # \n adds a new line
    file.write("This is the second line.\n")
    file.write("Python file writing is simple!\n")

print("File created: output.txt")

# --- Append mode ("a") --- adds to the end of an existing file
with open("output.txt", "a") as file:  # "a" = append mode
    file.write("This line was added later.\n")

print("Text appended to file.")

# --- Write a list of lines using writelines() ---
lines = [
    "Apple\n",
    "Banana\n",
    "Cherry\n"
]

with open("fruits.txt", "w") as file:
    file.writelines(lines)  # writes all items in the list

print("Fruits file created.")

# Verify what was written by reading it back
with open("output.txt", "r") as file:
    print("\n=== Contents of output.txt ===")
    print(file.read())

# Clean up
os.remove("output.txt")
os.remove("fruits.txt")
