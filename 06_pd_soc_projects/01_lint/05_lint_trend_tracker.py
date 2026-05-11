"""
Project: Lint Violation Trend Tracker
Tool context: Spyglass Lint / Questa Lint
What it does: Tracks lint violation counts across multiple runs over time.
Stores history in a JSON database and plots a trend chart.
Useful for showing closure progress to the design team and management.

Usage:
    python 05_lint_trend_tracker.py --add --run "RUN_20240115" --fatal 1 --error 5 --warning 12 --info 3
    python 05_lint_trend_tracker.py --show
    python 05_lint_trend_tracker.py --plot
"""

import json
import argparse
import os
from datetime import datetime

HISTORY_FILE = "lint_trend_history.json"

# Sample history for demo
SAMPLE_HISTORY = [
    {"run": "RUN_20240101", "date": "2024-01-01", "Fatal": 3, "Error": 24, "Warning": 45, "Info": 12},
    {"run": "RUN_20240108", "date": "2024-01-08", "Fatal": 2, "Error": 18, "Warning": 40, "Info": 10},
    {"run": "RUN_20240115", "date": "2024-01-15", "Fatal": 1, "Error": 10, "Warning": 35, "Info": 9},
    {"run": "RUN_20240122", "date": "2024-01-22", "Fatal": 1, "Error": 6,  "Warning": 28, "Info": 8},
    {"run": "RUN_20240129", "date": "2024-01-29", "Fatal": 0, "Error": 3,  "Warning": 20, "Info": 6},
]


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return SAMPLE_HISTORY


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def add_run(history, run, fatal, error, warning, info):
    entry = {
        "run":     run,
        "date":    datetime.today().strftime("%Y-%m-%d"),
        "Fatal":   fatal,
        "Error":   error,
        "Warning": warning,
        "Info":    info,
    }
    history.append(entry)
    save_history(history)
    total = fatal + error + warning + info
    print(f"Added run '{run}': Fatal={fatal} Error={error} Warning={warning} Info={info} (Total={total})")


def show_table(history):
    print("\n" + "=" * 75)
    print("  LINT VIOLATION TREND")
    print("=" * 75)
    print(f"  {'RUN':<22} {'DATE':<12} {'FATAL':>6} {'ERROR':>7} {'WARN':>7} {'INFO':>6} {'TOTAL':>7}")
    print("  " + "-" * 73)

    prev_total = None
    for entry in history:
        total = entry["Fatal"] + entry["Error"] + entry["Warning"] + entry["Info"]
        if prev_total is not None:
            delta = total - prev_total
            trend = f"▼{abs(delta)}" if delta < 0 else (f"▲{delta}" if delta > 0 else "─")
        else:
            trend = ""
        print(f"  {entry['run']:<22} {entry['date']:<12} "
              f"{entry['Fatal']:>6} {entry['Error']:>7} {entry['Warning']:>7} "
              f"{entry['Info']:>6} {total:>7}  {trend}")
        prev_total = total

    # Show improvement summary
    if len(history) >= 2:
        first = history[0]
        last  = history[-1]
        first_total = first["Fatal"] + first["Error"] + first["Warning"] + first["Info"]
        last_total  = last["Fatal"]  + last["Error"]  + last["Warning"]  + last["Info"]
        reduction   = first_total - last_total
        pct         = reduction / first_total * 100 if first_total else 0
        print(f"\n  Overall improvement: {first_total} → {last_total} violations "
              f"({reduction} fixed, {pct:.1f}% reduction)")


def plot_ascii(history):
    """ASCII bar chart of total violations per run."""
    totals = [(e["run"], e["Fatal"] + e["Error"] + e["Warning"] + e["Info"])
              for e in history]
    max_total = max(t for _, t in totals) if totals else 1
    bar_width  = 40

    print("\n  LINT TREND — ASCII Chart (Total violations per run)")
    print("  " + "-" * 65)
    for run, total in totals:
        bar_len = int(bar_width * total / max_total)
        bar     = "█" * bar_len
        print(f"  {run:<22} | {bar:<40} {total}")
    print()


def plot_matplotlib(history):
    """Plot a proper trend chart using matplotlib if available."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker

        runs    = [e["run"].replace("RUN_", "") for e in history]
        fatals  = [e["Fatal"]   for e in history]
        errors  = [e["Error"]   for e in history]
        warnings= [e["Warning"] for e in history]
        infos   = [e["Info"]    for e in history]

        x = range(len(runs))
        plt.figure(figsize=(10, 5))
        plt.stackplot(x, fatals, errors, warnings, infos,
                      labels=["Fatal", "Error", "Warning", "Info"],
                      colors=["#e74c3c", "#e67e22", "#f1c40f", "#3498db"],
                      alpha=0.8)
        plt.xticks(list(x), runs, rotation=30)
        plt.title("Lint Violation Trend Across Runs")
        plt.xlabel("Run")
        plt.ylabel("Violation Count")
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig("lint_trend.png")
        plt.close()
        print("  Trend chart saved: lint_trend.png")
    except ImportError:
        print("  matplotlib not installed — showing ASCII chart instead.")
        plot_ascii(history)


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Track lint violation trends across runs")
parser.add_argument("--add",     action="store_true", help="Add a new run entry")
parser.add_argument("--run",     help="Run name/tag e.g. RUN_20240115")
parser.add_argument("--fatal",   type=int, default=0)
parser.add_argument("--error",   type=int, default=0)
parser.add_argument("--warning", type=int, default=0)
parser.add_argument("--info",    type=int, default=0)
parser.add_argument("--show",    action="store_true", help="Show trend table")
parser.add_argument("--plot",    action="store_true", help="Plot trend chart")
args = parser.parse_args()

history = load_history()

if args.add:
    if not args.run:
        parser.error("--run is required with --add")
    add_run(history, args.run, args.fatal, args.error, args.warning, args.info)
elif args.plot:
    plot_matplotlib(history)
else:
    # default: show table + ascii chart
    show_table(history)
    plot_ascii(history)
