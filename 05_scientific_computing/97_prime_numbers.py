"""
Script: Prime Numbers
What it does: Finds and checks prime numbers using different algorithms.
Prime numbers are the building blocks of all numbers,
and are fundamental to cryptography (RSA encryption).
"""

import time
import math

# --- Check if a number is prime ---
def is_prime_basic(n):
    """Basic prime check: try dividing by all numbers up to n."""
    if n < 2:
        return False
    for i in range(2, n):  # check all divisors
        if n % i == 0:
            return False   # divisible → not prime
    return True

def is_prime_optimized(n):
    """
    Optimized prime check: only check up to √n.
    If n has a factor > √n, it must also have one < √n.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False           # even numbers > 2 are not prime
    for i in range(3, int(math.sqrt(n)) + 1, 2):  # only odd numbers
        if n % i == 0:
            return False
    return True

# --- Sieve of Eratosthenes: find ALL primes up to N ---
def sieve_of_eratosthenes(limit):
    """
    The Sieve is an ancient algorithm (200 BC) for finding all primes.
    Start with all numbers, cross out multiples of each prime.
    """
    is_prime = [True] * (limit + 1)  # assume all are prime initially
    is_prime[0] = is_prime[1] = False # 0 and 1 are not prime

    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            # Cross out all multiples of i starting from i²
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False

    return [i for i in range(limit + 1) if is_prime[i]]

# --- Demo ---
print("=== Checking Individual Numbers ===")
test_numbers = [1, 2, 3, 4, 17, 100, 97, 1000, 999983]
for n in test_numbers:
    result = is_prime_optimized(n)
    print(f"  {n:>8,} is {'prime ✓' if result else 'NOT prime ✗'}")

print("\n=== Primes up to 100 (Sieve) ===")
primes_100 = sieve_of_eratosthenes(100)
print(f"Found {len(primes_100)} primes: {primes_100}")

print("\n=== Primes up to 1,000 ===")
primes_1000 = sieve_of_eratosthenes(1000)
print(f"Count: {len(primes_1000)}")
print(f"Largest: {primes_1000[-1]}")
print(f"Sum: {sum(primes_1000):,}")

# --- Prime factorization ---
def prime_factors(n):
    """Find all prime factors of n."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

print("\n=== Prime Factorization ===")
for n in [12, 100, 360, 1024, 9999]:
    factors = prime_factors(n)
    print(f"  {n:>6} = {' × '.join(map(str, factors))}")

# --- Speed comparison ---
print("\n=== Speed: is_prime(999983) ===")
n = 999983
start = time.time()
is_prime_basic(n)
print(f"  Basic:     {(time.time()-start)*1000:.2f} ms")

start = time.time()
is_prime_optimized(n)
print(f"  Optimized: {(time.time()-start)*1000:.2f} ms")
