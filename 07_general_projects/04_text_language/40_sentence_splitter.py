"""
Project: Sentence Splitter and Text Tokenizer
What it does: Splits text into sentences, words, and tokens.
Text tokenization is the first step in most NLP (Natural Language Processing) pipelines.
Also handles tricky cases like abbreviations (Dr., Mr., vs.) and decimals (3.14).

Run: python 40_sentence_splitter.py
Run: python 40_sentence_splitter.py --file mytext.txt
"""

import re
import os
import argparse
from collections import Counter


SAMPLE_TEXT = """
Dr. Smith visited the lab at 9:00 a.m. on Monday. He was working on a new project.
The project, called Project X v2.0, aims to improve accuracy by 15.7%. It costs $1,200.50.
"This is exciting," said Dr. Smith. "We've never seen results like this before!"

Prof. Johnson (from the U.S.A.) reviewed the report. She found 3 issues on p. 12.
Issue no. 1: The data was collected incorrectly. Issue no. 2: The analysis was incomplete.
However, issues no. 3 was minor. The conclusion was clear: the project was a success.

Python is great! Have you tried it? I think you should. It's very powerful.
"""

# Abbreviations that are followed by a period but don't end a sentence
ABBREVIATIONS = {
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "st", "ave", "blvd",
    "vs", "etc", "fig", "no", "pp", "vol", "dept", "div", "approx",
    "inc", "corp", "ltd", "co", "est", "govt",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "u.s.a", "u.s", "e.g", "i.e", "p", "pp",
}


def split_sentences(text):
    """
    Split text into sentences using a rule-based approach.
    Handles tricky cases:
    - Abbreviations: Dr. Smith → not a sentence boundary
    - Decimal numbers: 3.14, $1,200.50 → not a sentence boundary
    - Quoted speech: ends with ." or !"
    - Multiple punctuation: !!! or ...
    """
    # Protect abbreviations by replacing their periods temporarily
    # We use a placeholder that won't be confused with sentence endings
    protected = text

    # Protect common abbreviations: "Dr." → "Dr<PERIOD>"
    for abbrev in ABBREVIATIONS:
        # Match the abbreviation followed by a period (case-insensitive)
        pattern = re.compile(r"\b(" + re.escape(abbrev) + r")\.", re.IGNORECASE)
        protected = pattern.sub(r"\1<PERIOD>", protected)

    # Protect decimal numbers: "3.14" → "3<PERIOD>14"
    protected = re.sub(r"(\d+)\.(\d+)", r"\1<PERIOD>\2", protected)

    # Protect time formats: "9:00" → stays as is, "a.m." → "a<PERIOD>m<PERIOD>"
    protected = re.sub(r"\b(a|p)\.(m)\.?", r"\1<PERIOD>\2<PERIOD>", protected, flags=re.IGNORECASE)

    # Now split on sentence-ending punctuation (. ! ?) followed by whitespace/end
    # The (?<=[.!?]) is a lookbehind — splits AFTER the punctuation, not before
    sentences = re.split(r"(?<=[.!?])\s+", protected)

    # Restore protected periods
    sentences = [s.replace("<PERIOD>", ".").strip() for s in sentences]

    # Filter out empty sentences
    return [s for s in sentences if s]


def tokenize_words(text):
    """
    Split text into individual tokens (words, numbers, punctuation).
    Returns a list of token strings.
    """
    # Match: words (including apostrophes for contractions), numbers, punctuation
    tokens = re.findall(r"\b\w+'\w+|\b\w+\b|[.,!?;:]", text)
    return tokens


def tokenize_by_type(text):
    """
    Classify each token by type: word, number, punctuation, or other.
    Returns a list of (token, type) tuples.
    """
    token_patterns = [
        ("NUMBER",      r"\b\d+(?:\.\d+)?\b"),         # integers and decimals
        ("WORD",        r"\b[a-zA-Z]+(?:\'[a-z]+)?\b"),# words (including contractions)
        ("PUNCTUATION", r"[.,!?;:\-()\"']"),             # punctuation marks
        ("CURRENCY",    r"\$\d+(?:\.\d+)?"),             # dollar amounts
        ("EMAIL",       r"\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b"),
        ("URL",         r"https?://\S+"),
    ]

    tokens = []
    remaining = text

    while remaining:
        matched = False
        for token_type, pattern in token_patterns:
            m = re.match(pattern, remaining)
            if m:
                tokens.append((m.group(), token_type))
                remaining = remaining[m.end():]
                matched = True
                break

        if not matched:
            # Skip unrecognized characters
            remaining = remaining[1:]

    return tokens


def print_analysis(text):
    """Display full text tokenization analysis."""
    print("=" * 60)
    print("  TEXT TOKENIZATION ANALYSIS")
    print("=" * 60)

    # Sentence splitting
    sentences = split_sentences(text)
    print(f"\n  Sentences ({len(sentences)}):")
    for i, sent in enumerate(sentences, 1):
        preview = sent[:80] + ("..." if len(sent) > 80 else "")
        print(f"  {i:>3}. {preview}")

    # Word tokens
    words = tokenize_words(text)
    print(f"\n  Word Token Count: {len(words)}")
    print(f"  Unique Words:     {len(set(w.lower() for w in words if w.isalpha()))}")

    # Token type analysis
    typed_tokens = tokenize_by_type(text)
    type_counts  = Counter(t for _, t in typed_tokens)

    print(f"\n  Token Types:")
    for ttype, count in type_counts.most_common():
        print(f"    {ttype:<15} {count}")

    # Average sentence length
    sent_lengths = [len(tokenize_words(s)) for s in sentences]
    if sent_lengths:
        avg_len = sum(sent_lengths) / len(sent_lengths)
        print(f"\n  Avg sentence length: {avg_len:.1f} words")
        print(f"  Shortest sentence:   {min(sent_lengths)} words")
        print(f"  Longest sentence:    {max(sent_lengths)} words")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Split text into sentences and tokens")
parser.add_argument("--file", help="Text file to analyze")
args = parser.parse_args()

print("=== Sentence Splitter & Tokenizer ===\n")

if args.file and os.path.exists(args.file):
    with open(args.file) as f:
        text = f.read()
else:
    print("Using built-in sample text.\n")
    text = SAMPLE_TEXT

print_analysis(text)
