"""
Script: String Operations
What it does: Comprehensive guide to working with strings in Python.
Strings are one of the most used data types — master these operations!
"""

# --- Basic String Operations ---
text = "Hello, World! Python is Amazing."
print("=== Basic Operations ===")
print(f"Original:  {text}")
print(f"Uppercase: {text.upper()}")
print(f"Lowercase: {text.lower()}")
print(f"Length:    {len(text)} characters")
print(f"Reversed:  {text[::-1]}")  # slicing with step=-1 reverses

# --- Searching and Checking ---
print("\n=== Searching ===")
print(f"Starts with 'Hello': {text.startswith('Hello')}")
print(f"Ends with 'Amazing.': {text.endswith('Amazing.')}")
print(f"Contains 'Python': {'Python' in text}")
print(f"Index of 'World':  {text.find('World')}")  # returns -1 if not found
print(f"Count of 'l':      {text.count('l')}")

# --- Splitting and Joining ---
print("\n=== Split and Join ===")
sentence = "apple,banana,cherry,date"
fruits = sentence.split(",")   # split by comma
print(f"Split: {fruits}")

joined = " | ".join(fruits)    # join with separator
print(f"Joined: {joined}")

# Split by whitespace (default)
words = "  hello   world  python  ".split()
print(f"Words: {words}")

# --- Stripping and Replacing ---
print("\n=== Strip and Replace ===")
messy = "   lots of spaces   "
print(f"strip():  '{messy.strip()}'")    # remove both ends
print(f"lstrip(): '{messy.lstrip()}'")   # remove left
print(f"rstrip(): '{messy.rstrip()}'")   # remove right

replaced = text.replace("Python", "JavaScript")
print(f"Replace: {replaced}")

# --- Formatting Strings ---
print("\n=== String Formatting ===")
name = "Alice"
age = 30
salary = 75000.50

# f-strings (modern, recommended)
print(f"f-string: {name} is {age} years old, earns ${salary:,.2f}")

# format() method
print("format(): {} is {} years old".format(name, age))

# Padding and alignment
print(f"Right aligned: {name:>15}")       # right-align in 15 chars
print(f"Left aligned:  {name:<15}|")      # left-align in 15 chars
print(f"Center aligned:{name:^15}|")      # center in 15 chars
print(f"Zero-padded:   {42:05d}")         # pad with zeros

# --- Advanced String Operations ---
print("\n=== Advanced ===")
csv_line = "Alice,30,New York,Developer"
name, age, city, role = csv_line.split(",")  # unpack split result
print(f"Unpacked: name={name}, age={age}, city={city}, role={role}")

# Check string type
print(f"'123'.isdigit():  {'123'.isdigit()}")    # all digits?
print(f"'abc'.isalpha():  {'abc'.isalpha()}")    # all letters?
print(f"'Hello'.istitle(): {'Hello'.istitle()}") # title case?

# String multiplication
separator = "=" * 40
print(f"\n{separator}")
print(f"{'CENTERED TITLE':^40}")
print(separator)
