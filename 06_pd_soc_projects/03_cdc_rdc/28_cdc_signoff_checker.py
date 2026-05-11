"""
Project: CDC/RDC Sign-Off Gate Checker
Tool context: Spyglass CDC / VC CDC / Spyglass RDC
What it does: Checks all CDC and RDC tapeout sign-off criteria:
  - Zero Fatal CDC violations
  - Zero unwaived CDC Errors
  - Zero Fatal RDC violations
  - All waivers validated
  - Crossing coverage >= target
Integrates with CI: exits 0 (pass) or 1 (fail).

Usage:
    python 28_cdc_signoff_checker.py
    python 28_cdc_signoff_checker.py --config cdc_signoff.json
"""

import json
import argparse
import sys
from datetime import datetime

DEFAULT_CONFIG = {
    "design": "soc_top",
    # CDC measurements
    "cdc_fatal_count":          1,    # intentionally failing
    "cdc_error_count":          0,
    "cdc_warning_count":        8,
    "cdc_unwaived_error_count": 0,
    "cdc_total_crossings":      74,
    "cdc_synced_crossings":     73,
    # RDC measurements
    "rdc_fatal_count":          0,
    "rdc_error_count":          3,
    "rdc_unwaived_error_count": 1,    # intentionally failing
    # Waiver status
    "waiver_count":             12,
    "waivers_approved":         11,
    "waivers_with_justification":11,
    # Targets
    "max_cdc_fatal":            0,
    "max_cdc_unwaived_error":   0,
    "max_rdc_fatal":            0,
    "max_rdc_unwaived_error":   0,
    "min_crossing_coverage_pct":99.0,
}


def run_gates(cfg):
    gates = []

    def gate(name, passed, detail):
        gates.append({"name": name, "passed": passed, "detail": detail})

    # G1: CDC Fatal
    gate("G1 — Zero Fatal CDC violations",
         cfg["cdc_fatal_count"] <= cfg["max_cdc_fatal"],
         f"Fatal CDC: {cfg['cdc_fatal_count']}  (limit: {cfg['max_cdc_fatal']})")

    # G2: CDC unwaived errors
    gate("G2 — Zero unwaived CDC Error violations",
         cfg["cdc_unwaived_error_count"] <= cfg["max_cdc_unwaived_error"],
         f"Unwaived CDC Errors: {cfg['cdc_unwaived_error_count']}")

    # G3: RDC Fatal
    gate("G3 — Zero Fatal RDC violations",
         cfg["rdc_fatal_count"] <= cfg["max_rdc_fatal"],
         f"Fatal RDC: {cfg['rdc_fatal_count']}  (limit: {cfg['max_rdc_fatal']})")

    # G4: RDC unwaived errors
    gate("G4 — Zero unwaived RDC Error violations",
         cfg["rdc_unwaived_error_count"] <= cfg["max_rdc_unwaived_error"],
         f"Unwaived RDC Errors: {cfg['rdc_unwaived_error_count']}")

    # G5: Crossing synchronization coverage
    total  = cfg["cdc_total_crossings"]
    synced = cfg["cdc_synced_crossings"]
    cov    = synced / total * 100 if total else 0
    gate("G5 — Crossing synchronization coverage ≥ target",
         cov >= cfg["min_crossing_coverage_pct"],
         f"Coverage: {synced}/{total} = {cov:.2f}%  (target: {cfg['min_crossing_coverage_pct']}%)")

    # G6: All waivers approved and justified
    gate("G6 — All waivers approved and have justification",
         cfg["waivers_approved"] == cfg["waiver_count"] and
         cfg["waivers_with_justification"] == cfg["waiver_count"],
         f"Approved: {cfg['waivers_approved']}/{cfg['waiver_count']}  "
         f"With justification: {cfg['waivers_with_justification']}/{cfg['waiver_count']}")

    return gates


def print_report(gates, design):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    print("=" * 65)
    print(f"  CDC/RDC SIGN-OFF GATE CHECK — {design}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 65)

    for g in gates:
        status = f"{GREEN}PASS{RST}" if g["passed"] else f"{RED}FAIL{RST}"
        print(f"\n  [{status}] {g['name']}")
        print(f"         {g['detail']}")

    all_pass = all(g["passed"] for g in gates)
    failed   = [g for g in gates if not g["passed"]]

    print("\n" + "=" * 65)
    if all_pass:
        print(f"  {GREEN}CDC/RDC SIGN-OFF: APPROVED ✓{RST}")
    else:
        print(f"  {RED}CDC/RDC SIGN-OFF: BLOCKED — {len(failed)} gate(s) failed{RST}")
        for g in failed:
            print(f"    • {g['name']}")
    print("=" * 65)
    return all_pass


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="CDC/RDC tapeout sign-off checker")
parser.add_argument("--config", help="Sign-off config JSON")
args = parser.parse_args()

cfg    = json.load(open(args.config)) if args.config else DEFAULT_CONFIG
if not args.config:
    print("No config — using built-in defaults.\n")

gates  = run_gates(cfg)
passed = print_report(gates, cfg.get("design", "soc_top"))
sys.exit(0 if passed else 1)
