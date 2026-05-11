"""
Project: CDC/RDC Violation Trend Tracker
Tool context: Spyglass CDC / VC CDC
What it does: Tracks CDC and RDC violation counts across design iterations.
Shows convergence trend toward sign-off. Stores history in JSON.

Usage:
    python 26_cdc_trend_tracker.py --add --run RUN_20240115 \
           --cdc-fatal 1 --cdc-error 5 --cdc-warning 8 \
           --rdc-error 3 --rdc-warning 2
    python 26_cdc_trend_tracker.py --show
"""

import json
import argparse
import os
from datetime import datetime

HISTORY_FILE = "cdc_rdc_history.json"

SAMPLE_HISTORY = [
    {"run": "RUN_20231201", "date": "2023-12-01",
     "cdc_fatal":3, "cdc_error":18, "cdc_warning":25, "rdc_error":8, "rdc_warning":5},
    {"run": "RUN_20231215", "date": "2023-12-15",
     "cdc_fatal":2, "cdc_error":14, "cdc_warning":20, "rdc_error":6, "rdc_warning":4},
    {"run": "RUN_20240101", "date": "2024-01-01",
     "cdc_fatal":1, "cdc_error":10, "cdc_warning":15, "rdc_error":4, "rdc_warning":3},
    {"run": "RUN_20240108", "date": "2024-01-08",
     "cdc_fatal":1, "cdc_error": 7, "cdc_warning":12, "rdc_error":3, "rdc_warning":2},
    {"run": "RUN_20240115", "date": "2024-01-15",
     "cdc_fatal":1, "cdc_error": 5, "cdc_warning": 8, "rdc_error":3, "rdc_warning":2},
]


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return SAMPLE_HISTORY


def save_history(h):
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f, indent=2)


def add_run(h, run, cdc_fatal, cdc_error, cdc_warning, rdc_error, rdc_warning):
    entry = {
        "run": run, "date": datetime.today().strftime("%Y-%m-%d"),
        "cdc_fatal": cdc_fatal, "cdc_error": cdc_error, "cdc_warning": cdc_warning,
        "rdc_error": rdc_error, "rdc_warning": rdc_warning,
    }
    h.append(entry)
    save_history(h)
    print(f"Added: {run} — CDC: Fatal={cdc_fatal} Err={cdc_error} Warn={cdc_warning} | "
          f"RDC: Err={rdc_error} Warn={rdc_warning}")


def show_table(history):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    print("=" * 90)
    print("  CDC / RDC VIOLATION TREND")
    print("=" * 90)
    print(f"\n  {'RUN':<22} {'DATE':<12} │ "
          f"{'CDC-FAT':>8} {'CDC-ERR':>8} {'CDC-WRN':>8} │ "
          f"{'RDC-ERR':>8} {'RDC-WRN':>8} │ {'TOTAL':>7}")
    print("  " + "-" * 88)

    prev_total = None
    for e in history:
        total = (e["cdc_fatal"] + e["cdc_error"] + e["cdc_warning"] +
                 e["rdc_error"] + e["rdc_warning"])
        trend = ""
        if prev_total is not None:
            d = total - prev_total
            trend = f"▼{abs(d)}" if d < 0 else (f"▲{d}" if d > 0 else "─")
        print(f"  {e['run']:<22} {e['date']:<12} │ "
              f"{e['cdc_fatal']:>8} {e['cdc_error']:>8} {e['cdc_warning']:>8} │ "
              f"{e['rdc_error']:>8} {e['rdc_warning']:>8} │ {total:>7}  {trend}")
        prev_total = total

    if len(history) >= 2:
        first = history[0]
        last  = history[-1]
        ft = (first["cdc_fatal"] + first["cdc_error"] + first["cdc_warning"] +
              first["rdc_error"] + first["rdc_warning"])
        lt = (last["cdc_fatal"] + last["cdc_error"] + last["cdc_warning"] +
              last["rdc_error"] + last["rdc_warning"])
        reduction = ft - lt
        pct = reduction / ft * 100 if ft else 0
        print(f"\n  Overall reduction: {ft} → {lt} violations "
              f"({reduction} fixed, {pct:.1f}%)")

    last = history[-1]
    print(f"\n  Current Status:")
    if last["cdc_fatal"] > 0:
        print(f"  {RED}BLOCKED — {last['cdc_fatal']} Fatal CDC violation(s) remain.{RST}")
    elif last["cdc_error"] > 0:
        print(f"  {RED}IN PROGRESS — {last['cdc_error']} CDC Error(s) remain.{RST}")
    else:
        print(f"  {GREEN}CDC Errors cleared — review remaining Warnings.{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Track CDC/RDC violation trends")
parser.add_argument("--add",         action="store_true")
parser.add_argument("--run",         help="Run tag")
parser.add_argument("--cdc-fatal",   type=int, default=0)
parser.add_argument("--cdc-error",   type=int, default=0)
parser.add_argument("--cdc-warning", type=int, default=0)
parser.add_argument("--rdc-error",   type=int, default=0)
parser.add_argument("--rdc-warning", type=int, default=0)
parser.add_argument("--show",        action="store_true")
args = parser.parse_args()

history = load_history()

if args.add:
    if not args.run:
        parser.error("--run required with --add")
    add_run(history, args.run,
            getattr(args, "cdc_fatal", 0), getattr(args, "cdc_error", 0),
            getattr(args, "cdc_warning", 0),
            getattr(args, "rdc_error", 0), getattr(args, "rdc_warning", 0))
else:
    show_table(history)
