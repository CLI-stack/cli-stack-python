"""
Script: Search Algorithms
What it does: Implements linear search and binary search.
Binary search is much faster than linear search for sorted data.
Understanding this is fundamental to computer science.
"""

import random
import time

# --- Linear Search: check every element ---
def linear_search(arr, target):
    """
    Linear Search: look at each element one by one until found.
    Works on unsorted lists.
    Time complexity: O(n) — checks up to n elements
    """
    for index, element in enumerate(arr):
        if element == target:
            return index    # found! return position
    return -1               # not found

# --- Binary Search: divide and conquer ---
def binary_search(arr, target):
    """
    Binary Search: works on SORTED lists.
    Start at the middle. If target is larger, search right half.
    If smaller, search left half. Repeat until found.
    Time complexity: O(log n) — much faster!
    """
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2       # find middle index

        if arr[mid] == target:
            return mid                # found!
        elif arr[mid] < target:
            low = mid + 1             # target must be in right half
        else:
            high = mid - 1            # target must be in left half

    return -1  # not found

# --- Binary Search (recursive version) ---
def binary_search_recursive(arr, target, low=0, high=None):
    """Recursive version of binary search."""
    if high is None:
        high = len(arr) - 1

    if low > high:
        return -1  # base case: not found

    mid = (low + high) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, high)
    else:
        return binary_search_recursive(arr, target, low, mid - 1)

# --- Demo ---
sorted_list = list(range(0, 1001, 2))  # even numbers 0-1000
target = 742

print(f"List: 0, 2, 4, ..., 1000 ({len(sorted_list)} elements)")
print(f"Searching for: {target}\n")

idx = linear_search(sorted_list, target)
print(f"Linear Search: found at index {idx}")

idx = binary_search(sorted_list, target)
print(f"Binary Search: found at index {idx}")

idx = binary_search_recursive(sorted_list, target)
print(f"Binary (recursive): found at index {idx}")

# Not found case
print(f"\nSearching for 743 (odd number, not in list):")
print(f"Linear: {linear_search(sorted_list, 743)}")
print(f"Binary: {binary_search(sorted_list, 743)}")

# --- Speed comparison ---
print("\n=== Speed Comparison (1,000,000 elements) ===")
big_list = list(range(0, 2000000, 2))   # 1M even numbers
target = 1999998                          # near the end

start = time.time()
linear_search(big_list, target)
linear_time = (time.time() - start) * 1000

start = time.time()
binary_search(big_list, target)
binary_time = (time.time() - start) * 1000

print(f"Linear Search: {linear_time:.2f} ms")
print(f"Binary Search: {binary_time:.4f} ms")
print(f"Binary is ~{linear_time/binary_time:.0f}x faster!")
