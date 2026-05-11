"""
Project: UPF / Power Analysis Sign-Off Gate Checker
Tool context: Synopsys PA Compiler / Cadence Voltus
What it does: Checks all UPF sign-off criteria in one gate report:
  - Zero missing isolation cells
  - Zero missing level shifters
  - All retention strategies defined
  - Zero AO cell placement errors
  - All UPF violations waived or fixed
Exits 0 (pass) or 1 (fail) for CI/flow integration.

Usage:
    python 40_upf_signoff_checker.py
    python 40_upf_signoff_checker.py --config upf_signoff.json
"""

import json
import argparse
import sys
from datetime import datetime

DEFAULT_CONFIG = {
    "design": "soc_top",
    "iso_missing":          2,   # missing isolation cells (failing)
    "ls_missing":           0,
    "ret_missing":          1,   # missing retention (failing)
    "ao_cell_errors":       0,
    "pa_violations_fatal":  0,
    "pa_violations_error":  3,
    "pa_unwaived_error":    1,   # unwaived (failing)
    "waivers_count":        10,
    "waivers_approved":     9,   # not all approved (failing)
    # Targets (all must be 0 for sign-off)
    "max_iso_missing":      0,
    "max_ls_missing":       0,
    "max_ret_missing":      0,
    "max_ao_errors":        0,
    "max_pa_unwaived":      0,
    "min_waivers_approved": 1.0,  # 100% of waivers must be approved
}


def run_gates(cfg):
    gates = []

    def gate(name, passed, detail):
        gates.append({"name": name, "passed": passed, "detail": detail})

    gate("G1 — No missing isolation cells",
         cfg["iso_missing"] <= cfg["max_iso_missing"],
         f"Missing ISO cells: {cfg['iso_missing']}  (limit: {cfg['max_iso_missing']})")

    gate("G2 — No missing level shifters",
         cfg["ls_missing"] <= cfg["max_ls_missing"],
         f"Missing LS cells: {cfg['ls_missing']}  (limit: {cfg['max_ls_missing']})")

    gate("G3 — All retention strategies defined",
         cfg["ret_missing"] <= cfg["max_ret_missing"],
         f"Missing retention: {cfg['ret_missing']}  (limit: {cfg['max_ret_missing']})")

    gate("G4 — No always-on cell placement errors",
         cfg["ao_cell_errors"] <= cfg["max_ao_errors"],
         f"AO cell errors: {cfg['ao_cell_errors']}  (limit: {cfg['max_ao_errors']})")

    gate("G5 — No unwaived PA violations",
         cfg["pa_unwaived_error"] <= cfg["max_pa_unwaived"],
         f"Unwaived PA errors: {cfg['pa_unwaived_error']}  (limit: {cfg['max_pa_unwaived']})")

    gate("G6 — All waivers approved",
         cfg["waivers_approved"] == cfg["waivers_count"],
         f"Approved waivers: {cfg['waivers_approved']}/{cfg['waivers_count']}")

    return gates


def print_report(gates, design):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    print("=" * 65)
    print(f"  UPF SIGN-OFF GATE CHECK — {design}")
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
        print(f"  {GREEN}UPF SIGN-OFF: APPROVED ✓{RST}")
    else:
        print(f"  {RED}UPF SIGN-OFF: BLOCKED — {len(failed)} gate(s) failed{RST}")
        for g in failed:
            print(f"    • {g['name']}")
    print("=" * 65)
    return all_pass


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="UPF tapeout sign-off gate checker")
parser.add_argument("--config", help="Sign-off config JSON file")
args = parser.parse_args()

cfg = json.load(open(args.config)) if args.config else DEFAULT_CONFIG
if not args.config:
    print("No config — using built-in defaults.\n")

gates  = run_gates(cfg)
passed = print_report(gates, cfg.get("design", "soc_top"))
sys.exit(0 if passed else 1)
