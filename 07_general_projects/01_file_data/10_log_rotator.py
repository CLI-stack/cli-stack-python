"""
Project: Log File Rotator
What it does: Manages log files by archiving old ones and keeping only
the most recent N files. Prevents log directories from growing indefinitely
and eating up disk space. Common in production server environments.

Strategy:
  1. Find all log files in a directory
  2. Sort by age (newest first)
  3. Keep the N most recent files
  4. Compress and archive the rest
  5. Delete files older than max_age_days

Run: python 10_log_rotator.py  (creates demo logs and rotates them)
Run: python 10_log_rotator.py --log-dir /var/log/myapp --keep 5 --max-age 30
"""

import os
import gzip          # built-in: compress files using gzip
import shutil        # for file operations (copy, move)
import argparse
import time
from datetime import datetime, timedelta


def get_log_files(log_dir, extension=".log"):
    """
    Find all log files in a directory, sorted by modification time (newest first).
    Returns a list of (filepath, modification_time) tuples.
    """
    log_files = []

    for filename in os.listdir(log_dir):
        if filename.endswith(extension):
            filepath = os.path.join(log_dir, filename)
            mtime    = os.path.getmtime(filepath)  # modification timestamp (Unix time)
            log_files.append((filepath, mtime))

    # Sort by modification time, newest first (reverse=True)
    log_files.sort(key=lambda x: x[1], reverse=True)

    return log_files


def compress_file(filepath):
    """
    Compress a file using gzip compression.
    Reads the original file and writes a compressed .gz version.
    The original file is deleted after successful compression.
    """
    compressed_path = filepath + ".gz"  # e.g. "app.log" → "app.log.gz"

    # Open input file in binary mode, open output in gzip write mode
    with open(filepath, "rb") as f_in:
        with gzip.open(compressed_path, "wb") as f_out:
            # shutil.copyfileobj copies data in chunks (memory-efficient)
            shutil.copyfileobj(f_in, f_out)

    # Delete the original uncompressed file
    os.remove(filepath)

    original_size   = os.path.getsize(compressed_path)  # compressed size
    return compressed_path


def format_size(size_bytes):
    """Human-readable file size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def rotate_logs(log_dir, keep_count=5, max_age_days=30, dry_run=False):
    """
    Perform log rotation:
    1. Find all log files
    2. Keep the newest 'keep_count' files untouched
    3. Compress files that are still within max_age_days
    4. Delete files older than max_age_days

    dry_run=True: show what would happen without actually doing it
    """
    print(f"Log directory: {log_dir}")
    print(f"Keep newest:   {keep_count} files")
    print(f"Max age:       {max_age_days} days")
    print(f"Mode:          {'DRY RUN' if dry_run else 'LIVE'}\n")

    log_files = get_log_files(log_dir)  # sorted newest to oldest

    if not log_files:
        print("No log files found.")
        return

    print(f"Found {len(log_files)} log file(s):\n")

    cutoff_time = time.time() - (max_age_days * 24 * 3600)
    # Convert days to seconds: max_age_days × 24 hours × 3600 seconds
    # Files older than cutoff_time will be deleted

    kept       = 0
    compressed = 0
    deleted    = 0
    space_saved= 0

    for i, (filepath, mtime) in enumerate(log_files):
        filename = os.path.basename(filepath)
        size     = os.path.getsize(filepath)
        age_days = (time.time() - mtime) / (24 * 3600)  # age in days
        mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

        if i < keep_count:
            # This file is among the newest — keep it untouched
            print(f"  KEEP       {filename:<30} {format_size(size):>10}  (age: {age_days:.1f}d)")
            kept += 1

        elif mtime < cutoff_time:
            # Too old — delete it
            print(f"  DELETE     {filename:<30} {format_size(size):>10}  (age: {age_days:.1f}d  — EXPIRED)")
            if not dry_run:
                os.remove(filepath)
            space_saved += size
            deleted += 1

        else:
            # Old enough to compress, but not expired — compress it
            print(f"  COMPRESS   {filename:<30} {format_size(size):>10}  (age: {age_days:.1f}d)")
            if not dry_run:
                compressed_path = compress_file(filepath)
                new_size = os.path.getsize(compressed_path)
                savings  = size - new_size
                ratio    = savings / size * 100 if size > 0 else 0
                print(f"             → {os.path.basename(compressed_path)}  "
                      f"{format_size(new_size)}  (saved {ratio:.0f}%)")
                space_saved += savings
            compressed += 1

    print(f"\n  Summary:")
    print(f"    Kept:       {kept}")
    print(f"    Compressed: {compressed}")
    print(f"    Deleted:    {deleted}")
    print(f"    Space saved: {format_size(space_saved)}")


def create_demo_logs(log_dir):
    """Create sample log files with different ages for demonstration."""
    os.makedirs(log_dir, exist_ok=True)

    now = time.time()  # current time as Unix timestamp

    # Create log files with different simulated ages
    log_specs = [
        ("app_2024_03_15.log",  0),        # today
        ("app_2024_03_14.log",  1),        # 1 day old
        ("app_2024_03_10.log",  5),        # 5 days old
        ("app_2024_02_15.log",  28),       # 28 days old
        ("app_2024_01_01.log",  73),       # 73 days old
        ("app_2023_12_01.log",  105),      # 105 days old (very old)
    ]

    for filename, age_days in log_specs:
        filepath = os.path.join(log_dir, filename)

        # Write some fake log content
        with open(filepath, "w") as f:
            f.write(f"[INFO]  Application started\n" * 50)
            f.write(f"[ERROR] Something went wrong\n" * 5)

        # Set the modification time to simulate the age
        # os.utime() sets (access_time, modification_time)
        fake_time = now - (age_days * 24 * 3600)
        os.utime(filepath, (fake_time, fake_time))

        print(f"  Created: {filename}  (simulated age: {age_days} days)")

    return log_dir


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Rotate and compress old log files")
parser.add_argument("--log-dir",  default=None, help="Log directory (default: demo)")
parser.add_argument("--keep",     type=int, default=3, help="Keep N newest files")
parser.add_argument("--max-age",  type=int, default=60, help="Delete files older than N days")
parser.add_argument("--dry-run",  action="store_true", help="Preview without changes")
args = parser.parse_args()

print("=== Log File Rotator ===\n")

if args.log_dir and os.path.isdir(args.log_dir):
    log_dir = args.log_dir
else:
    log_dir = "demo_logs"
    print("Creating demo log files...\n")
    create_demo_logs(log_dir)
    print()

rotate_logs(log_dir, keep_count=args.keep, max_age_days=args.max_age, dry_run=args.dry_run)

# Clean up demo
if not args.log_dir:
    shutil.rmtree(log_dir)
    print("\n(Demo log directory cleaned up)")
