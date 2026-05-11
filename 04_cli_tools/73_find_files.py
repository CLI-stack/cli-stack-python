"""
Script: Find Files CLI
What it does: Searches for files by name, extension, or size.
Similar to the Unix 'find' command.

Run: python 73_find_files.py . --ext .py
Run: python 73_find_files.py . --name "*.txt" --min-size 1024
"""

import argparse
import os
import fnmatch
from datetime import datetime

def find_files(directory, extension=None, name_pattern=None, min_size=None, max_size=None):
    """Walk through directory and find matching files."""
    results = []

    for root, dirs, files in os.walk(directory):
        # Skip hidden directories (like .git)
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for filename in files:
            filepath = os.path.join(root, filename)

            # Filter by extension
            if extension and not filename.endswith(extension):
                continue

            # Filter by name pattern
            if name_pattern and not fnmatch.fnmatch(filename, name_pattern):
                continue

            # Filter by file size
            try:
                size = os.path.getsize(filepath)
            except OSError:
                continue

            if min_size and size < min_size:
                continue
            if max_size and size > max_size:
                continue

            # Get modification time
            mtime = os.path.getmtime(filepath)
            mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

            results.append({
                "path": filepath,
                "size": size,
                "modified": mod_time,
                "name": filename
            })

    return results

def format_size(bytes_val):
    """Convert bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"

# --- Parse arguments ---
parser = argparse.ArgumentParser(description="Find files in a directory")
parser.add_argument("directory", help="Directory to search")
parser.add_argument("--ext", help="File extension (e.g., .py)")
parser.add_argument("--name", help="File name pattern (e.g., '*.txt')")
parser.add_argument("--min-size", type=int, help="Minimum file size in bytes")
parser.add_argument("--max-size", type=int, help="Maximum file size in bytes")
parser.add_argument("--sort", choices=["name", "size", "date"], default="name")

args = parser.parse_args()

if not os.path.exists(args.directory):
    print(f"Directory not found: {args.directory}")
    exit(1)

print(f"Searching in: {args.directory}\n")
results = find_files(args.directory, args.ext, args.name, args.min_size, args.max_size)

# Sort results
results.sort(key=lambda f: f.get({"name": "name", "size": "size", "date": "modified"}[args.sort]))

print(f"Found {len(results)} files:\n")
print(f"{'Filename':<35} {'Size':>10} {'Modified'}")
print("-" * 65)
for f in results[:50]:  # limit output
    print(f"{f['path']:<35} {format_size(f['size']):>10} {f['modified']}")

if len(results) > 50:
    print(f"\n... and {len(results) - 50} more files")
