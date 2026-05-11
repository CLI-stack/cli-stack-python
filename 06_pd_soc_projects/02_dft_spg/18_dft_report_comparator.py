"""
Project: DFT Report Comparator
Tool context: SpyGlass DFT / DFTMAX
What it does: Compares DFT violation reports between two tape-out runs.
Shows new violations (regressions), fixed violations, and coverage delta.
Essential for sign-off milestone tracking.

Usage:
    python 18_dft_report_comparator.py --old run1/dft.rpt --new run2/dft.rpt
"""

import re
import argparse

OLD_REPORT = """\
RULE:DFT_C01 SEVERITY:Error MODULE:cpu_core FILE:rtl/cpu_core.v LINE:245
RULE:DFT_C01 SEVERITY:Error MODULE:dma_ctrl FILE:rtl/dma_ctrl.v LINE:88
RULE:DFT_O01 SEVERITY:Error MODULE:alu_unit FILE:rtl/alu_unit.v LINE:134
RULE:DFT_S01 SEVERITY:Error MODULE:pll_ctrl FILE:rtl/pll_ctrl.v LINE:78
RULE:DFT_S02 SEVERITY:Warning MODULE:fifo_ctrl FILE:rtl/fifo_ctrl.v LINE:200
RULE:DFT_C02 SEVERITY:Warning MODULE:apb_bridge FILE:rtl/apb_bridge.v LINE:67
"""

NEW_REPORT = """\
RULE:DFT_C01 SEVERITY:Error MODULE:cpu_core FILE:rtl/cpu_core.v LINE:245
RULE:DFT_O01 SEVERITY:Error MODULE:alu_unit FILE:rtl/alu_unit.v LINE:134
RULE:DFT_S02 SEVERITY:Warning MODULE:fifo_ctrl FILE:rtl/fifo_ctrl.v LINE:200
RULE:DFT_M01 SEVERITY:Error MODULE:dma_ctrl FILE:rtl/dma_ctrl.v LINE:300
RULE:DFT_M01 SEVERITY:Error MODULE:spi_ctrl FILE:rtl/spi_ctrl.v LINE:145
"""


def parse_to_keys(text):
    """Parse report into a dict of (rule, module, file, line) → severity."""
    pat = re.compile(r"RULE:(\S+)\s+SEVERITY:(\S+)\s+MODULE:(\S+)\s+FILE:(\S+)\s+LINE:(\d+)")
    result = {}
    for m in pat.finditer(text):
        key = (m.group(1), m.group(3), m.group(4), int(m.group(5)))
        result[key] = m.group(2)
    return result


def compare(old, new):
    old_keys = set(old.keys())
    new_keys = set(new.keys())
    return old_keys - new_keys, new_keys - old_keys, old_keys & new_keys


def print_delta(old, new, fixed, new_added, unchanged):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print("=" * 65)
    print("  DFT REPORT DELTA COMPARISON")
    print("=" * 65)
    print(f"\n  Old report : {len(old)} violations")
    print(f"  New report : {len(new)} violations")
    print(f"  Delta      : {len(new) - len(old):+d}")
    print(f"\n  {GREEN}FIXED    : {len(fixed)}{RST}  (resolved violations)")
    print(f"  {RED}NEW      : {len(new_added)}{RST}  (regressions)")
    print(f"  {YEL}REMAIN   : {len(unchanged)}{RST}  (still open)")

    def section(title, keys, source, color):
        if not keys:
            return
        print(f"\n  {color}── {title} ──{RST}")
        print(f"  {'RULE':<12} {'SEV':<9} {'MODULE':<15} {'FILE:LINE'}")
        print("  " + "-" * 65)
        for key in sorted(keys):
            rule, mod, file_, line = key
            sev = source.get(key, "?")
            print(f"  {rule:<12} {sev:<9} {mod:<15} {file_}:{line}")

    section("FIXED VIOLATIONS",       fixed,     old, GREEN)
    section("NEW VIOLATIONS (REGRESSIONS)", new_added, new, RED)
    section("REMAINING VIOLATIONS",   unchanged, old, YEL)

    if not new_added:
        print(f"\n  {GREEN}No regressions introduced. Good progress!{RST}")
    else:
        print(f"\n  {RED}WARNING: {len(new_added)} new DFT violation(s) introduced. "
              f"Review and fix before milestone.{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Compare DFT reports between runs")
parser.add_argument("--old", help="Old DFT report file")
parser.add_argument("--new", help="New DFT report file")
args = parser.parse_args()

old_text = open(args.old).read() if args.old else OLD_REPORT
new_text = open(args.new).read() if args.new else NEW_REPORT
if not args.old:
    print("No files given — using sample data.\n")

old = parse_to_keys(old_text)
new = parse_to_keys(new_text)
fixed, new_added, unchanged = compare(old, new)
print_delta(old, new, fixed, new_added, unchanged)
