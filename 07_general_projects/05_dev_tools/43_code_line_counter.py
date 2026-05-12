"""
Project: Code Line Counter (cloc-like tool)
What it does: Counts lines of code in a project, broken down by language.
Shows: total files, blank lines, comment lines, and actual code lines.
Similar to the popular 'cloc' (count lines of code) command-line tool.

Run: python 43_code_line_counter.py  (counts current directory)
Run: python 43_code_line_counter.py --dir /path/to/project
"""

import os
import argparse
from collections import defaultdict


# Extension → language name mapping
LANGUAGE_MAP = {
    ".py":    "Python",
    ".js":    "JavaScript",
    ".ts":    "TypeScript",
    ".jsx":   "React JSX",
    ".tsx":   "React TSX",
    ".html":  "HTML",
    ".css":   "CSS",
    ".scss":  "SCSS",
    ".java":  "Java",
    ".c":     "C",
    ".cpp":   "C++",
    ".h":     "C/C++ Header",
    ".cs":    "C#",
    ".go":    "Go",
    ".rs":    "Rust",
    ".rb":    "Ruby",
    ".php":   "PHP",
    ".sh":    "Shell",
    ".bash":  "Bash",
    ".sql":   "SQL",
    ".r":     "R",
    ".swift": "Swift",
    ".kt":    "Kotlin",
    ".yaml":  "YAML",
    ".yml":   "YAML",
    ".json":  "JSON",
    ".xml":   "XML",
    ".md":    "Markdown",
    ".txt":   "Text",
    ".toml":  "TOML",
    ".ini":   "INI",
    ".cfg":   "Config",
}

# Comment markers for each language
COMMENT_MARKERS = {
    "Python":      ["#"],
    "JavaScript":  ["//", "/*"],
    "TypeScript":  ["//", "/*"],
    "Java":        ["//", "/*"],
    "C":           ["//", "/*"],
    "C++":         ["//", "/*"],
    "Go":          ["//", "/*"],
    "Rust":        ["//", "/*"],
    "Ruby":        ["#"],
    "PHP":         ["//", "#", "/*"],
    "Shell":       ["#"],
    "Bash":        ["#"],
    "SQL":         ["--", "/*"],
    "R":           ["#"],
}

# Directories to skip (generated code, dependencies, etc.)
SKIP_DIRS = {
    ".git", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    "env", "dist", "build", ".next", ".nuxt", "target", "vendor",
    ".pytest_cache", ".mypy_cache", "coverage",
}


def analyze_file(filepath, language):
    """
    Count blank, comment, and code lines in a single file.
    Returns (blank_lines, comment_lines, code_lines).
    """
    blank    = 0
    comments = 0
    code     = 0

    comment_markers = COMMENT_MARKERS.get(language, [])
    in_block_comment = False  # track /* ... */ style block comments

    try:
        # errors="ignore" skips lines with encoding errors
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()

                # Blank line: empty or only whitespace
                if not stripped:
                    blank += 1
                    continue

                # Check for block comment start/end (/* ... */)
                if "/*" in stripped and not in_block_comment:
                    in_block_comment = True
                if in_block_comment:
                    comments += 1
                    if "*/" in stripped:
                        in_block_comment = False
                    continue

                # Check for single-line comment markers (// or #)
                is_comment = any(stripped.startswith(m) for m in comment_markers
                                 if m != "/*")
                if is_comment:
                    comments += 1
                else:
                    code += 1

    except (PermissionError, OSError):
        pass  # skip files we can't read

    return blank, comments, code


def count_project(directory):
    """
    Walk through a project directory and count lines for all source files.
    Returns a dict: {language: {files, blank, comments, code}}
    """
    stats = defaultdict(lambda: {"files": 0, "blank": 0, "comments": 0, "code": 0})

    for root, dirs, files in os.walk(directory):
        # Skip unwanted directories (modify dirs in-place to prevent os.walk from entering them)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

        for filename in files:
            ext  = os.path.splitext(filename)[1].lower()  # file extension

            if ext not in LANGUAGE_MAP:
                continue  # skip unknown file types

            language = LANGUAGE_MAP[ext]
            filepath = os.path.join(root, filename)

            blank, comments, code = analyze_file(filepath, language)

            stats[language]["files"]    += 1
            stats[language]["blank"]    += blank
            stats[language]["comments"] += comments
            stats[language]["code"]     += code

    return stats


def print_report(stats, directory):
    """Display the code count results in a formatted table."""
    CYN  = "\033[36m"
    GRN  = "\033[92m"
    YEL  = "\033[33m"
    BOLD = "\033[1m"
    RST  = "\033[0m"

    total_files    = sum(s["files"]    for s in stats.values())
    total_blank    = sum(s["blank"]    for s in stats.values())
    total_comments = sum(s["comments"] for s in stats.values())
    total_code     = sum(s["code"]     for s in stats.values())
    total_lines    = total_blank + total_comments + total_code

    print("=" * 75)
    print(f"  {BOLD}CODE LINE COUNTER{RST}")
    print(f"  Directory: {os.path.abspath(directory)}")
    print("=" * 75)

    if not stats:
        print("\n  No source files found.")
        return

    # Sort by lines of code (most code first)
    sorted_stats = sorted(stats.items(), key=lambda x: -x[1]["code"])

    print(f"\n  {'LANGUAGE':<20} {'FILES':>6} {'BLANK':>8} {'COMMENTS':>10} "
          f"{'CODE':>8} {'TOTAL':>8}")
    print("  " + "─" * 65)

    for language, s in sorted_stats:
        total = s["blank"] + s["comments"] + s["code"]
        print(f"  {language:<20} {s['files']:>6} {s['blank']:>8} "
              f"{s['comments']:>10} {s['code']:>8} {total:>8}")

    # Totals row
    print("  " + "─" * 65)
    print(f"  {'TOTAL':<20} {GRN}{total_files:>6} {total_blank:>8} "
          f"{total_comments:>10} {total_code:>8} {total_lines:>8}{RST}")

    # Summary
    code_pct    = total_code / total_lines * 100 if total_lines else 0
    comment_pct = total_comments / total_lines * 100 if total_lines else 0
    blank_pct   = total_blank / total_lines * 100 if total_lines else 0

    print(f"\n  Summary:")
    print(f"    Total source files  : {total_files}")
    print(f"    Total lines         : {total_lines:,}")
    print(f"    Lines of code       : {total_code:,} ({code_pct:.0f}%)")
    print(f"    Comment lines       : {total_comments:,} ({comment_pct:.0f}%)")
    print(f"    Blank lines         : {total_blank:,} ({blank_pct:.0f}%)")

    # Language distribution bar
    print(f"\n  Language Distribution:")
    max_code = sorted_stats[0][1]["code"] if sorted_stats else 1
    for language, s in sorted_stats[:8]:
        bar_len = int(30 * s["code"] / max_code)
        bar     = "█" * bar_len
        pct     = s["code"] / total_code * 100 if total_code else 0
        print(f"    {language:<20} {bar:<30} {pct:.1f}%")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Count lines of code by language")
parser.add_argument("--dir", default=".", help="Project directory (default: current)")
args = parser.parse_args()

print("=== Code Line Counter ===\n")
print(f"Scanning: {os.path.abspath(args.dir)}\n")

stats = count_project(args.dir)
print_report(stats, args.dir)
