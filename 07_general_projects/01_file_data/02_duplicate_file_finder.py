"""
Project: Duplicate File Finder
What it does: Scans a folder and finds files that have identical content,
even if they have different names. Uses MD5 hashing to fingerprint files
— two files with the same hash have identical content.

How hashing works:
  - Every unique file produces a unique "fingerprint" (hash string)
  - If two files have the same hash → they are identical copies
  - We group files by their hash to find duplicates

Run: python 02_duplicate_file_finder.py  (scans current directory)
Run: python 02_duplicate_file_finder.py --dir /path/to/scan
"""

import os
import hashlib   # built-in module for computing file hashes
import argparse
from collections import defaultdict  # dict that auto-creates default values


def get_file_hash(filepath, chunk_size=65536):
    """
    Compute the MD5 hash (fingerprint) of a file.
    Reads in chunks to handle large files without loading them all into memory.

    chunk_size=65536 means we read 64 KB at a time (65536 bytes = 64 × 1024).
    """
    hasher = hashlib.md5()  # create an MD5 hasher object

    with open(filepath, "rb") as f:  # "rb" = read in binary mode (works for any file type)
        while True:
            chunk = f.read(chunk_size)  # read the next chunk

            if not chunk:
                break  # empty chunk means we've reached the end of the file

            hasher.update(chunk)  # feed this chunk into the hash calculation

    # hexdigest() returns the hash as a 32-character hex string like "a1b2c3d4..."
    return hasher.hexdigest()


def format_size(size_bytes):
    """Convert a byte count into a human-readable string like '1.5 MB'."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def find_duplicates(directory):
    """
    Walk through all files in a directory and group them by content hash.
    Returns a dict where keys are hashes and values are lists of matching file paths.
    """
    # defaultdict(list) creates a new empty list for any key that doesn't exist yet
    # This saves us from having to check 'if key not in dict' every time
    hash_groups = defaultdict(list)

    total_files = 0
    skipped     = 0

    print(f"Scanning: {directory}\n")

    # os.walk() visits every subfolder recursively
    # root = current folder, dirs = list of subfolders, files = list of files
    for root, dirs, files in os.walk(directory):
        # Skip hidden folders (like .git) for speed
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for filename in files:
            filepath = os.path.join(root, filename)  # full path to the file

            try:
                file_hash = get_file_hash(filepath)       # compute the fingerprint
                hash_groups[file_hash].append(filepath)   # group by hash
                total_files += 1
            except (PermissionError, OSError):
                # Some files may be locked or inaccessible — skip them
                skipped += 1

    print(f"Scanned: {total_files} files  (skipped: {skipped})\n")

    # Keep only groups that have MORE than one file (those are the duplicates)
    duplicates = {h: paths for h, paths in hash_groups.items() if len(paths) > 1}

    return duplicates


def report_duplicates(duplicates):
    """Print a report of all duplicate file groups."""
    if not duplicates:
        print("No duplicates found! All files are unique.")
        return

    total_wasted = 0  # total disk space wasted by duplicate files
    group_count  = 0

    print(f"Found {len(duplicates)} duplicate group(s):\n")

    for file_hash, file_paths in duplicates.items():
        group_count += 1

        # Get size of one copy (they're all identical so any one will do)
        try:
            file_size = os.path.getsize(file_paths[0])
        except OSError:
            file_size = 0

        # Wasted space = size × (number of copies - 1)
        wasted = file_size * (len(file_paths) - 1)
        total_wasted += wasted

        print(f"  Group {group_count}: {len(file_paths)} copies  "
              f"(size: {format_size(file_size)}, wasted: {format_size(wasted)})")
        print(f"  Hash: {file_hash[:16]}...")  # show first 16 chars of hash

        for i, path in enumerate(file_paths):
            marker = "  KEEP   →" if i == 0 else "  DELETE →"  # suggest which to keep
            print(f"    {marker} {path}")
        print()

    print(f"Total wasted space: {format_size(total_wasted)}")


def create_demo_files():
    """Create sample duplicate files for demonstration."""
    os.makedirs("demo_folder/subfolder", exist_ok=True)

    # Create original files
    with open("demo_folder/report.txt", "w") as f:
        f.write("Annual report content here. Version 2024.")

    # Create duplicates (same content, different names/locations)
    with open("demo_folder/report_backup.txt", "w") as f:
        f.write("Annual report content here. Version 2024.")  # identical!

    with open("demo_folder/subfolder/report_copy.txt", "w") as f:
        f.write("Annual report content here. Version 2024.")  # identical!

    # Create a unique file (not a duplicate)
    with open("demo_folder/notes.txt", "w") as f:
        f.write("These are my notes. Completely different content.")

    print("Demo files created in 'demo_folder/'")
    return "demo_folder"


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Find duplicate files by content hash")
parser.add_argument("--dir", help="Directory to scan (default: creates demo folder)")
args = parser.parse_args()

print("=== Duplicate File Finder ===\n")

if args.dir and os.path.isdir(args.dir):
    scan_dir = args.dir
else:
    print("No directory given — creating demo files...\n")
    scan_dir = create_demo_files()
    print()

duplicates = find_duplicates(scan_dir)
report_duplicates(duplicates)

# Clean up demo
if not args.dir:
    import shutil
    shutil.rmtree("demo_folder")
    print("\n(Demo folder cleaned up)")
