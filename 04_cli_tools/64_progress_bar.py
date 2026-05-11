"""
Script: Progress Bar
What it does: Shows a visual progress bar in the terminal while doing work.
Useful for long-running tasks so users know something is happening.

Install: pip install tqdm  (optional — script shows both with and without)
"""

import time
import sys

# --- Method 1: Manual progress bar (no extra libraries) ---
def manual_progress_bar(current, total, bar_length=40, description=""):
    """Draw a simple ASCII progress bar."""
    percent = current / total                       # e.g., 0.75 = 75%
    filled = int(bar_length * percent)              # number of # to draw
    bar = "#" * filled + "-" * (bar_length - filled)  # filled + empty

    # \r moves cursor to start of line (overwrites instead of new line)
    print(f"\r{description} [{bar}] {percent:.0%} ({current}/{total})", end="", flush=True)

    if current == total:
        print()  # new line when complete

# Simulate a task with manual progress bar
print("=== Manual Progress Bar ===")
total_items = 20
for i in range(total_items + 1):
    manual_progress_bar(i, total_items, description="Processing")
    time.sleep(0.05)  # simulate work

print("Done!\n")

# --- Method 2: Spinner for tasks with unknown duration ---
def spinner_task(seconds=3):
    """Show a spinning animation while working."""
    spinner_chars = ["|", "/", "-", "\\"]  # rotating characters
    end_time = time.time() + seconds

    i = 0
    while time.time() < end_time:
        char = spinner_chars[i % len(spinner_chars)]
        print(f"\r  Working... {char}", end="", flush=True)
        time.sleep(0.1)
        i += 1

    print("\r  Done!            ")  # spaces to clear the spinner

print("=== Spinner (3 seconds) ===")
spinner_task(3)

# --- Method 3: Using tqdm library (much easier!) ---
try:
    from tqdm import tqdm

    print("\n=== tqdm Progress Bar ===")
    for item in tqdm(range(20), desc="Processing", unit="item"):
        time.sleep(0.05)  # simulate work

    print("Done with tqdm!")

except ImportError:
    print("\ntqdm not installed. Run: pip install tqdm")
    print("(tqdm provides much nicer progress bars!)")
