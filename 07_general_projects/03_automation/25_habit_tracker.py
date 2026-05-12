"""
Project: Habit Tracker with Streaks
What it does: Tracks daily habits and calculates streak counts.
A "streak" is how many consecutive days you've completed a habit.
Research shows that tracking streaks motivates people to maintain habits.

Run: python 25_habit_tracker.py  (shows dashboard)
Run: python 25_habit_tracker.py check "Exercise"
Run: python 25_habit_tracker.py add "Read 30 minutes"
Run: python 25_habit_tracker.py history
"""

import json
import os
import argparse
from datetime import datetime, timedelta


DATA_FILE = "habits.json"


def load_data():
    """Load habit data from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    # Default habits for first run
    return {
        "habits": [
            {"name": "Exercise",         "emoji": "💪"},
            {"name": "Read 30 minutes",  "emoji": "📚"},
            {"name": "Drink 8 glasses",  "emoji": "💧"},
            {"name": "No social media",  "emoji": "🚫"},
            {"name": "Sleep 8 hours",    "emoji": "😴"},
        ],
        "completions": {}   # {habit_name: [list of date strings "YYYY-MM-DD"]}
    }


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def calculate_streak(dates):
    """
    Calculate the current consecutive day streak.
    Works by checking: did I complete this habit today? Yesterday? Day before?
    Stops counting when it finds a gap.
    """
    if not dates:
        return 0

    # Convert date strings to date objects and sort (newest first)
    date_objects = sorted([datetime.strptime(d, "%Y-%m-%d").date() for d in dates],
                          reverse=True)

    today     = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # Streak only counts if the habit was done today OR yesterday
    # (we don't break the streak just because today isn't over yet)
    if date_objects[0] < yesterday:
        return 0  # last completion was more than 1 day ago — streak broken

    streak = 1
    # Count backwards: each date must be exactly 1 day before the previous
    for i in range(1, len(date_objects)):
        expected_prev = date_objects[i-1] - timedelta(days=1)  # the day before
        if date_objects[i] == expected_prev:
            streak += 1
        else:
            break  # gap found — streak ends

    return streak


def check_habit(data, habit_name):
    """Mark a habit as complete for today."""
    today    = datetime.now().strftime("%Y-%m-%d")
    habit_names = [h["name"] for h in data["habits"]]

    if habit_name not in habit_names:
        print(f"Habit '{habit_name}' not found.")
        print(f"Available habits: {', '.join(habit_names)}")
        return

    # Initialize the completion list for this habit if it doesn't exist
    if habit_name not in data["completions"]:
        data["completions"][habit_name] = []

    completion_list = data["completions"][habit_name]

    if today in completion_list:
        print(f"'{habit_name}' is already checked for today!")
        return

    completion_list.append(today)
    save_data(data)

    streak = calculate_streak(completion_list)
    print(f"✓ Checked: '{habit_name}' for {today}")
    print(f"  Current streak: {streak} day(s)")
    if streak >= 7:
        print(f"  🔥 Amazing! {streak}-day streak!")


def add_habit(data, habit_name, emoji="✅"):
    """Add a new habit to track."""
    existing_names = [h["name"] for h in data["habits"]]
    if habit_name in existing_names:
        print(f"Habit '{habit_name}' already exists.")
        return

    data["habits"].append({"name": habit_name, "emoji": emoji})
    save_data(data)
    print(f"Added new habit: {emoji} {habit_name}")


def show_dashboard(data):
    """Display today's habit completion status with streaks."""
    today     = datetime.now().strftime("%Y-%m-%d")
    today_str = datetime.now().strftime("%A, %B %d, %Y")

    print(f"\n{'='*55}")
    print(f"  HABIT TRACKER — {today_str}")
    print(f"{'='*55}\n")

    total    = len(data["habits"])
    done_today = 0

    for habit in data["habits"]:
        name        = habit["name"]
        emoji       = habit.get("emoji", "✅")
        completions = data["completions"].get(name, [])
        done        = today in completions
        streak      = calculate_streak(completions)
        total_days  = len(completions)  # total completions all time

        if done:
            status = "\033[92m✓ DONE\033[0m"
            done_today += 1
        else:
            status = "\033[90m○ TODO\033[0m"

        # Show streak with fire emoji for long streaks
        streak_display = f"{streak}🔥" if streak >= 7 else f"{streak}d"

        print(f"  {emoji} {name:<25} {status}  streak:{streak_display:>4}  total:{total_days}")

    print(f"\n  Progress: {done_today}/{total} habits done today")

    # Progress bar
    if total > 0:
        pct = done_today / total
        bar = "█" * int(pct * 30) + "░" * (30 - int(pct * 30))
        print(f"  [{bar}] {pct*100:.0f}%")


def show_history(data, days=7):
    """Show a calendar grid of habit completions for the past N days."""
    print(f"\n  Habit History (last {days} days):\n")

    # Generate the past N days
    past_dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                  for i in range(days-1, -1, -1)]

    # Header row: date labels
    print(f"  {'HABIT':<25}", end="")
    for d in past_dates:
        print(f" {d[8:]:>4}", end="")  # just show day number (e.g. "15")
    print()
    print("  " + "─" * (25 + days * 5))

    for habit in data["habits"]:
        name        = habit["name"]
        completions = set(data["completions"].get(name, []))  # set for O(1) lookup

        print(f"  {name:<25}", end="")
        for date in past_dates:
            # ● = done that day, ○ = missed, · = future
            if date in completions:
                print(f" {'●':>4}", end="")   # completed
            else:
                print(f" {'○':>4}", end="")   # not completed
        print()


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Daily habit tracker with streaks")
subparsers = parser.add_subparsers(dest="command")

check_p = subparsers.add_parser("check", help="Mark a habit as done today")
check_p.add_argument("habit", nargs="+", help="Habit name (can be multi-word)")

add_p = subparsers.add_parser("add", help="Add a new habit")
add_p.add_argument("habit", nargs="+")
add_p.add_argument("--emoji", default="✅")

subparsers.add_parser("history", help="Show completion history")
args = parser.parse_args()

data = load_data()

if args.command == "check":
    check_habit(data, " ".join(args.habit))
elif args.command == "add":
    add_habit(data, " ".join(args.habit), args.emoji)
elif args.command == "history":
    show_history(data)
else:
    show_dashboard(data)

# Clean up demo data
if os.path.exists(DATA_FILE):
    os.remove(DATA_FILE)
