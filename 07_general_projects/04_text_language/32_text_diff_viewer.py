"""
Project: Text Diff Viewer
What it does: Compares two versions of text and shows what changed —
additions, deletions, and unchanged lines. Like 'git diff' but in Python.
Uses Python's built-in difflib module.

Run: python 32_text_diff_viewer.py
Run: python 32_text_diff_viewer.py --file1 v1.txt --file2 v2.txt
"""

import difflib   # built-in: text comparison algorithms
import argparse
import os


# Sample texts to compare (simulating a document before and after edits)
VERSION_1 = """Python is a programming language.
It was created by Guido van Rossum.
Python 1.0 was released in 1991.
It is known for its simple syntax.
Python supports multiple paradigms.
It has a large standard library.
Python is widely used in data science.
"""

VERSION_2 = """Python is a high-level programming language.
It was created by Guido van Rossum in the Netherlands.
Python 1.0 was released in 1994.
It is famous for its clean and readable syntax.
Python supports multiple programming paradigms.
It has a comprehensive standard library.
Python is widely used in data science and machine learning.
Python has a thriving community of developers.
"""


def diff_lines(text1, text2, label1="Version 1", label2="Version 2"):
    """
    Compare two texts line by line and categorize each line as:
    - ADDED    (in text2 but not text1)
    - DELETED  (in text1 but not text2)
    - CHANGED  (in both but different)
    - SAME     (identical in both)

    difflib.ndiff() returns the line-by-line difference.
    Each line is prefixed with:
      '  ' = unchanged
      '+ ' = added
      '- ' = deleted
      '? ' = detailed character-level difference
    """
    lines1 = text1.splitlines(keepends=True)  # keepends=True keeps the \n
    lines2 = text2.splitlines(keepends=True)

    # ndiff() compares sequences of lines
    diff = list(difflib.ndiff(lines1, lines2))
    return diff


def show_unified_diff(text1, text2, label1="Version 1", label2="Version 2", context=3):
    """
    Generate a unified diff (like git diff format).
    Shows changed lines with N lines of context around each change.

    context=3 means show 3 unchanged lines before and after each change block.
    This helps readers understand what surrounds the change.
    """
    lines1 = text1.splitlines(keepends=True)
    lines2 = text2.splitlines(keepends=True)

    # unified_diff() generates a unified format diff
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=label1,       # label for the "before" version
        tofile=label2,         # label for the "after" version
        n=context,             # lines of context
        lineterm=""            # don't add extra newlines
    )
    return list(diff)


def show_side_by_side(text1, text2, width=40):
    """
    Display two texts side by side with differences highlighted.
    Like a split-view editor comparing two versions.
    """
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()

    # Pad the shorter list so both have equal length
    max_lines = max(len(lines1), len(lines2))
    lines1 += [""] * (max_lines - len(lines1))  # pad with empty strings
    lines2 += [""] * (max_lines - len(lines2))

    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print(f"\n  {'LEFT':<{width}} │ {'RIGHT'}")
    print("  " + "─" * width + "─┼─" + "─" * width)

    for l1, l2 in zip(lines1, lines2):
        if l1 == l2:
            # Identical line
            print(f"  {l1[:width]:<{width}} │ {l2[:width]}")
        elif l1 and not l2:
            # Line was deleted
            print(f"  {RED}{l1[:width]:<{width}}{RST} │")
        elif l2 and not l1:
            # Line was added
            print(f"  {'':<{width}} │ {GREEN}{l2[:width]}{RST}")
        else:
            # Line was changed
            print(f"  {RED}{l1[:width]:<{width}}{RST} │ {GREEN}{l2[:width]}{RST}")


def print_diff_stats(text1, text2):
    """Show statistics: how many lines added, deleted, unchanged."""
    lines1 = set(text1.splitlines())
    lines2 = set(text2.splitlines())

    added    = len(lines2 - lines1)
    deleted  = len(lines1 - lines2)
    unchanged= len(lines1 & lines2)

    # Calculate similarity ratio (0.0 = completely different, 1.0 = identical)
    ratio = difflib.SequenceMatcher(None, text1, text2).ratio()

    print(f"\n  Diff Statistics:")
    print(f"    Lines added   : \033[92m+{added}\033[0m")
    print(f"    Lines deleted : \033[91m-{deleted}\033[0m")
    print(f"    Unchanged     : {unchanged}")
    print(f"    Similarity    : {ratio*100:.1f}%")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Compare two text versions")
parser.add_argument("--file1", help="First text file")
parser.add_argument("--file2", help="Second text file")
parser.add_argument("--mode",  choices=["unified","sidebyside","stats"],
                    default="unified", help="Display mode")
args = parser.parse_args()

print("=== Text Diff Viewer ===\n")

if args.file1 and args.file2 and os.path.exists(args.file1) and os.path.exists(args.file2):
    with open(args.file1) as f: text1 = f.read()
    with open(args.file2) as f: text2 = f.read()
    label1, label2 = args.file1, args.file2
else:
    print("Using built-in sample texts.\n")
    text1, text2   = VERSION_1, VERSION_2
    label1, label2 = "Version 1 (original)", "Version 2 (revised)"

print_diff_stats(text1, text2)

# Show unified diff (like git diff)
print(f"\n  Unified Diff ({label1} → {label2}):")
GREEN = "\033[92m"
RED   = "\033[91m"
CYN   = "\033[36m"
RST   = "\033[0m"
print()

for line in show_unified_diff(text1, text2, label1, label2):
    if line.startswith("+"):
        print(f"  {GREEN}{line}{RST}", end="")
    elif line.startswith("-"):
        print(f"  {RED}{line}{RST}", end="")
    elif line.startswith("@@"):
        print(f"  {CYN}{line}{RST}", end="")
    else:
        print(f"  {line}", end="")

# Show side by side
print(f"\n\n  Side-by-Side View:")
show_side_by_side(text1, text2, width=50)
