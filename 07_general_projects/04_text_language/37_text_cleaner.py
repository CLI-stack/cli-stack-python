"""
Project: Text Cleaner and Normalizer
What it does: Cleans messy text data — removes extra whitespace,
fixes punctuation, standardizes formatting, removes HTML tags,
and normalizes special characters. Common preprocessing step in NLP pipelines.

Run: python 37_text_cleaner.py
Run: python 37_text_cleaner.py --file messy_text.txt
"""

import re
import os
import argparse
import unicodedata  # built-in: for Unicode character normalization


MESSY_SAMPLES = [
    # Sample 1: HTML with messy whitespace
    """  <p>Hello   World!!!    This   has   too   many   spaces.</p>
   <br>  Also has HTML  tags.  &amp; HTML entities &lt;like these&gt;.  """,

    # Sample 2: Special characters and encoding issues
    "Café naïve resumé — with em-dash and ‘smart quotes’",

    # Sample 3: Inconsistent punctuation
    "Hello , world !!! How are you ???   I'm  fine...   Really  !!",

    # Sample 4: Mixed case headers
    "INTRODUCTION\nThis is the INTRODUCTION section. It INTRODUCES the topic.",
]


def remove_html_tags(text):
    """
    Remove HTML tags like <p>, <br>, <strong> etc.
    HTML tags follow the pattern: < anything >

    re.sub() replaces all matches of the pattern with a replacement string.
    r"<[^>]+>" matches < followed by anything except > followed by >
    """
    return re.sub(r"<[^>]+>", " ", text)


def decode_html_entities(text):
    """
    Convert HTML entities back to their characters.
    &amp; → &    &lt; → <    &gt; → >    &nbsp; → (space)
    """
    entities = {
        "&amp;":  "&",
        "&lt;":   "<",
        "&gt;":   ">",
        "&quot;": '"',
        "&apos;": "'",
        "&nbsp;": " ",
    }
    for entity, char in entities.items():
        text = text.replace(entity, char)
    return text


def normalize_unicode(text):
    """
    Normalize Unicode characters to their ASCII equivalents where possible.
    é → e   ñ → n   ü → u   — → -   ' → '

    unicodedata.normalize("NFKD") decomposes characters into base + accent
    Then encode("ascii", "ignore") strips the accent marks
    """
    # First, replace smart quotes and dashes with ASCII equivalents
    replacements = {
        "‘": "'",    # left single quotation mark
        "’": "'",    # right single quotation mark
        "“": '"',    # left double quotation mark
        "”": '"',    # right double quotation mark
        "—": "-",    # em dash
        "–": "-",    # en dash
        "…": "...",  # horizontal ellipsis
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # Decompose accented characters and remove accents
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text


def fix_whitespace(text):
    """
    Normalize all whitespace:
    - Multiple spaces → single space
    - Multiple newlines → single newline
    - Strip leading/trailing whitespace from each line
    """
    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)

    # Replace multiple newlines with single newline
    text = re.sub(r"\n\s*\n", "\n", text)

    # Strip each line
    lines = [line.strip() for line in text.split("\n")]
    text  = "\n".join(line for line in lines if line)  # remove empty lines

    return text.strip()


def fix_punctuation(text):
    """
    Fix common punctuation issues:
    - Space before punctuation: "Hello !" → "Hello!"
    - Multiple punctuation: "!!!" → "!"
    - Space after opening bracket: "( hello)" → "(hello)"
    """
    # Remove space before punctuation marks
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)

    # Add space after punctuation if missing (but not at end)
    text = re.sub(r"([.,!?;:])([A-Za-z])", r"\1 \2", text)

    # Collapse multiple identical punctuation: !!! → !   ??? → ?
    text = re.sub(r"([!?]){2,}", r"\1", text)

    # Collapse multiple dots (unless it's an ellipsis ...)
    text = re.sub(r"\.{4,}", "...", text)

    return text


def remove_special_chars(text, keep="letters spaces punctuation"):
    """
    Remove non-standard characters, keeping only letters, digits,
    common punctuation, and whitespace.
    """
    # Keep: letters (a-z A-Z), digits (0-9), common punctuation, whitespace
    return re.sub(r"[^\w\s.,!?;:'\"-]", "", text)


def clean_text(text, options=None):
    """
    Apply all cleaning steps in the right order.
    Options is a dict controlling which steps to apply.
    """
    if options is None:
        options = {
            "remove_html":      True,
            "decode_entities":  True,
            "normalize_unicode":True,
            "fix_whitespace":   True,
            "fix_punctuation":  True,
        }

    steps_applied = []

    if options.get("remove_html"):
        text = remove_html_tags(text)
        steps_applied.append("remove HTML tags")

    if options.get("decode_entities"):
        text = decode_html_entities(text)
        steps_applied.append("decode HTML entities")

    if options.get("normalize_unicode"):
        text = normalize_unicode(text)
        steps_applied.append("normalize Unicode")

    if options.get("fix_whitespace"):
        text = fix_whitespace(text)
        steps_applied.append("fix whitespace")

    if options.get("fix_punctuation"):
        text = fix_punctuation(text)
        steps_applied.append("fix punctuation")

    return text, steps_applied


def print_before_after(original, cleaned, label=""):
    """Display original and cleaned text side by side."""
    CYN = "\033[36m"
    GRN = "\033[92m"
    RST = "\033[0m"

    print(f"\n  {'─'*55}")
    if label:
        print(f"  {label}")
    print(f"  {CYN}BEFORE:{RST}")
    print(f"    {repr(original[:100])}")
    print(f"  {GRN}AFTER:{RST}")
    print(f"    {repr(cleaned[:100])}")
    print(f"  Reduced by: {len(original) - len(cleaned)} characters")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Clean and normalize text")
parser.add_argument("--file",    help="Text file to clean")
parser.add_argument("--output",  help="Save cleaned text to file")
args = parser.parse_args()

print("=== Text Cleaner and Normalizer ===\n")

if args.file and os.path.exists(args.file):
    with open(args.file, encoding="utf-8", errors="replace") as f:
        text = f.read()
    cleaned, steps = clean_text(text)
    print(f"File: {args.file}")
    print(f"Original length: {len(text)} chars")
    print(f"Cleaned length:  {len(cleaned)} chars")
    print(f"Steps applied: {', '.join(steps)}")
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"Saved to: {args.output}")
    else:
        print(f"\nCleaned text:\n{cleaned[:500]}")
else:
    # Demo mode: run all samples
    print("Cleaning messy text samples:\n")
    labels = ["HTML & Whitespace", "Unicode & Special Chars",
              "Punctuation", "Mixed Case"]

    for label, sample in zip(labels, MESSY_SAMPLES):
        cleaned, steps = clean_text(sample)
        print_before_after(sample, cleaned, label)
