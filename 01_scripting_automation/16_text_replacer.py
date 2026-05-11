"""
Script: Text Find and Replace
What it does: Searches for text inside a file and replaces it with something else.
Like the Find & Replace feature in a text editor, but scriptable.
"""

import os

# Create a sample file with text to replace
original_text = """Hello, my name is John.
John works at AcmeCorp.
John's phone number is 555-1234.
AcmeCorp was founded in 2000.
John loves Python programming.
"""

with open("document.txt", "w") as f:
    f.write(original_text)

print("Original file created.\n")
print("=== Original Content ===")
print(original_text)

# --- Simple replacement: replace one word ---
def replace_in_file(filepath, old_text, new_text):
    """Read a file, replace text, and write it back."""
    with open(filepath, "r") as f:
        content = f.read()          # read entire file

    new_content = content.replace(old_text, new_text)  # replace all occurrences

    with open(filepath, "w") as f:
        f.write(new_content)        # write back to file

    return content.count(old_text)  # return how many replacements were made

# Replace "John" with "Alice"
count = replace_in_file("document.txt", "John", "Alice")
print(f"Replaced 'John' with 'Alice' ({count} times)\n")

# Replace "AcmeCorp" with "TechStartup"
count = replace_in_file("document.txt", "AcmeCorp", "TechStartup")
print(f"Replaced 'AcmeCorp' with 'TechStartup' ({count} times)\n")

# Read and display the final result
with open("document.txt", "r") as f:
    print("=== Updated Content ===")
    print(f.read())

os.remove("document.txt")
