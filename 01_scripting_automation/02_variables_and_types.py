"""
Script: Variables and Data Types
What it does: Shows the basic data types in Python — integers, floats,
strings, and booleans. Every piece of data in Python has a type.
"""

# Integer — whole numbers (no decimal point)
age = 25
print("Age:", age)
print("Type:", type(age))  # type() tells you the data type

# Float — numbers with a decimal point
height = 5.9
print("\nHeight:", height)
print("Type:", type(height))

# String — text enclosed in quotes
name = "Alice"
print("\nName:", name)
print("Type:", type(name))

# Boolean — only True or False
is_student = True
print("\nIs student:", is_student)
print("Type:", type(is_student))

# You can do math with numbers
total = age + 5
print("\nAge in 5 years:", total)

# You can join strings together (called concatenation)
greeting = "Hello, " + name + "!"
print(greeting)
