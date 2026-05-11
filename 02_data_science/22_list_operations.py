"""
Script: List Operations
What it does: Demonstrates common operations with Python lists.
Lists are one of the most important data structures in Python.
Think of a list as a collection of items in a specific order.
"""

# --- Creating lists ---
fruits = ["apple", "banana", "cherry", "date", "elderberry"]
numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
mixed = [1, "hello", True, 3.14, None]  # lists can mix different types

print("Fruits list:", fruits)
print("Numbers list:", numbers)

# --- Accessing items (indexing starts at 0!) ---
print("\n=== Accessing Items ===")
print("First item:  ", fruits[0])    # index 0 = first
print("Last item:   ", fruits[-1])   # negative index = from the end
print("Second item: ", fruits[1])

# --- Slicing: get a portion of the list ---
print("\n=== Slicing ===")
print("First 3:  ", fruits[:3])      # from start to index 3 (not included)
print("Last 2:   ", fruits[-2:])     # last 2 items
print("Middle:   ", fruits[1:4])     # index 1 to 3

# --- Adding items ---
fruits.append("fig")                 # add to the end
fruits.insert(1, "avocado")          # insert at specific position
print("\nAfter adding:", fruits)

# --- Removing items ---
fruits.remove("banana")              # remove by value
popped = fruits.pop()                # remove and return last item
print("After removing:", fruits)
print("Popped item:", popped)

# --- Sorting ---
numbers_sorted = sorted(numbers)     # returns a new sorted list
print("\nOriginal:", numbers)
print("Sorted:  ", numbers_sorted)
print("Reversed:", sorted(numbers, reverse=True))

# --- Useful list operations ---
print("\n=== Useful Operations ===")
print("Length:", len(fruits))
print("Count of 'apple':", fruits.count("apple"))
print("Index of 'cherry':", fruits.index("cherry"))
print("Is 'apple' in list?", "apple" in fruits)

# --- List comprehension (compact way to create lists) ---
squares = [x**2 for x in range(1, 6)]  # [1², 2², 3², 4², 5²]
print("\nSquares:", squares)

evens = [x for x in numbers if x % 2 == 0]  # filter even numbers
print("Even numbers:", evens)
