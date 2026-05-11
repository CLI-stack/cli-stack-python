"""
Script: Countdown Timer CLI
What it does: A countdown timer you run from the terminal.
Shows remaining time and notifies you when time is up.

Run: python 71_timer_cli.py 60          (60 seconds)
Run: python 71_timer_cli.py 25m         (25 minutes — Pomodoro timer!)
Run: python 71_timer_cli.py 1h30m       (1 hour 30 minutes)
"""

import sys
import time
from datetime import datetime, timedelta

def parse_duration(duration_str):
    """
    Parse a duration string into total seconds.
    Examples: "30" → 30s, "5m" → 300s, "1h30m" → 5400s
    """
    import re
    duration_str = duration_str.strip().lower()

    # Check for just a number (assume seconds)
    if duration_str.isdigit():
        return int(duration_str)

    # Parse hours, minutes, seconds
    total = 0
    hours = re.search(r"(\d+)h", duration_str)
    minutes = re.search(r"(\d+)m", duration_str)
    seconds = re.search(r"(\d+)s", duration_str)

    if hours:
        total += int(hours.group(1)) * 3600
    if minutes:
        total += int(minutes.group(1)) * 60
    if seconds:
        total += int(seconds.group(1))

    return total

def format_time(seconds):
    """Format seconds as HH:MM:SS."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def countdown(total_seconds, label="Timer"):
    """Run a countdown timer."""
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=total_seconds)

    print(f"\n{label}: {format_time(total_seconds)}")
    print(f"Started: {start_time.strftime('%H:%M:%S')}")
    print(f"Ends at: {end_time.strftime('%H:%M:%S')}")
    print("\nPress Ctrl+C to cancel\n")

    try:
        for remaining in range(total_seconds, -1, -1):
            bar_length = 30
            filled = int(bar_length * (total_seconds - remaining) / total_seconds)
            bar = "█" * filled + "░" * (bar_length - filled)
            print(f"\r  [{bar}] {format_time(remaining)} remaining", end="", flush=True)
            if remaining > 0:
                time.sleep(1)

        print(f"\n\n{'=' * 40}")
        print("  ⏰ TIME'S UP! ")
        print(f"{'=' * 40}\n")

    except KeyboardInterrupt:
        print(f"\n\n  Timer cancelled with {format_time(remaining)} remaining.")

# --- Main ---
if len(sys.argv) < 2:
    print("Usage: python 71_timer_cli.py <duration>")
    print("Examples: 30   (30 seconds)")
    print("          5m   (5 minutes)")
    print("          1h30m (1.5 hours)")
    print("\nRunning a 10-second demo:")
    countdown(10, "Demo Timer")
else:
    duration = parse_duration(sys.argv[1])
    if duration <= 0:
        print(f"Invalid duration: {sys.argv[1]}")
    else:
        countdown(duration, f"Timer ({sys.argv[1]})")
