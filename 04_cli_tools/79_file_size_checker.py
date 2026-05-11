"""
Script: File Size Checker CLI
What it does: Lists files sorted by size, finds the largest files in a directory.
Useful for finding what's eating up your disk space.

Run: python 79_file_size_checker.py .
Run: python 79_file_size_checker.py /home/user --top 10 --min-size 1MB
"""

import os
import argparse

def format_size(bytes_val):
    """Convert bytes to a human-readable string like '1.5 MB'."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024.0:
            return f"{bytes_val:>8.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} PB"

def parse_size(size_str):
    """Parse a size string like '10MB' to bytes."""
    size_str = size_str.upper().strip()
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
    for unit, factor in units.items():
        if size_str.endswith(unit):
            return float(size_str[:-len(unit)]) * factor
    return float(size_str)

def scan_directory(directory, min_size=0, extensions=None):
    """Recursively scan directory and return list of (size, path) tuples."""
    files = []
    total_size = 0

    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]  # skip hidden

        for filename in filenames:
            filepath = os.path.join(root, filename)

            if extensions and not any(filename.endswith(e) for e in extensions):
                continue

            try:
                size = os.path.getsize(filepath)
                total_size += size
                if size >= min_size:
                    files.append((size, filepath))
            except (OSError, PermissionError):
                pass

    return files, total_size

# --- Parse arguments ---
parser = argparse.ArgumentParser(description="Find large files in a directory")
parser.add_argument("directory", nargs="?", default=".", help="Directory to scan")
parser.add_argument("--top", type=int, default=20, help="Show top N files (default: 20)")
parser.add_argument("--min-size", default="0", help="Minimum file size (e.g., 1KB, 10MB)")
args = parser.parse_args()

min_bytes = parse_size(args.min_size)
directory = os.path.abspath(args.directory)

print(f"Scanning: {directory}")
print(f"Minimum size: {format_size(min_bytes).strip()}")
print()

files, total = scan_directory(directory, min_bytes)

# Sort by size (largest first)
files.sort(reverse=True)

print(f"{'Size':>12} {'File'}")
print("-" * 70)
for size, path in files[:args.top]:
    # Make path relative for readability
    rel_path = os.path.relpath(path, directory)
    print(f"{format_size(size)} {rel_path}")

print("-" * 70)
print(f"{'Total:':>12} {format_size(total).strip()} across {len(files)} files")
