"""
Script: Sorting Algorithms
What it does: Implements common sorting algorithms from scratch.
Understanding sorting helps you learn how algorithms work and why
some are faster than others.
"""

import time
import random

# --- Bubble Sort: simple but slow ---
def bubble_sort(arr):
    """
    Bubble Sort: compare adjacent elements, swap if out of order.
    Repeat until no more swaps needed.
    Time complexity: O(n²) — slow for large lists
    """
    arr = arr.copy()  # don't modify the original
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]  # swap
    return arr

# --- Selection Sort: find minimum and place it ---
def selection_sort(arr):
    """
    Selection Sort: find the minimum, put it first.
    Then find the next minimum, put it second. And so on.
    Time complexity: O(n²)
    """
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        min_idx = i  # assume current position is minimum
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j  # found a smaller element
        arr[i], arr[min_idx] = arr[min_idx], arr[i]  # place minimum
    return arr

# --- Insertion Sort: like sorting playing cards ---
def insertion_sort(arr):
    """
    Insertion Sort: take one element at a time and insert it in the right position.
    Like how you sort cards in your hand.
    Time complexity: O(n²) worst case, O(n) best case (already sorted)
    """
    arr = arr.copy()
    for i in range(1, len(arr)):
        key = arr[i]    # element to insert
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]   # shift larger elements right
            j -= 1
        arr[j + 1] = key          # insert key in correct position
    return arr

# --- Merge Sort: divide and conquer ---
def merge_sort(arr):
    """
    Merge Sort: split list in half, sort each half, merge together.
    Much faster than bubble sort for large lists.
    Time complexity: O(n log n)
    """
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])     # sort left half
    right = merge_sort(arr[mid:])    # sort right half
    return merge(left, right)

def merge(left, right):
    """Merge two sorted lists into one sorted list."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# --- Test all algorithms ---
test_data = random.sample(range(1, 101), 20)
print(f"Original: {test_data}")

algorithms = [
    ("Bubble Sort",    bubble_sort),
    ("Selection Sort", selection_sort),
    ("Insertion Sort", insertion_sort),
    ("Merge Sort",     merge_sort),
    ("Python built-in",sorted),
]

print("\n=== Sorting Results ===")
for name, func in algorithms:
    result = func(test_data)
    print(f"  {name:<20}: {result}")

# --- Benchmark ---
print("\n=== Speed Comparison (1000 elements) ===")
big_list = random.sample(range(10000), 1000)
for name, func in algorithms:
    start = time.time()
    func(big_list)
    elapsed = (time.time() - start) * 1000
    print(f"  {name:<20}: {elapsed:.2f} ms")
