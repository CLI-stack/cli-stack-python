"""
Script: Basic Statistics
What it does: Calculates common statistics — mean, median, mode, min, max, range.
Uses only Python's built-in statistics module, no extra installs needed.
"""

import statistics  # built-in module for statistical calculations

# Sample dataset — exam scores of 10 students
scores = [72, 85, 90, 60, 78, 95, 85, 70, 88, 65]

print("=== Student Exam Scores ===")
print(f"Data: {scores}\n")

# Mean = average (sum of all values divided by count)
mean = statistics.mean(scores)
print(f"Mean (Average):  {mean}")

# Median = middle value when sorted
median = statistics.median(scores)
print(f"Median (Middle): {median}")

# Mode = most frequently occurring value
mode = statistics.mode(scores)
print(f"Mode (Most common): {mode}")

# Min and Max
print(f"Minimum score: {min(scores)}")
print(f"Maximum score: {max(scores)}")

# Range = max - min
score_range = max(scores) - min(scores)
print(f"Range: {score_range}")

# Standard deviation = how spread out the values are
# Low std dev = scores clustered together, high = widely spread
std_dev = statistics.stdev(scores)
print(f"Standard Deviation: {std_dev:.2f}")

# Variance = square of standard deviation
variance = statistics.variance(scores)
print(f"Variance: {variance:.2f}")

# Manual mean calculation (to understand what's happening)
manual_mean = sum(scores) / len(scores)
print(f"\nManual mean check: {manual_mean:.2f}")

# Sort and show percentiles manually
sorted_scores = sorted(scores)
print(f"\nSorted scores: {sorted_scores}")
print(f"25th percentile (Q1): {sorted_scores[len(sorted_scores)//4]}")
print(f"75th percentile (Q3): {sorted_scores[3*len(sorted_scores)//4]}")
