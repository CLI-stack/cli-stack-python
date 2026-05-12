"""
Project: Git Log Analyzer
What it does: Analyzes a git repository's commit history and generates
statistics: commits per author, activity by day/hour, most changed files,
commit frequency trends. Helps teams understand contribution patterns.

Run: python 42_git_log_analyzer.py  (analyzes current git repo)
Run: python 42_git_log_analyzer.py --repo /path/to/repo --days 30
"""

import subprocess  # to run git commands
import re
import argparse
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta


def run_git_command(args, repo_path="."):
    """
    Execute a git command and return its output as a string.
    subprocess.run() runs an external command and captures output.
    """
    try:
        result = subprocess.run(
            ["git"] + args,                  # e.g. ["git", "log", "--oneline"]
            cwd=repo_path,                   # working directory = the repo
            capture_output=True,             # capture stdout and stderr
            text=True,                       # return as string (not bytes)
            timeout=30                       # don't wait more than 30 seconds
        )
        if result.returncode != 0:
            return None

        return result.stdout.strip()

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def is_git_repo(path):
    """Check if a directory is a git repository."""
    result = run_git_command(["rev-parse", "--is-inside-work-tree"], repo_path=path)
    return result == "true"


def get_commits(repo_path, days=30):
    """
    Get all commits from the last N days.
    Uses git's --format option to output structured data.
    %H = full hash, %an = author name, %ae = author email,
    %ad = author date, %s = subject (first line of commit message)
    """
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Custom format: each field separated by a pipe character
    log_format = "%H|%an|%ae|%ad|%s"
    date_format = "--date=format:%Y-%m-%d %H:%M"

    output = run_git_command(
        ["log",
         f"--since={since_date}",      # only commits after this date
         f"--format={log_format}",     # output format
         date_format,                  # human-readable date format
        ],
        repo_path=repo_path
    )

    if not output:
        return []

    commits = []
    for line in output.split("\n"):
        if "|" not in line:
            continue
        parts = line.split("|", 4)  # split into max 5 parts
        if len(parts) >= 5:
            commits.append({
                "hash":    parts[0],
                "author":  parts[1].strip(),
                "email":   parts[2].strip(),
                "date":    parts[3].strip(),
                "message": parts[4].strip(),
            })

    return commits


def get_changed_files(repo_path, days=30):
    """
    Get files that changed the most in the specified period.
    --name-only outputs just the file names, one per line.
    --diff-filter=M shows only Modified files (not Added/Deleted).
    """
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    output = run_git_command(
        ["log", f"--since={since_date}", "--name-only", "--format="],
        repo_path=repo_path
    )

    if not output:
        return Counter()

    # Count each file's appearance (each appearance = one commit that changed it)
    files = [line.strip() for line in output.split("\n") if line.strip()]
    return Counter(files)


def analyze_activity(commits):
    """Analyze when commits happen (day of week, hour of day)."""
    day_counts  = Counter()
    hour_counts = Counter()

    for commit in commits:
        try:
            dt = datetime.strptime(commit["date"], "%Y-%m-%d %H:%M")
            day_counts[dt.strftime("%A")]   += 1   # Monday, Tuesday, etc.
            hour_counts[dt.hour]            += 1   # 0-23
        except ValueError:
            pass

    return day_counts, hour_counts


def print_git_report(commits, file_counts, repo_path, days):
    """Display the git analysis report."""
    GREEN = "\033[92m"
    YEL   = "\033[33m"
    CYN   = "\033[36m"
    RST   = "\033[0m"

    print("=" * 60)
    print(f"  GIT REPOSITORY ANALYSIS")
    print(f"  Repo: {os.path.abspath(repo_path)}")
    print(f"  Period: last {days} days")
    print("=" * 60)

    if not commits:
        print(f"\n  No commits found in the last {days} days.")
        return

    print(f"\n  Total commits: {len(commits)}")

    # ── Author breakdown ───────────────────────────────────────────────────────
    author_counts = Counter(c["author"] for c in commits)
    print(f"\n  {CYN}Commits by Author:{RST}")
    print(f"  {'AUTHOR':<30} {'COMMITS':>8}  BAR")
    print("  " + "─" * 55)
    max_commits = author_counts.most_common(1)[0][1]
    for author, count in author_counts.most_common(10):
        bar_len = int(20 * count / max_commits)
        bar     = "█" * bar_len
        pct     = count / len(commits) * 100
        print(f"  {author:<30} {count:>8}  {bar} ({pct:.0f}%)")

    # ── Day of week activity ───────────────────────────────────────────────────
    day_counts, hour_counts = analyze_activity(commits)
    print(f"\n  {CYN}Activity by Day of Week:{RST}")
    DAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    max_day = max(day_counts.values()) if day_counts else 1
    for day in DAY_ORDER:
        count   = day_counts.get(day, 0)
        bar_len = int(25 * count / max_day) if max_day else 0
        bar     = "█" * bar_len
        weekend = "  (weekend)" if day in ("Saturday","Sunday") else ""
        print(f"  {day:<12} {count:>4}  {bar}{weekend}")

    # ── Most active hours ──────────────────────────────────────────────────────
    if hour_counts:
        print(f"\n  {CYN}Most Active Hours:{RST}")
        max_hour = max(hour_counts.values())
        for hour in sorted(hour_counts.keys()):
            count   = hour_counts[hour]
            bar_len = int(15 * count / max_hour)
            bar     = "█" * bar_len
            ampm    = "AM" if hour < 12 else "PM"
            h12     = hour % 12 or 12
            print(f"  {h12:>3} {ampm}  {count:>4}  {bar}")

    # ── Most changed files ─────────────────────────────────────────────────────
    if file_counts:
        print(f"\n  {CYN}Most Changed Files (top 10):{RST}")
        max_file = file_counts.most_common(1)[0][1]
        for filename, count in file_counts.most_common(10):
            bar_len = int(20 * count / max_file)
            bar     = "█" * bar_len
            # Shorten long paths
            short_name = filename if len(filename) <= 45 else "..." + filename[-42:]
            print(f"  {short_name:<45} {count:>3}  {bar}")

    # ── Recent commits ─────────────────────────────────────────────────────────
    print(f"\n  {CYN}Recent Commits (last 10):{RST}")
    print(f"  {'DATE':<17} {'AUTHOR':<20} {'MESSAGE'}")
    print("  " + "─" * 75)
    for commit in commits[:10]:
        date    = commit["date"][:16]     # "2024-01-15 14:30"
        author  = commit["author"][:18]
        message = commit["message"][:45]
        print(f"  {date:<17} {author:<20} {message}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Analyze git repository commit history")
parser.add_argument("--repo", default=".", help="Path to git repository (default: current dir)")
parser.add_argument("--days", type=int, default=30, help="Analyze last N days (default: 30)")
args = parser.parse_args()

print("=== Git Log Analyzer ===\n")

if not is_git_repo(args.repo):
    print(f"Not a git repository: {os.path.abspath(args.repo)}")
    print("Run this script from inside a git repository, or use --repo /path/to/repo")
else:
    print(f"Analyzing: {os.path.abspath(args.repo)} (last {args.days} days)...")
    commits     = get_commits(args.repo, args.days)
    file_counts = get_changed_files(args.repo, args.days)
    print_git_report(commits, file_counts, args.repo, args.days)
