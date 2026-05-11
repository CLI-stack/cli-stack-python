"""
Project: Fault Coverage Tracker (Multi-Run History)
Tool context: TetraMAX / DFTMAX
What it does: Tracks DFT fault coverage across multiple ATPG runs.
Stores history in JSON and shows a trend table with pass/fail status
against the sign-off target. Useful for monitoring closure progress.

Usage:
    python 15_fault_coverage_tracker.py --add --run RUN_20240115 \
           --sa 98.78 --tr 95.40 --ca 92.10 --patterns 8633
    python 15_fault_coverage_tracker.py --show
    python 15_fault_coverage_tracker.py --show --target-sa 99.0 --target-tr 96.0
"""

import json
import argparse
import os
from datetime import datetime

HISTORY_FILE = "dft_coverage_history.json"

SAMPLE_HISTORY = [
    {"run": "RUN_20231201", "date": "2023-12-01", "sa": 97.20, "tr": 93.10, "ca": 89.50, "patterns": 9200},
    {"run": "RUN_20231215", "date": "2023-12-15", "sa": 97.85, "tr": 94.30, "ca": 90.80, "patterns": 8900},
    {"run": "RUN_20240101", "date": "2024-01-01", "sa": 98.10, "tr": 94.80, "ca": 91.40, "patterns": 8800},
    {"run": "RUN_20240108", "date": "2024-01-08", "sa": 98.50, "tr": 95.10, "ca": 91.90, "patterns": 8700},
    {"run": "RUN_20240115", "date": "2024-01-15", "sa": 98.78, "tr": 95.40, "ca": 92.10, "patterns": 8633},
]

TARGETS = {"sa": 99.0, "tr": 96.0, "ca": 95.0}


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return SAMPLE_HISTORY


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def add_run(history, run, sa, tr, ca, patterns):
    entry = {
        "run":      run,
        "date":     datetime.today().strftime("%Y-%m-%d"),
        "sa":       sa,
        "tr":       tr,
        "ca":       ca,
        "patterns": patterns,
    }
    history.append(entry)
    save_history(history)
    print(f"Added: {run} — SA:{sa}% TR:{tr}% CA:{ca}% Patterns:{patterns}")


def show_table(history, targets):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    def c(val, target):
        return f"{GREEN}{val:.2f}%{RST}" if val >= target else f"{RED}{val:.2f}%{RST}"

    print("=" * 85)
    print("  DFT FAULT COVERAGE TREND")
    print(f"  Targets — SA: {targets['sa']}%  TR: {targets['tr']}%  CA: {targets['ca']}%")
    print("=" * 85)
    print(f"\n  {'RUN':<22} {'DATE':<12} {'SA COV':>10} {'TR COV':>10} "
          f"{'CA COV':>10} {'PATTERNS':>10}")
    print("  " + "-" * 80)

    for e in history:
        print(f"  {e['run']:<22} {e['date']:<12} "
              f"{c(e['sa'], targets['sa']):>19} "
              f"{c(e['tr'], targets['tr']):>19} "
              f"{c(e['ca'], targets['ca']):>19} "
              f"{e['patterns']:>10,}")

    # Show improvement
    if len(history) >= 2:
        first, last = history[0], history[-1]
        print(f"\n  Improvement from first to last run:")
        for fm, label in [("sa","SA"), ("tr","TR"), ("ca","CA")]:
            delta = last[fm] - first[fm]
            color = GREEN if delta >= 0 else RED
            print(f"    {label}: {first[fm]:.2f}% → {last[fm]:.2f}%  "
                  f"({color}+{delta:.2f}%{RST})")

    # Final sign-off status
    last = history[-1]
    print(f"\n  Current Sign-off Status:")
    all_pass = True
    for fm, label, target in [("sa","Stuck-At",targets["sa"]),
                                ("tr","Transition",targets["tr"]),
                                ("ca","Cell-Aware",targets["ca"])]:
        passed = last[fm] >= target
        if not passed:
            all_pass = False
        status = f"{GREEN}PASS{RST}" if passed else f"{RED}FAIL (need +{target-last[fm]:.2f}%){RST}"
        print(f"    {label:<15}: {status}")

    print(f"\n  {'DFT SIGN-OFF: '+GREEN+'PASS'+RST if all_pass else 'DFT SIGN-OFF: '+RED+'BLOCKED'+RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Track DFT fault coverage across runs")
parser.add_argument("--add",        action="store_true")
parser.add_argument("--run",        help="Run tag")
parser.add_argument("--sa",         type=float, default=0.0, help="Stuck-at coverage %%")
parser.add_argument("--tr",         type=float, default=0.0, help="Transition coverage %%")
parser.add_argument("--ca",         type=float, default=0.0, help="Cell-aware coverage %%")
parser.add_argument("--patterns",   type=int,   default=0)
parser.add_argument("--show",       action="store_true")
parser.add_argument("--target-sa",  type=float, default=TARGETS["sa"])
parser.add_argument("--target-tr",  type=float, default=TARGETS["tr"])
parser.add_argument("--target-ca",  type=float, default=TARGETS["ca"])
args = parser.parse_args()

history = load_history()
targets = {"sa": args.target_sa, "tr": args.target_tr, "ca": args.target_ca}

if args.add:
    if not args.run:
        parser.error("--run is required with --add")
    add_run(history, args.run, args.sa, args.tr, args.ca, args.patterns)
else:
    if not args.show:
        print("No action specified — showing table by default.\n")
    show_table(history, targets)
