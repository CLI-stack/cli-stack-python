"""
Project: Tapeout Readiness Checker
Tool context: Cross-flow tapeout gate
What it does: The final gate check before tapeout submission.
Aggregates sign-off status from all flows (Lint, DFT, CDC, RDC, UPF, Timing)
and generates a tapeout readiness report with a PASS/FAIL verdict.
This is the "big red button" script that runs before GDS submission.

Usage:
    python 46_tapeout_readiness_checker.py
    python 46_tapeout_readiness_checker.py --config tapeout_gate.json
"""

import json
import argparse
import sys
from datetime import datetime

DEFAULT_CONFIG = {
    "design":    "soc_top",
    "revision":  "RTL_FREEZE_v1.2",
    "foundry":   "TSMC N5",
    "engineer":  "SoC Design Team",

    # Lint
    "lint_fatal":           0,
    "lint_unwaived_error":  0,
    "lint_waivers_approved":True,

    # DFT
    "sa_coverage":          99.05,
    "tr_coverage":          96.20,
    "ca_coverage":          95.10,
    "scan_chains_ok":       True,
    "mbist_all_pass":       True,

    # CDC
    "cdc_fatal":            0,
    "cdc_unwaived_error":   0,
    "rdc_fatal":            0,
    "rdc_unwaived_error":   0,

    # UPF
    "iso_missing":          0,
    "ls_missing":           0,
    "ret_missing":          0,

    # Timing (from STA)
    "setup_wns_ns":        -0.05,   # failing — still has setup violation
    "hold_wns_ns":          0.0,
    "max_tran_violations":  0,
    "max_cap_violations":   0,

    # Physical
    "drc_violations":       0,
    "lvs_clean":            True,
    "antenna_violations":   12,     # failing

    # Targets
    "target_setup_wns":     0.0,
    "target_hold_wns":      0.0,
    "target_antenna":       0,
}


def run_tapeout_gates(cfg):
    gates = []

    def gate(category, name, passed, detail):
        gates.append({
            "category": category,
            "name":     name,
            "passed":   passed,
            "detail":   detail,
        })

    # ── Lint ──────────────────────────────────────────────────────────────────
    gate("LINT", "Zero Fatal lint violations",
         cfg["lint_fatal"] == 0,
         f"Fatal: {cfg['lint_fatal']}")
    gate("LINT", "Zero unwaived lint errors",
         cfg["lint_unwaived_error"] == 0,
         f"Unwaived errors: {cfg['lint_unwaived_error']}")
    gate("LINT", "All lint waivers approved",
         cfg["lint_waivers_approved"],
         "All approved" if cfg["lint_waivers_approved"] else "Unapproved waivers remain")

    # ── DFT ───────────────────────────────────────────────────────────────────
    gate("DFT", "Stuck-at coverage ≥ 99%",
         cfg["sa_coverage"] >= 99.0,
         f"SA: {cfg['sa_coverage']:.2f}%")
    gate("DFT", "Transition coverage ≥ 96%",
         cfg["tr_coverage"] >= 96.0,
         f"TR: {cfg['tr_coverage']:.2f}%")
    gate("DFT", "MBIST all memories pass",
         cfg["mbist_all_pass"],
         "PASS" if cfg["mbist_all_pass"] else "FAIL — some memories failing")

    # ── CDC/RDC ───────────────────────────────────────────────────────────────
    gate("CDC", "Zero Fatal CDC violations",
         cfg["cdc_fatal"] == 0,
         f"Fatal CDC: {cfg['cdc_fatal']}")
    gate("CDC", "Zero unwaived CDC errors",
         cfg["cdc_unwaived_error"] == 0,
         f"Unwaived CDC: {cfg['cdc_unwaived_error']}")
    gate("RDC", "Zero Fatal RDC violations",
         cfg["rdc_fatal"] == 0,
         f"Fatal RDC: {cfg['rdc_fatal']}")

    # ── UPF ───────────────────────────────────────────────────────────────────
    gate("UPF", "All isolation cells inserted",
         cfg["iso_missing"] == 0,
         f"Missing ISO: {cfg['iso_missing']}")
    gate("UPF", "All level shifters inserted",
         cfg["ls_missing"] == 0,
         f"Missing LS: {cfg['ls_missing']}")

    # ── Timing ────────────────────────────────────────────────────────────────
    gate("TIMING", "Setup timing closed (WNS ≥ 0)",
         cfg["setup_wns_ns"] >= cfg["target_setup_wns"],
         f"WNS: {cfg['setup_wns_ns']:.3f} ns")
    gate("TIMING", "Hold timing closed (WNS ≥ 0)",
         cfg["hold_wns_ns"] >= cfg["target_hold_wns"],
         f"Hold WNS: {cfg['hold_wns_ns']:.3f} ns")

    # ── Physical ──────────────────────────────────────────────────────────────
    gate("PHYSICAL", "DRC clean",
         cfg["drc_violations"] == 0,
         f"DRC violations: {cfg['drc_violations']}")
    gate("PHYSICAL", "LVS clean",
         cfg["lvs_clean"],
         "LVS CLEAN" if cfg["lvs_clean"] else "LVS FAILED")
    gate("PHYSICAL", "Antenna violations resolved",
         cfg["antenna_violations"] <= cfg["target_antenna"],
         f"Antenna violations: {cfg['antenna_violations']}")

    return gates


def print_tapeout_report(gates, cfg):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"
    BOLD  = "\033[1m"

    print("=" * 70)
    print(f"  {BOLD}TAPEOUT READINESS CHECK{RST}")
    print(f"  Design  : {cfg['design']}  Rev: {cfg['revision']}")
    print(f"  Foundry : {cfg['foundry']}")
    print(f"  Date    : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    current_cat = None
    for g in gates:
        if g["category"] != current_cat:
            print(f"\n  ── {g['category']} ──")
            current_cat = g["category"]
        status = f"{GREEN}PASS{RST}" if g["passed"] else f"{RED}FAIL{RST}"
        print(f"    [{status}] {g['name']}")
        print(f"             {g['detail']}")

    all_pass = all(g["passed"] for g in gates)
    failed   = [g for g in gates if not g["passed"]]

    print("\n" + "=" * 70)
    if all_pass:
        print(f"  {GREEN}{BOLD}TAPEOUT READINESS: GO — All gates passed ✓{RST}")
        print(f"  Design is ready for GDS submission.")
    else:
        print(f"  {RED}{BOLD}TAPEOUT READINESS: NO-GO — {len(failed)} gate(s) failed{RST}")
        print(f"\n  Open items before tapeout:")
        for g in failed:
            print(f"    [{g['category']}] {g['name']}: {g['detail']}")
    print("=" * 70)
    return all_pass


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Final tapeout readiness gate check")
parser.add_argument("--config", help="Gate config JSON file")
args = parser.parse_args()

cfg    = json.load(open(args.config)) if args.config else DEFAULT_CONFIG
if not args.config:
    print("No config — using built-in defaults.\n")

gates  = run_tapeout_gates(cfg)
passed = print_tapeout_report(gates, cfg)
sys.exit(0 if passed else 1)
