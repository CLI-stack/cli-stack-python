"""
Project: Disk Usage Reporter
What it does: Analyzes disk usage across a directory tree and generates
a report showing the largest folders and files. Similar to the 'du' command
but with a nicer output and HTML export option.

Run: python 49_disk_usage_reporter.py  (analyzes current directory)
Run: python 49_disk_usage_reporter.py --dir /path --depth 2 --top 10
"""

import os
import argparse
from datetime import datetime


def format_size(size_bytes):
    """Convert bytes to human-readable string."""
    if size_bytes == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_dir_size(path):
    """
    Calculate the total size of all files in a directory recursively.
    Walks through every subdirectory and sums up file sizes.
    Returns -1 if access is denied.
    """
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            # Skip hidden directories to avoid permission errors and clutter
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    total += os.path.getsize(filepath)
                except (OSError, PermissionError):
                    pass  # skip files we can't read
    except PermissionError:
        return -1

    return total


def analyze_directory(base_path, max_depth=2):
    """
    Recursively analyze a directory up to max_depth levels.
    Returns a list of (path, size, depth) tuples.
    """
    results = []

    def walk(path, depth):
        if depth > max_depth:
            return

        try:
            entries = sorted(os.scandir(path), key=lambda e: e.name)
        except PermissionError:
            return

        for entry in entries:
            if entry.name.startswith("."):
                continue  # skip hidden files/folders

            full_path = entry.path

            if entry.is_dir(follow_symlinks=False):
                size = get_dir_size(full_path)
                if size >= 0:
                    results.append({
                        "path":  full_path,
                        "name":  entry.name,
                        "size":  size,
                        "depth": depth,
                        "type":  "dir",
                    })
                    walk(full_path, depth + 1)  # recurse into subdirectory

            elif entry.is_file(follow_symlinks=False):
                try:
                    size = entry.stat().st_size
                    results.append({
                        "path":  full_path,
                        "name":  entry.name,
                        "size":  size,
                        "depth": depth,
                        "type":  "file",
                    })
                except OSError:
                    pass

    walk(base_path, 0)
    return results


def get_extension_breakdown(path):
    """Count total size by file extension."""
    from collections import defaultdict
    by_ext = defaultdict(int)

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for filename in files:
            ext  = os.path.splitext(filename)[1].lower() or "(no extension)"
            filepath = os.path.join(root, filename)
            try:
                by_ext[ext] += os.path.getsize(filepath)
            except OSError:
                pass

    return by_ext


def print_report(base_path, results, top_n=15):
    """Display the disk usage report."""
    CYN  = "\033[36m"
    GRN  = "\033[92m"
    YEL  = "\033[33m"
    BOLD = "\033[1m"
    RST  = "\033[0m"

    # Separate directories and files
    dirs  = sorted([r for r in results if r["type"] == "dir"],  key=lambda x: -x["size"])
    files = sorted([r for r in results if r["type"] == "file"], key=lambda x: -x["size"])

    # Calculate totals
    total_size = get_dir_size(base_path)

    print("=" * 65)
    print(f"  {BOLD}DISK USAGE REPORT{RST}")
    print(f"  Directory: {base_path}")
    print(f"  Total size: {format_size(total_size)}")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    # Top directories
    print(f"\n  {CYN}Top {top_n} Directories by Size:{RST}\n")
    print(f"  {'SIZE':>10}  {'% OF TOTAL':>10}  {'PATH'}")
    print("  " + "─" * 65)

    for d in dirs[:top_n]:
        pct      = d["size"] / total_size * 100 if total_size else 0
        rel_path = os.path.relpath(d["path"], base_path)
        indent   = "  " * d["depth"]   # indent based on folder depth

        # Color code by size percentage
        if pct >= 30:     color = YEL
        elif pct >= 10:   color = ""
        else:             color = "\033[90m"  # grey for small ones

        bar_len = min(int(pct / 3), 20)
        bar     = "█" * bar_len

        print(f"  {format_size(d['size']):>10}  {pct:>9.1f}%  "
              f"{indent}{color}{rel_path}{RST}  {color}{bar}{RST}")

    # Top files
    print(f"\n  {CYN}Top {top_n} Largest Files:{RST}\n")
    print(f"  {'SIZE':>10}  {'FILE'}")
    print("  " + "─" * 65)

    for f in files[:top_n]:
        rel_path = os.path.relpath(f["path"], base_path)
        print(f"  {format_size(f['size']):>10}  {rel_path}")

    # Extension breakdown
    by_ext = get_extension_breakdown(base_path)
    sorted_ext = sorted(by_ext.items(), key=lambda x: -x[1])[:10]

    print(f"\n  {CYN}Size by File Type (top 10):{RST}\n")
    print(f"  {'EXTENSION':<20} {'SIZE':>10}  {'%':>5}")
    print("  " + "─" * 40)

    for ext, size in sorted_ext:
        pct = size / total_size * 100 if total_size else 0
        bar = "█" * int(pct / 2)
        print(f"  {ext:<20} {format_size(size):>10}  {pct:>4.1f}%  {bar}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Analyze disk usage by directory")
parser.add_argument("--dir",   default=".", help="Directory to analyze")
parser.add_argument("--depth", type=int, default=2, help="Max folder depth to show")
parser.add_argument("--top",   type=int, default=10, help="Top N items to show")
args = parser.parse_args()

print("=== Disk Usage Reporter ===\n")
print(f"Analyzing: {os.path.abspath(args.dir)}  (depth: {args.depth})")
print("Please wait...\n")

results = analyze_directory(os.path.abspath(args.dir), max_depth=args.depth)
print_report(os.path.abspath(args.dir), results, top_n=args.top)
