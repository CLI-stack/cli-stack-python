"""
Project: Palindrome Checker and Finder
What it does: Checks if words/sentences are palindromes and finds
palindromes in a word list. Also generates palindrome statistics.

A palindrome reads the same forwards and backwards:
  Words: "racecar", "level", "radar", "noon", "civic"
  Phrases: "A man a plan a canal Panama"
           "Never odd or even"
           "Was it a car or a cat I saw"

Run: python 39_palindrome_checker.py
Run: python 39_palindrome_checker.py --check "racecar"
Run: python 39_palindrome_checker.py --check "A man a plan a canal Panama"
"""

import re
import argparse


def is_palindrome(text, strict=False):
    """
    Check if a string is a palindrome.

    strict=False: ignore spaces, punctuation, and capitalization
                  (allows checking phrases like "A man a plan a canal Panama")
    strict=True:  exact character matching (character by character)
    """
    if strict:
        # Strict mode: compare exactly as given
        return text == text[::-1]  # [::-1] reverses the string
    else:
        # Lenient mode: clean the text first
        # Keep only lowercase letters (ignore spaces, punctuation, case)
        cleaned = re.sub(r"[^a-zA-Z0-9]", "", text.lower())

        # Compare cleaned string to its reverse
        return cleaned == cleaned[::-1]


def find_palindromes_in_list(word_list, min_length=3):
    """
    Find all palindromes in a list of words.
    min_length: only find palindromes of at least this many characters.
    """
    return [word for word in word_list
            if len(word) >= min_length and is_palindrome(word, strict=True)]


def longest_palindrome_substring(text):
    """
    Find the longest palindrome substring within a larger string.
    Uses the 'expand around center' algorithm.

    Algorithm idea:
      - For each character in the string, try to expand outward
      - Keep expanding as long as the substring remains a palindrome
      - Track the longest one found

    Time complexity: O(n²) — acceptable for reasonable string lengths
    """
    if not text:
        return ""

    text    = text.lower()
    start   = 0   # start index of the longest palindrome found
    max_len = 1   # length of the longest palindrome found

    def expand(left, right):
        """Expand outward from center while palindrome holds."""
        nonlocal start, max_len
        while left >= 0 and right < len(text) and text[left] == text[right]:
            current_len = right - left + 1
            if current_len > max_len:
                max_len = current_len
                start   = left
            left  -= 1  # expand leftward
            right += 1  # expand rightward

    for i in range(len(text)):
        expand(i, i)       # odd-length palindromes (center = single char)
        expand(i, i + 1)   # even-length palindromes (center = between two chars)

    return text[start:start + max_len]


def generate_palindrome_numbers(limit=200):
    """Find all palindrome numbers up to 'limit'."""
    return [n for n in range(1, limit + 1) if str(n) == str(n)[::-1]]


# Sample word list to search for palindromes
WORD_LIST = [
    "racecar", "level", "radar", "noon", "civic", "refer", "madam",
    "rotor", "kayak", "stats", "tenet", "deified", "rotator", "repaper",
    "python", "programming", "hello", "world", "data", "science",
    "bib", "bob", "deed", "did", "dud", "ewe", "eye", "gag",
    "gig", "pup", "pep", "pop", "sis", "wow", "tit", "nun",
    "aha", "eke", "ele", "ere", "eve", "gag",
]

PALINDROME_PHRASES = [
    "A man a plan a canal Panama",
    "Never odd or even",
    "Was it a car or a cat I saw",
    "Do geese see God",
    "A Santa at NASA",
    "No lemon no melon",
    "Mr Owl ate my metal worm",
    "Race fast safe car",
]


def print_report():
    """Show a comprehensive palindrome demonstration."""
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    # Check individual words
    print("=== Word Palindromes ===\n")
    test_words = ["racecar", "python", "level", "hello", "radar", "world",
                  "madam", "deified", "rotator", "kayak", "banana"]

    for word in test_words:
        result = is_palindrome(word, strict=True)
        color  = GREEN if result else RED
        icon   = "✓" if result else "✗"
        rev    = word[::-1]
        print(f"  {color}{icon}{RST} {word:<12}  reverse: {rev:<12}  "
              f"{'PALINDROME' if result else 'not palindrome'}")

    # Check phrases
    print("\n=== Phrase Palindromes (ignoring spaces/punctuation) ===\n")
    for phrase in PALINDROME_PHRASES:
        result  = is_palindrome(phrase)
        color   = GREEN if result else RED
        cleaned = re.sub(r"[^a-zA-Z]", "", phrase.lower())
        print(f"  {color}{'✓' if result else '✗'}{RST} '{phrase}'")
        print(f"    Cleaned: {cleaned}")
        print()

    # Find palindromes in word list
    found = find_palindromes_in_list(WORD_LIST)
    print(f"=== Palindromes in Word List ({len(found)} found) ===\n")
    found.sort(key=len, reverse=True)
    for w in found:
        print(f"  {w}")

    # Longest palindrome substring
    print(f"\n=== Longest Palindrome in a String ===\n")
    test_strings = [
        "babad",
        "racecar is a palindrome",
        "abcba12321xyz",
        "the level of the racecar radar",
    ]
    for s in test_strings:
        longest = longest_palindrome_substring(s)
        print(f"  In: '{s}'")
        print(f"  Longest palindrome: '{longest}' (length {len(longest)})\n")

    # Palindrome numbers
    pal_nums = generate_palindrome_numbers(200)
    print(f"=== Palindrome Numbers (1-200): {len(pal_nums)} found ===\n")
    print("  " + "  ".join(str(n) for n in pal_nums))


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Check and find palindromes")
parser.add_argument("--check",  help="Check if a word or phrase is a palindrome")
parser.add_argument("--strict", action="store_true",
                    help="Strict mode (exact matching, no normalization)")
args = parser.parse_args()

print("=== Palindrome Checker ===\n")

if args.check:
    text   = args.check
    result = is_palindrome(text, strict=args.strict)
    mode   = "strict" if args.strict else "lenient (ignores spaces/case)"
    print(f"Text    : '{text}'")
    print(f"Mode    : {mode}")
    print(f"Reversed: '{text[::-1]}'")
    print(f"Result  : {'✓ PALINDROME' if result else '✗ NOT a palindrome'}")
else:
    print_report()
