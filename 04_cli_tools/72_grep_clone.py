"""
Script: Grep Clone (Search in Files)
What it does: Searches for a pattern in files, like the Unix 'grep' command.
grep is one of the most useful tools for developers — find text in any file.

Run: python 72_grep_clone.py "error" logfile.txt
Run: python 72_grep_clone.py "def " mycode.py --line-numbers --ignore-case
"""

import argparse
import os
import re

def search_file(filepath, pattern, case_insensitive=False, show_line_numbers=True, show_filename=False):
    """Search for pattern in a file and return matching lines."""
    flags = re.IGNORECASE if case_insensitive else 0
    matches = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, start=1):
                if re.search(pattern, line, flags):
                    entry = {}
                    if show_filename:
                        entry["file"] = filepath
                    if show_line_numbers:
                        entry["line_num"] = line_num
                    entry["line"] = line.rstrip()
                    matches.append(entry)
    except PermissionError:
        print(f"Permission denied: {filepath}")

    return matches

def highlight_match(line, pattern, flags=0):
    """Add simple highlighting to matched text (brackets)."""
    return re.sub(pattern, lambda m: f"[{m.group()}]", line, flags=flags)

# --- Parse arguments ---
parser = argparse.ArgumentParser(description="Search for patterns in files (like grep)")
parser.add_argument("pattern", help="Pattern to search for (can be regex)")
parser.add_argument("files", nargs="+", help="File(s) to search")
parser.add_argument("-i", "--ignore-case", action="store_true", help="Case-insensitive search")
parser.add_argument("-n", "--line-numbers", action="store_true", help="Show line numbers")
parser.add_argument("-c", "--count", action="store_true", help="Show only count of matches")
parser.add_argument("-r", "--recursive", action="store_true", help="Search directories recursively")

args = parser.parse_args()

flags = re.IGNORECASE if args.ignore_case else 0
total_matches = 0

for filepath in args.files:
    if os.path.isdir(filepath):
        if args.recursive:
            for root, _, files in os.walk(filepath):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    matches = search_file(full_path, args.pattern, args.ignore_case, True, len(args.files) > 1)
                    for m in matches:
                        if not args.count:
                            prefix = f"{m.get('file', '')}:" if 'file' in m else ""
                            prefix += f"{m['line_num']}:" if 'line_num' in m else ""
                            print(f"{prefix} {m['line']}")
                    total_matches += len(matches)
    else:
        matches = search_file(filepath, args.pattern, args.ignore_case, args.line_numbers, len(args.files) > 1)
        if args.count:
            print(f"{filepath}: {len(matches)} matches")
        else:
            for m in matches:
                prefix = f"{m.get('file', '')}:" if 'file' in m else ""
                prefix += f"{m['line_num']}:" if 'line_num' in m else ""
                print(f"{prefix} {m['line']}")
        total_matches += len(matches)

if args.count:
    print(f"Total: {total_matches} matches")
