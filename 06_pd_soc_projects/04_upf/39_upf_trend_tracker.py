"""
Project: UPF/Power Analysis Violation Trend Tracker
Tool context: PA Compiler / Voltus
What it does: Tracks UPF/PA violation counts across design iterations.
Monitors convergence of isolation, level-shifter, retention,
and always-on cell issues toward sign-off.

Usage:
    python 39_upf_trend_tracker.py --show
    python 39_upf_trend_tracker.py --add --run RUN_20240115 \
           --iso-missing 2 --ls-missing 3 --ret-missing 1 --ao-errors 0
"""

import json
import argparse
import os
from datetime import datetime

HISTORY_FILE = "upf_trend_history.json"

SAMPLE_HISTORY = [
    {"run":"RUN_20231201","date":"2023-12-01","iso_missing":8,"ls_missing":6,"ret_missing":5,"ao_errors":3},
    {"run":"RUN_20231215","date":"2023-12-15","iso_missing":6,"ls_missing":5,"ret_missing":4,"ao_errors":2},
    {"run":"RUN_20240101","date":"2024-01-01","iso_missing":4,"ls_missing":4,"ret_missing":3,"ao_errors":1},
    {"run":"RUN_20240108","date":"2024-01-08","iso_missing":3,"ls_missing":3,"ret_missing":2,"ao_errors":1},
    {"run":"RUN_20240115","date":"2024-01-15","iso_missing":2,"ls_missing":3,"ret_missing":1,"ao_errors":0},
]


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return SAMPLE_HISTORY


def save_history(h):
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f, indent=2)


def add_run(h, run, iso, ls, ret, ao):
    entry = {
        "run": run, "date": datetime.today().strftime("%Y-%m-%d"),
        "iso_missing": iso, "ls_missing": ls,
        "ret_missing": ret, "ao_errors":  ao,
    }
    h.append(entry)
    save_history(h)
    print(f"Added: {run} — ISO:{iso} LS:{ls} RET:{ret} AO:{ao}")


def show_table(history):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    print("=" * 80)
    print("  UPF / POWER ANALYSIS VIOLATION TREND")
    print("=" * 80)
    print(f"\n  {'RUN':<22} {'DATE':<12} │ "
          f"{'ISO':>6} {'LS':>6} {'RET':>6} {'AO':>6} │ {'TOTAL':>7}")
    print("  " + "-" * 75)

    prev_total = None
    for e in history:
        total = e["iso_missing"] + e["ls_missing"] + e["ret_missing"] + e["ao_errors"]
        trend = ""
        if prev_total is not None:
            d = total - prev_total
            trend = f"▼{abs(d)}" if d < 0 else (f"▲{d}" if d > 0 else "─")
        print(f"  {e['run']:<22} {e['date']:<12} │ "
              f"{e['iso_missing']:>6} {e['ls_missing']:>6} "
              f"{e['ret_missing']:>6} {e['ao_errors']:>6} │ {total:>7}  {trend}")
        prev_total = total

    last = history[-1]
    total_last = last["iso_missing"] + last["ls_missing"] + last["ret_missing"] + last["ao_errors"]

    print(f"\n  Current Open Issues:")
    for label, key in [("Missing Isolation Cells", "iso_missing"),
                        ("Missing Level Shifters",  "ls_missing"),
                        ("Missing Retention",       "ret_missing"),
                        ("Always-On Cell Errors",   "ao_errors")]:
        val = last[key]
        col = RED if val > 0 else GREEN
        print(f"    {label:<30} : {col}{val}{RST}")

    verdict = total_last == 0
    col = GREEN if verdict else RED
    print(f"\n  UPF Sign-Off Status: {col}{'CLEAR' if verdict else 'IN PROGRESS ('+str(total_last)+' issues remain)'}{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Track UPF violation trends")
parser.add_argument("--add",          action="store_true")
parser.add_argument("--run",          help="Run tag")
parser.add_argument("--iso-missing",  type=int, default=0)
parser.add_argument("--ls-missing",   type=int, default=0)
parser.add_argument("--ret-missing",  type=int, default=0)
parser.add_argument("--ao-errors",    type=int, default=0)
parser.add_argument("--show",         action="store_true")
args = parser.parse_args()

history = load_history()
if args.add:
    if not args.run:
        parser.error("--run required")
    add_run(history, args.run,
            getattr(args,"iso_missing",0), getattr(args,"ls_missing",0),
            getattr(args,"ret_missing",0), getattr(args,"ao_errors",0))
else:
    show_table(history)
