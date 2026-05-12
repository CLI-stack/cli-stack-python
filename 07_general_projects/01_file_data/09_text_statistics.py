"""
Project: Text Statistics and Readability Analyzer
What it does: Analyzes a piece of text and computes various statistics:
  - Word/sentence/paragraph counts
  - Average word and sentence length
  - Flesch Reading Ease score (how easy text is to read)
  - Most common words (excluding stop words)
  - Estimated reading time

The Flesch Reading Ease formula:
  206.835 − 1.015 × (words/sentences) − 84.6 × (syllables/words)
  Score 90-100: Very Easy   (children's books)
  Score 60-70:  Standard    (newspapers)
  Score 0-30:   Very Hard   (academic journals)

Run: python 09_text_statistics.py
Run: python 09_text_statistics.py --file mytext.txt
"""

import re
import argparse
import os
from collections import Counter

SAMPLE_TEXT = """
Python is a high-level, interpreted programming language known for its simplicity
and readability. Created by Guido van Rossum and first released in 1991, Python
has grown to become one of the most popular programming languages in the world.

The language emphasizes code readability and allows programmers to express concepts
in fewer lines of code compared to languages like C++ or Java. Python supports
multiple programming paradigms, including procedural, object-oriented, and
functional programming.

Python's comprehensive standard library and large ecosystem of third-party packages
make it suitable for a wide variety of applications. Data scientists use libraries
like NumPy, Pandas, and Matplotlib for analysis and visualization. Web developers
use frameworks like Django and Flask to build web applications.

One of Python's greatest strengths is its community. The Python community is known
for being welcoming, inclusive, and helpful. There are thousands of tutorials,
courses, and books available for learners at every level.
"""

# Common English words that carry little meaning (called "stop words")
# We exclude these when counting significant word frequencies
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "that", "this", "it", "its", "as", "not",
    "than", "like", "about", "their", "they", "we", "i", "you", "he", "she",
}


def count_syllables(word):
    """
    Estimate the number of syllables in a word.
    This uses a simplified algorithm — not perfect but good enough for readability scoring.

    Rules: count vowel groups, subtract silent 'e' at the end, minimum 1 syllable.
    """
    word = word.lower().strip(".,!?;:-")  # remove punctuation

    # Count groups of consecutive vowels (each group ≈ one syllable)
    vowels  = "aeiouy"
    count   = 0
    prev_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            count += 1   # new vowel group starts
        prev_was_vowel = is_vowel

    # Silent 'e' at the end of a word doesn't count as a syllable
    if word.endswith("e") and count > 1:
        count -= 1

    return max(1, count)  # every word has at least 1 syllable


def analyze_text(text):
    """Compute all statistics for the given text."""

    # ── Tokenize ──────────────────────────────────────────────────────────────
    # Split into words (keep only alphabetic characters)
    words = re.findall(r"\b[a-zA-Z]+\b", text)

    # Split into sentences (end at . ! ?)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]  # remove empty

    # Split into paragraphs (separated by blank lines)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # ── Basic counts ──────────────────────────────────────────────────────────
    word_count      = len(words)
    sentence_count  = max(len(sentences), 1)  # avoid division by zero
    paragraph_count = len(paragraphs)
    char_count      = len(text)
    char_no_spaces  = len(text.replace(" ", "").replace("\n", ""))

    # ── Averages ──────────────────────────────────────────────────────────────
    avg_word_length = sum(len(w) for w in words) / word_count if words else 0
    avg_words_per_sentence = word_count / sentence_count

    # ── Syllable count (for Flesch score) ────────────────────────────────────
    total_syllables = sum(count_syllables(w) for w in words)

    # ── Flesch Reading Ease score ─────────────────────────────────────────────
    # Higher score = easier to read
    if word_count > 0 and sentence_count > 0:
        flesch = (206.835
                  - 1.015 * (word_count / sentence_count)
                  - 84.6  * (total_syllables / word_count))
        flesch = max(0, min(100, flesch))  # clamp to 0-100 range
    else:
        flesch = 0

    # Interpret the Flesch score
    if flesch >= 90:   readability = "Very Easy (children's book)"
    elif flesch >= 70: readability = "Easy (conversational)"
    elif flesch >= 60: readability = "Standard (newspaper)"
    elif flesch >= 50: readability = "Fairly Difficult"
    elif flesch >= 30: readability = "Difficult (academic)"
    else:              readability = "Very Difficult (specialized)"

    # ── Word frequency (excluding stop words) ─────────────────────────────────
    meaningful_words = [w.lower() for w in words if w.lower() not in STOP_WORDS]
    word_freq        = Counter(meaningful_words)

    # ── Reading time estimate ──────────────────────────────────────────────────
    # Average adult reads about 200-250 words per minute
    reading_time_min = word_count / 225
    reading_time_sec = reading_time_min * 60

    return {
        "words":           word_count,
        "sentences":       sentence_count,
        "paragraphs":      paragraph_count,
        "characters":      char_count,
        "chars_no_spaces": char_no_spaces,
        "avg_word_len":    avg_word_length,
        "avg_words_sent":  avg_words_per_sentence,
        "syllables":       total_syllables,
        "flesch_score":    flesch,
        "readability":     readability,
        "reading_time":    reading_time_sec,
        "top_words":       word_freq.most_common(10),
    }


def print_report(stats):
    """Display analysis results in a formatted report."""
    print("=" * 55)
    print("  TEXT STATISTICS REPORT")
    print("=" * 55)

    print("\n  Basic Counts:")
    print(f"    Words            : {stats['words']:,}")
    print(f"    Sentences        : {stats['sentences']:,}")
    print(f"    Paragraphs       : {stats['paragraphs']:,}")
    print(f"    Characters       : {stats['characters']:,}")
    print(f"    Chars (no spaces): {stats['chars_no_spaces']:,}")

    print("\n  Complexity:")
    print(f"    Avg word length  : {stats['avg_word_len']:.2f} chars")
    print(f"    Avg words/sentence: {stats['avg_words_sent']:.1f}")
    print(f"    Total syllables  : {stats['syllables']:,}")

    print(f"\n  Readability (Flesch):")
    print(f"    Score     : {stats['flesch_score']:.1f} / 100")
    print(f"    Level     : {stats['readability']}")

    # Visual bar for the score
    bar_len = int(stats["flesch_score"] / 100 * 40)
    bar     = "█" * bar_len + "░" * (40 - bar_len)
    print(f"    [{bar}]")

    rt = stats["reading_time"]
    print(f"\n  Estimated Reading Time:")
    if rt < 60:
        print(f"    {rt:.0f} seconds")
    else:
        print(f"    {rt/60:.1f} minutes")

    print(f"\n  Top 10 Words (excluding common words):")
    for word, count in stats["top_words"]:
        bar = "█" * min(count, 20)
        print(f"    {word:<20} {count:>3}  {bar}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Analyze text statistics and readability")
parser.add_argument("--file", help="Text file to analyze (default: uses sample)")
args = parser.parse_args()

print("=== Text Statistics Analyzer ===\n")

if args.file and os.path.exists(args.file):
    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"Analyzing: {args.file}\n")
else:
    print("No file given — using built-in sample text.\n")
    text = SAMPLE_TEXT

stats = analyze_text(text)
print_report(stats)
