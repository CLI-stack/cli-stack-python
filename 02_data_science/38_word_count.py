"""
Script: Word Count and Text Analysis
What it does: Counts words in text, finds the most common words,
and does basic text analysis. A classic beginner data task.
"""

import string  # for punctuation characters
from collections import Counter  # Counter makes counting easy

# Sample text (could also be read from a file)
text = """
Python is a powerful programming language. Python is easy to learn and use.
Python supports multiple programming paradigms. Many developers love Python.
Data science, machine learning, and web development all use Python.
Python has a great community and lots of libraries.
Learning Python opens many career opportunities in software development.
"""

print("=== Original Text ===")
print(text)

# --- Step 1: Clean the text ---
# Convert to lowercase so "Python" and "python" are counted together
text_lower = text.lower()

# Remove punctuation
for char in string.punctuation:
    text_lower = text_lower.replace(char, " ")

# Split into individual words
words = text_lower.split()  # split() breaks on whitespace
print(f"\nTotal words: {len(words)}")

# --- Step 2: Count word frequencies ---
word_counts = Counter(words)  # {word: count, ...}

# --- Step 3: Remove common filler words (stop words) ---
stop_words = {"a", "an", "the", "is", "are", "and", "in", "of", "to",
              "has", "all", "many", "lots", "great", "love"}
filtered = {word: count for word, count in word_counts.items()
            if word not in stop_words}

# --- Step 4: Show results ---
print("\n=== Top 10 Most Common Words ===")
most_common = Counter(filtered).most_common(10)
for word, count in most_common:
    bar = "#" * count  # simple bar chart using characters
    print(f"  {word:<20} {count:>3}  {bar}")

print(f"\nUnique words (excluding stop words): {len(filtered)}")

# --- Step 5: Find sentences containing a keyword ---
keyword = "python"
print(f"\n=== Sentences containing '{keyword}' ===")
sentences = text.strip().split(".")
for sentence in sentences:
    if keyword in sentence.lower():
        print(f"  - {sentence.strip()}")
