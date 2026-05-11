"""
Project: DFT Sign-Off Gate Checker
Tool context: SpyGlass DFT / TetraMAX / STAR Memory System
What it does: Checks all DFT tapeout sign-off criteria in one place:
  - Stuck-at fault coverage >= target
  - Transition fault coverage >= target
  - Zero unwaived DFT DRC errors
  - MBIST all memories passing
  - Scan chain imbalance within limit
Exits with code 0 (pass) or 1 (fail) for CI integration.

Usage:
    python 19_dft_signoff_checker.py --config dft_signoff.json
"""

import json
import argparse
import sys
from datetime import datetime

# Default sign-off targets
DEFAULT_CONFIG = {
    "design":               "soc_top",
    "sa_coverage_target":   99.0,
    "tr_coverage_target":   96.0,
    "ca_coverage_target":   95.0,
    "max_unwaived_drc":     0,
    "max_scan_imbalance_pct": 10.0,
    "mbist_all_pass":       True,
    # Actual measured values (would be parsed from reports in real flow)
    "sa_coverage_actual":   98.78,
    "tr_coverage_actual":   95.40,
    "ca_coverage_actual":   92.10,
    "unwaived_drc_count":   0,
    "scan_imbalance_pct":   14.8,  # intentionally failing for demo
    "mbist_pass_count":     4,
    "mbist_total_count":    5,     # one failing
}


def load_config(path):
    with open(path) as f:
        return json.load(f)


def run_gates(cfg):
    gates   = []
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    RST     = "\033[0m"

    def gate(name, passed, detail):
        gates.append({"name": name, "passed": passed, "detail": detail})

    # G1: Stuck-at fault coverage
    sa  = cfg["sa_coverage_actual"]
    tgt = cfg["sa_coverage_target"]
    gate("G1 — Stuck-at fault coverage ≥ target",
         sa >= tgt,
         f"Actual: {sa:.2f}%  Target: {tgt:.2f}%")

    # G2: Transition fault coverage
    tr  = cfg["tr_coverage_actual"]
    tgt = cfg["tr_coverage_target"]
    gate("G2 — Transition fault coverage ≥ target",
         tr >= tgt,
         f"Actual: {tr:.2f}%  Target: {tgt:.2f}%")

    # G3: Cell-aware coverage
    ca  = cfg["ca_coverage_actual"]
    tgt = cfg["ca_coverage_target"]
    gate("G3 — Cell-aware fault coverage ≥ target",
         ca >= tgt,
         f"Actual: {ca:.2f}%  Target: {tgt:.2f}%")

    # G4: DFT DRC violations
    drc     = cfg["unwaived_drc_count"]
    max_drc = cfg["max_unwaived_drc"]
    gate("G4 — Zero unwaived DFT DRC violations",
         drc <= max_drc,
         f"Unwaived DRC count: {drc}  (limit: {max_drc})")

    # G5: Scan chain imbalance
    imbal = cfg["scan_imbalance_pct"]
    limit = cfg["max_scan_imbalance_pct"]
    gate("G5 — Scan chain imbalance within limit",
         imbal <= limit,
         f"Imbalance: {imbal:.1f}%  (limit: {limit:.1f}%)")

    # G6: MBIST all pass
    mbist_pass  = cfg["mbist_pass_count"]
    mbist_total = cfg["mbist_total_count"]
    gate("G6 — All MBIST memories pass",
         mbist_pass == mbist_total,
         f"Passing: {mbist_pass}/{mbist_total} memories")

    return gates


def print_report(gates, design):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    print("=" * 65)
    print(f"  DFT SIGN-OFF GATE CHECK — {design}")
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
        print(f"  {GREEN}DFT SIGN-OFF: APPROVED ✓{RST}")
    else:
        print(f"  {RED}DFT SIGN-OFF: BLOCKED — {len(failed)} gate(s) failed{RST}")
        print(f"\n  Failed gates:")
        for g in failed:
            print(f"    • {g['name']}")
    print("=" * 65)

    return all_pass


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="DFT tapeout sign-off gate checker")
parser.add_argument("--config", help="Sign-off config JSON file")
args = parser.parse_args()

cfg = load_config(args.config) if args.config else DEFAULT_CONFIG
if not args.config:
    print("No config file — using built-in defaults.\n")

gates  = run_gates(cfg)
passed = print_report(gates, cfg.get("design", "soc_top"))
sys.exit(0 if passed else 1)
