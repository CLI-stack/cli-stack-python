"""
Script: Simple CLI with input()
What it does: Creates an interactive command-line program using Python's
built-in input() function to get text from the user.
No extra libraries needed — just pure Python.
"""

print("=" * 40)
print("    Welcome to the Simple CLI App")
print("=" * 40)

# --- Basic input ---
name = input("\nWhat is your name? ").strip()  # strip() removes extra spaces
print(f"Hello, {name}!")

# --- Get a number and convert it ---
while True:
    try:
        age_str = input("What is your age? ")
        age = int(age_str)  # convert string to integer
        break  # exit the loop if conversion worked
    except ValueError:
        print("  Please enter a valid number.")

print(f"In 10 years, you will be {age + 10} years old.")

# --- Yes/No prompt ---
def ask_yes_no(prompt):
    """Ask a yes/no question and return True/False."""
    while True:
        answer = input(f"{prompt} (yes/no): ").strip().lower()
        if answer in ["yes", "y"]:
            return True
        elif answer in ["no", "n"]:
            return False
        else:
            print("  Please answer 'yes' or 'no'.")

likes_python = ask_yes_no("\nDo you like Python?")
if likes_python:
    print("Great choice! Python is awesome.")
else:
    print("Give it time — Python grows on you!")

# --- Multiple choice menu ---
print("\n=== What would you like to learn next? ===")
options = ["Data Science", "Web Development", "CLI Tools", "Scientific Computing"]
for i, option in enumerate(options, 1):
    print(f"  {i}. {option}")

while True:
    try:
        choice = int(input("Enter number (1-4): "))
        if 1 <= choice <= 4:
            break
        print("  Choose between 1 and 4.")
    except ValueError:
        print("  Please enter a number.")

print(f"\nExcellent! You chose: {options[choice - 1]}")
print("Happy learning!")
