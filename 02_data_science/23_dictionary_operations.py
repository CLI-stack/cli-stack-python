"""
Script: Dictionary Operations
What it does: Shows how to work with Python dictionaries.
A dictionary stores key-value pairs — like a real dictionary where
you look up a word (key) to get its definition (value).
"""

# --- Creating a dictionary ---
person = {
    "name": "Alice",
    "age": 30,
    "city": "New York",
    "hobbies": ["reading", "coding", "hiking"]
}

print("Person:", person)

# --- Accessing values ---
print("\n=== Accessing Values ===")
print("Name:", person["name"])            # access by key
print("Age:", person.get("age"))          # .get() is safer (no error if missing)
print("Email:", person.get("email", "Not provided"))  # default value if missing

# --- Modifying values ---
person["age"] = 31                        # update existing key
person["email"] = "alice@example.com"    # add new key
print("\nUpdated person:", person)

# --- Removing items ---
removed = person.pop("hobbies")           # remove and return value
print("Removed hobbies:", removed)
del person["email"]                       # delete a key
print("After removals:", person)

# --- Iterating through a dictionary ---
student_grades = {"Math": 90, "English": 85, "Science": 92, "History": 78}

print("\n=== Student Grades ===")
for subject, grade in student_grades.items():  # .items() gives key-value pairs
    print(f"  {subject}: {grade}")

print("\nSubjects:", list(student_grades.keys()))    # just keys
print("Grades:", list(student_grades.values()))     # just values

# --- Nested dictionaries ---
employees = {
    "E001": {"name": "Bob", "role": "Developer", "salary": 75000},
    "E002": {"name": "Carol", "role": "Designer", "salary": 68000},
}

print("\n=== Employees ===")
for emp_id, info in employees.items():
    print(f"  {emp_id}: {info['name']} ({info['role']}) - ${info['salary']}")

# --- Dictionary comprehension ---
squared = {x: x**2 for x in range(1, 6)}  # {1:1, 2:4, 3:9, 4:16, 5:25}
print("\nSquared dict:", squared)
