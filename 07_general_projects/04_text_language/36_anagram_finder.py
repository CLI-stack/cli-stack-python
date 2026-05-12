"""
Project: Anagram Finder and Word Game Tools
What it does: Finds anagrams, checks if words are anagrams of each other,
and generates anagram groups from a word list.
An anagram is a word formed by rearranging the letters of another word:
  "listen" ↔ "silent"   "race" ↔ "care"   "night" ↔ "thing"

Run: python 36_anagram_finder.py
Run: python 36_anagram_finder.py --check listen silent
Run: python 36_anagram_finder.py --find race
"""

import argparse
from collections import defaultdict


# A large list of common English words (subset for demo)
WORD_LIST = [
    "listen", "silent", "enlist", "inlets", "tinsel",
    "race", "care", "acre", "acer",
    "night", "thing",
    "heart", "earth", "hater", "rathe",
    "stone", "tones", "notes", "senot",
    "evil", "vile", "live", "veil",
    "dormitory", "dirty room",
    "astronomer", "moon starer",
    "the eyes", "they see",
    "python", "typhon",
    "cat", "act",
    "dog", "god",
    "art", "rat", "tar",
    "eat", "tea", "ate", "eta",
    "lamp", "palm",
    "elbow", "below",
    "save", "vase", "aves",
    "secure", "rescue",
    "binary", "brainy",
    "garden", "danger", "ranged", "gander",
    "players", "replays", "parsley",
    "reserved", "reversed",
    "stressed", "desserts",
]


def get_signature(word):
    """
    Get the 'signature' of a word — its letters sorted alphabetically.
    Anagrams have the same signature!
    e.g.: "listen" → "eilnst"
          "silent" → "eilnst"   ← same! they're anagrams
          "enlist" → "eilnst"   ← same!

    We also strip spaces and lowercase to normalize.
    """
    cleaned = word.lower().replace(" ", "")  # remove spaces, lowercase
    return "".join(sorted(cleaned))           # sort letters alphabetically


def is_anagram(word1, word2):
    """Check if two words (or phrases) are anagrams of each other."""
    return get_signature(word1) == get_signature(word2)


def find_anagram_groups(word_list):
    """
    Group all words in the list by their signature.
    Words with the same signature are anagrams of each other.
    Returns only groups with 2+ words (actual anagram groups).
    """
    groups = defaultdict(list)  # sig → [list of words with that sig]

    for word in word_list:
        sig = get_signature(word)
        groups[sig].append(word)

    # Only return groups with more than one word
    return {sig: words for sig, words in groups.items() if len(words) > 1}


def find_anagrams_for(target, word_list):
    """Find all words in the list that are anagrams of the target word."""
    target_sig = get_signature(target)
    return [w for w in word_list if get_signature(w) == target_sig and w.lower() != target.lower()]


def generate_anagrams(word, max_results=20):
    """
    Generate all possible arrangements of letters in a word.
    WARNING: This can be VERY slow for long words (n! permutations).
    "abc" → 6 arrangements   "abcd" → 24   "abcde" → 120
    Only practical for words up to 7-8 letters.
    """
    import itertools

    if len(word) > 8:
        return ["Word too long to generate all permutations (would take too long)"]

    # itertools.permutations() generates all orderings of the letters
    perms   = set("".join(p) for p in itertools.permutations(word.lower()))
    return sorted(list(perms))[:max_results]


def print_groups(groups):
    """Display anagram groups in a formatted table."""
    print(f"\n  Found {len(groups)} anagram group(s):\n")

    for i, (sig, words) in enumerate(sorted(groups.items(), key=lambda x: -len(x[1])), 1):
        # Show the group
        words_str = "  ↔  ".join(words)
        print(f"  {i:>3}. [{sig}]  {words_str}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Anagram finder and word game tools")
parser.add_argument("--check",   nargs="+", help="Check if words are anagrams: --check listen silent")
parser.add_argument("--find",    help="Find anagrams of a word in the word list")
parser.add_argument("--groups",  action="store_true", help="Show all anagram groups")
parser.add_argument("--generate",help="Generate all letter arrangements of a word")
args = parser.parse_args()

print("=== Anagram Finder ===\n")

if args.check:
    # Check if provided words are all anagrams of each other
    words = args.check
    print(f"Checking: {' vs '.join(words)}")
    sigs  = [get_signature(w) for w in words]
    if len(set(sigs)) == 1:
        print(f"✓ YES — they are all anagrams! (signature: {sigs[0]})")
    else:
        print("✗ NO — they are not all anagrams")
        for w, s in zip(words, sigs):
            print(f"  '{w}' → signature: {s}")

elif args.find:
    word     = args.find
    anagrams = find_anagrams_for(word, WORD_LIST)
    print(f"Anagrams of '{word}' in word list:")
    if anagrams:
        for a in anagrams:
            print(f"  {a}")
    else:
        print("  None found in the word list")

elif args.generate:
    word   = args.generate
    perms  = generate_anagrams(word)
    print(f"Letter arrangements of '{word}' ({len(perms)} shown):")
    for perm in perms[:20]:
        print(f"  {perm}")

else:
    # Default: show all anagram groups + some specific examples
    print("=== Classic Anagram Pairs ===\n")
    pairs = [
        ("listen",  "silent"),
        ("heart",   "earth"),
        ("evil",    "vile"),
        ("garden",  "danger"),
        ("binary",  "brainy"),
        ("stressed","desserts"),
    ]
    for w1, w2 in pairs:
        check = "✓ Anagram" if is_anagram(w1, w2) else "✗ Not anagram"
        sig   = get_signature(w1)
        print(f"  {w1:<15} ↔  {w2:<15}  {check}  [sig: {sig}]")

    groups = find_anagram_groups(WORD_LIST)
    print(f"\n=== Anagram Groups from Word List ===")
    print_groups(groups)
