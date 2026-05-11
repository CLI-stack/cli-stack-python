"""
Script: Python Math Module
What it does: Demonstrates Python's built-in math functions.
The math module gives you access to mathematical functions like
square root, logarithm, trigonometry, and constants like pi.

No extra install needed — math is built into Python.
"""

import math  # built-in math module

print("=== Math Constants ===")
print(f"π (pi):     {math.pi}")       # 3.14159...
print(f"e:          {math.e}")        # Euler's number 2.71828...
print(f"tau (2π):   {math.tau}")      # 6.28318...
print(f"Infinity:   {math.inf}")      # positive infinity

print("\n=== Rounding ===")
x = 3.7
print(f"Number: {x}")
print(f"floor({x}): {math.floor(x)}")   # round DOWN → 3
print(f"ceil({x}):  {math.ceil(x)}")    # round UP → 4
print(f"round({x}): {round(x)}")        # standard rounding → 4
print(f"trunc({x}): {math.trunc(x)}")   # remove decimal → 3

print("\n=== Powers and Roots ===")
print(f"sqrt(16):   {math.sqrt(16)}")   # square root = 4
print(f"2^10:       {math.pow(2, 10):.0f}") # 2 to the power 10 = 1024
print(f"cbrt(27):   {27 ** (1/3):.4f}") # cube root (x^(1/3))
print(f"abs(-5):    {abs(-5)}")          # absolute value

print("\n=== Logarithms ===")
print(f"log(e):     {math.log(math.e):.4f}")   # natural log, should be 1
print(f"log10(100): {math.log10(100)}")         # log base 10 = 2
print(f"log2(8):    {math.log2(8)}")            # log base 2 = 3

print("\n=== Trigonometry (input in radians) ===")
angle_degrees = 45
angle_radians = math.radians(angle_degrees)  # convert degrees to radians
print(f"sin(45°): {math.sin(angle_radians):.4f}")
print(f"cos(45°): {math.cos(angle_radians):.4f}")
print(f"tan(45°): {math.tan(angle_radians):.4f}")

# Convert radians back to degrees
print(f"\n90 radians in degrees: {math.degrees(math.pi/2):.1f}°")

print("\n=== Factorials and Combinations ===")
print(f"5! (factorial): {math.factorial(5)}")    # 5! = 120
print(f"C(10,3):        {math.comb(10, 3)}")     # combinations
print(f"P(5,2):         {math.perm(5, 2)}")      # permutations
