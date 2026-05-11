"""
Script: Word Counter CLI
What it does: Counts words, characters, lines, and sentences in a file or text.
Similar to the 'wc' command on Linux.

Run: python 68_word_counter.py --text "Hello world!"
Run: python 68_word_counter.py --file myfile.txt
"""

import argparse
import os
import re

def count_text(text):
    """Count various statistics about the given text."""
    lines = text.split("\n")
    words = text.split()
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", "").replace("\n", ""))
    sentences = len(re.findall(r"[.!?]+", text))
    paragraphs = len([p for p in text.split("\n\n") if p.strip()])

    return {
        "lines": len(lines),
        "words": len(words),
        "sentences": sentences,
        "paragraphs": paragraphs,
        "characters": chars,
        "chars_no_spaces": chars_no_spaces,
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "avg_words_per_sentence": len(words) / sentences if sentences else 0,
    }

def display_stats(stats, source_name="Input"):
    """Print statistics in a formatted table."""
    print(f"\n=== Statistics for: {source_name} ===")
    print(f"  Lines:               {stats['lines']:>8}")
    print(f"  Words:               {stats['words']:>8}")
    print(f"  Sentences:           {stats['sentences']:>8}")
    print(f"  Paragraphs:          {stats['paragraphs']:>8}")
    print(f"  Characters:          {stats['characters']:>8}")
    print(f"  Characters (no spc): {stats['chars_no_spaces']:>8}")
    print(f"  Avg word length:     {stats['avg_word_length']:>8.2f} chars")
    print(f"  Avg words/sentence:  {stats['avg_words_per_sentence']:>8.1f}")

# --- Parse arguments ---
parser = argparse.ArgumentParser(description="Count words, lines, and characters")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--text", help="Count stats for given text")
group.add_argument("--file", help="Count stats for a file")
args = parser.parse_args()

if args.text:
    stats = count_text(args.text)
    display_stats(stats, "provided text")

elif args.file:
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
    else:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
        stats = count_text(content)
        file_size = os.path.getsize(args.file)
        display_stats(stats, args.file)
        print(f"  File size:           {file_size:>8} bytes")
