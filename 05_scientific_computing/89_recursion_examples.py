"""
Script: Recursion Examples
What it does: Demonstrates recursion — a function that calls itself.
Recursion is a powerful technique for problems that can be broken
into smaller versions of the same problem.
"""

import sys

# --- Example 1: Countdown ---
def countdown(n):
    """Count down from n to 0 using recursion."""
    if n <= 0:
        print("Go!")
        return        # base case — stop recursion
    print(n)
    countdown(n - 1)  # recursive call with smaller problem

print("=== Countdown ===")
countdown(5)

# --- Example 2: Factorial ---
def factorial(n):
    """
    Calculate n! = n × (n-1) × (n-2) × ... × 1
    Example: 5! = 5 × 4 × 3 × 2 × 1 = 120
    Base case: 0! = 1
    """
    if n <= 1:
        return 1                   # base case
    return n * factorial(n - 1)   # recursive: n! = n × (n-1)!

print("\n=== Factorial ===")
for i in range(8):
    print(f"  {i}! = {factorial(i)}")

# --- Example 3: Fibonacci ---
def fibonacci(n):
    """
    Fibonacci: each number is the sum of the previous two.
    F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)
    Sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21...
    """
    if n <= 1:
        return n               # base cases
    return fibonacci(n-1) + fibonacci(n-2)

print("\n=== Fibonacci Sequence ===")
fib_sequence = [fibonacci(i) for i in range(12)]
print("  F(0) to F(11):", fib_sequence)

# --- Fibonacci with memoization (much faster) ---
memo = {}
def fibonacci_memo(n):
    """Fibonacci with memoization — stores results to avoid recalculation."""
    if n in memo:
        return memo[n]   # return cached result
    if n <= 1:
        return n
    memo[n] = fibonacci_memo(n-1) + fibonacci_memo(n-2)
    return memo[n]

print(f"  F(35) = {fibonacci_memo(35)} (fast with memoization)")

# --- Example 4: Sum of a list ---
def recursive_sum(numbers):
    """Sum a list using recursion (instead of sum() or a loop)."""
    if len(numbers) == 0:
        return 0                                    # base case: empty list
    return numbers[0] + recursive_sum(numbers[1:])  # head + sum of tail

print("\n=== Recursive Sum ===")
numbers = [1, 2, 3, 4, 5]
print(f"  Sum of {numbers} = {recursive_sum(numbers)}")

# --- Example 5: Flatten nested list ---
def flatten(nested):
    """Flatten a nested list into a single list."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))  # recursively flatten sublists
        else:
            result.append(item)
    return result

print("\n=== Flatten Nested List ===")
nested = [1, [2, 3], [4, [5, 6]], [7, [8, [9]]]]
print(f"  Input:  {nested}")
print(f"  Output: {flatten(nested)}")
