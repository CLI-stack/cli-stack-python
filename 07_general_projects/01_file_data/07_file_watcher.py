"""
Project: File Watcher
What it does: Monitors a folder for changes — new files, deleted files,
and modified files. Runs continuously and reports any changes it detects.
Useful for monitoring log folders, auto-processing uploads, or syncing.

How it works:
  - Take a "snapshot" of all files and their modification times
  - Wait a few seconds
  - Take another snapshot
  - Compare the two to find what changed
  - Repeat forever (or for a fixed duration)

Run: python 07_file_watcher.py
Run: python 07_file_watcher.py --folder /path/to/watch --interval 3
"""

import os
import time
import argparse
from datetime import datetime


def get_folder_snapshot(folder_path):
    """
    Capture the current state of all files in a folder.
    Returns a dict: {filepath: modification_time}
    The modification time tells us when a file was last changed.
    """
    snapshot = {}

    for root, dirs, files in os.walk(folder_path):
        # Skip hidden folders (like .git)
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                # os.path.getmtime() returns the last-modified timestamp as a float
                # (seconds since January 1, 1970 — called Unix timestamp)
                mtime = os.path.getmtime(filepath)
                snapshot[filepath] = mtime
            except OSError:
                pass  # file may have been deleted between listdir and getmtime

    return snapshot


def compare_snapshots(old_snapshot, new_snapshot):
    """
    Compare two folder snapshots and return what changed.
    Returns three lists: added, deleted, modified file paths.
    """
    old_files = set(old_snapshot.keys())  # set of file paths in old snapshot
    new_files = set(new_snapshot.keys())  # set of file paths in new snapshot

    # Files in new but NOT in old → they were added
    added = list(new_files - old_files)

    # Files in old but NOT in new → they were deleted
    deleted = list(old_files - new_files)

    # Files in BOTH snapshots but with a different modification time → modified
    modified = [
        f for f in old_files & new_files  # & = intersection (files in both)
        if old_snapshot[f] != new_snapshot[f]  # modification time changed
    ]

    return added, deleted, modified


def watch_folder(folder_path, interval=2, max_cycles=None):
    """
    Continuously monitor a folder for changes.

    folder_path: which folder to watch
    interval:    seconds to wait between checks
    max_cycles:  how many checks to do before stopping (None = run forever)
    """
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid folder.")
        return

    print(f"Watching folder: {folder_path}")
    print(f"Check interval:  {interval} seconds")
    print(f"Press Ctrl+C to stop\n")

    # Take the initial snapshot to use as baseline
    old_snapshot = get_folder_snapshot(folder_path)
    print(f"  Baseline snapshot: {len(old_snapshot)} files tracked")
    print(f"  Started at: {datetime.now().strftime('%H:%M:%S')}\n")

    cycle = 0
    total_events = 0

    try:
        while max_cycles is None or cycle < max_cycles:
            time.sleep(interval)  # wait before checking again
            cycle += 1

            # Take a new snapshot
            new_snapshot = get_folder_snapshot(folder_path)

            # Compare to find changes
            added, deleted, modified = compare_snapshots(old_snapshot, new_snapshot)

            # Report any changes found
            if added or deleted or modified:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Changes detected:")

                for f in added:
                    size = os.path.getsize(f) if os.path.exists(f) else 0
                    print(f"  + ADDED    {os.path.basename(f)}  ({size} bytes)")
                    total_events += 1

                for f in deleted:
                    print(f"  - DELETED  {os.path.basename(f)}")
                    total_events += 1

                for f in modified:
                    size = os.path.getsize(f) if os.path.exists(f) else 0
                    print(f"  ~ MODIFIED {os.path.basename(f)}  ({size} bytes)")
                    total_events += 1

                print()

            # The NEW snapshot becomes the OLD snapshot for the next cycle
            old_snapshot = new_snapshot

    except KeyboardInterrupt:
        print(f"\nStopped. Detected {total_events} total events in {cycle} checks.")


def demo_watcher():
    """Run a demo: create a temp folder, watch it, simulate file changes."""
    import threading
    import shutil

    watch_dir = "watch_demo"
    os.makedirs(watch_dir, exist_ok=True)

    # Write an initial file
    with open(f"{watch_dir}/initial.txt", "w") as f:
        f.write("initial content")

    def simulate_changes():
        """This runs in a background thread to simulate file changes."""
        time.sleep(2)
        with open(f"{watch_dir}/new_file.txt", "w") as f:
            f.write("new file added!")

        time.sleep(2)
        with open(f"{watch_dir}/initial.txt", "w") as f:
            f.write("modified content")  # modify the original file

        time.sleep(2)
        os.remove(f"{watch_dir}/new_file.txt")  # delete a file

    print("=== File Watcher Demo ===")
    print("Simulating: add → modify → delete over 8 seconds\n")

    # Start the change simulator in a background thread
    # daemon=True means the thread will stop when the main program stops
    t = threading.Thread(target=simulate_changes, daemon=True)
    t.start()

    # Watch for 4 cycles (4 × 2 seconds = 8 seconds)
    watch_folder(watch_dir, interval=2, max_cycles=4)

    # Clean up
    shutil.rmtree(watch_dir)
    print("(Demo folder cleaned up)")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Watch a folder for file changes")
parser.add_argument("--folder",   help="Folder to monitor (default: runs demo)")
parser.add_argument("--interval", type=int, default=2, help="Seconds between checks")
args = parser.parse_args()

if args.folder:
    watch_folder(args.folder, interval=args.interval)
else:
    demo_watcher()
