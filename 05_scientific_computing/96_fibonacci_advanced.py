"""
Script: Fibonacci Sequence — Multiple Approaches
What it does: Shows 5 different ways to generate Fibonacci numbers,
comparing their speed and memory usage.
Great for understanding algorithms, recursion, and generators.
"""

import time

# --- Method 1: Simple recursion (slow) ---
def fib_recursive(n):
    """Simple recursion — elegant but very slow for large n."""
    if n <= 1:
        return n
    return fib_recursive(n-1) + fib_recursive(n-2)

# --- Method 2: Memoization (fast recursion) ---
def fib_memo(n, cache={}):
    """Recursion with caching — much faster."""
    if n in cache:
        return cache[n]
    if n <= 1:
        return n
    cache[n] = fib_memo(n-1) + fib_memo(n-2)
    return cache[n]

# --- Method 3: Iterative (fast, O(n) time, O(1) space) ---
def fib_iterative(n):
    """Iterative approach — fast and memory efficient."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b   # move the window forward
    return b

# --- Method 4: Generator (memory efficient for sequences) ---
def fib_generator(count):
    """Generator yields Fibonacci numbers one at a time."""
    a, b = 0, 1
    for _ in range(count):
        yield a           # yield means: return this value, then resume
        a, b = b, a + b

# --- Method 5: Matrix exponentiation (very fast for huge n) ---
def fib_matrix(n):
    """Uses matrix power — O(log n) time complexity."""
    def matrix_mult(A, B):
        return [
            [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
            [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]
        ]

    def matrix_pow(M, power):
        result = [[1, 0], [0, 1]]  # identity matrix
        while power > 0:
            if power % 2 == 1:
                result = matrix_mult(result, M)
            M = matrix_mult(M, M)
            power //= 2
        return result

    if n == 0:
        return 0
    base = [[1, 1], [1, 0]]
    return matrix_pow(base, n)[0][1]

# --- Display first 15 Fibonacci numbers ---
print("=== First 15 Fibonacci Numbers ===")
fib15 = list(fib_generator(15))
print(fib15)

# --- Compare all methods for n=30 ---
n = 30
print(f"\n=== All Methods: F({n}) ===")
methods = [
    ("Recursive",    lambda: fib_recursive(n)),
    ("Memoized",     lambda: fib_memo(n)),
    ("Iterative",    lambda: fib_iterative(n)),
    ("Matrix",       lambda: fib_matrix(n)),
]

for name, func in methods:
    start = time.time()
    result = func()
    elapsed = (time.time() - start) * 1000
    print(f"  {name:<15}: F({n}) = {result:>8,}  ({elapsed:.3f} ms)")

# --- Speed test for large n ---
print(f"\n=== Speed Test: F(40) ===")
for name, func in methods[1:]:  # skip slow recursive for n=40
    func()  # warm up cache
    start = time.time()
    result = func()
    elapsed = (time.time() - start) * 1000
    print(f"  {name:<15}: {result:>12,}  ({elapsed:.4f} ms)")
