"""
Project: Scan Insertion Completeness Checker
Tool context: Synopsys DFTMAX / Tessent
What it does: Parses a scan insertion summary report and verifies that
all flip-flops are scan-stitched, no cells were excluded unintentionally,
and all scan chains are properly terminated with SI/SO ports.

Usage:
    python 20_scan_insertion_checker.py --report scan_summary.rpt
"""

import re
import argparse

SAMPLE_REPORT = """\
# Scan Insertion Summary Report — DFTMAX
# Design: soc_top
# Date: 2024-01-15

========================================
FLIP-FLOP SCAN STITCHING SUMMARY
========================================

Total flip-flops in design   : 52480
Scan-stitched flip-flops     : 48520
Excluded flip-flops          : 3960
  Reason: async_reset        :   540   (cells with async reset, need review)
  Reason: black_box          :  1200   (inside IP black boxes — expected)
  Reason: scan_exclude attr  :  2220   (intentionally excluded via SDC attr)

Scan efficiency              : 92.45%  (48520 / 52480)

========================================
SCAN CHAIN TERMINATION CHECK
========================================

Chain  1 : SI=scan_si[0]   SO=scan_so[0]  Terminated=YES
Chain  2 : SI=scan_si[1]   SO=scan_so[1]  Terminated=YES
Chain  3 : SI=scan_si[2]   SO=scan_so[2]  Terminated=YES
Chain  4 : SI=scan_si[3]   SO=scan_so[3]  Terminated=YES
Chain  5 : SI=scan_si[4]   SO=scan_so[4]  Terminated=YES
Chain  6 : SI=scan_si[5]   SO=scan_so[5]  Terminated=YES
Chain  7 : SI=scan_si[6]   SO=scan_so[6]  Terminated=YES
Chain  8 : SI=scan_si[7]   SO=scan_so[7]  Terminated=NO  (open SO pin!)

========================================
EXCLUDED CELLS DETAIL (async_reset)
========================================

cpu_core/rst_sync/rst_dff[0]   DFFR   async_reset
cpu_core/rst_sync/rst_dff[1]   DFFR   async_reset
pll_ctrl/pll_lock_reg           DFFRA  async_reset
"""


def parse_scan_summary(text):
    results = {}

    # Global metrics
    for key, pat in [
        ("total_ff",      r"Total flip-flops in design\s*:\s*(\d+)"),
        ("stitched_ff",   r"Scan-stitched flip-flops\s*:\s*(\d+)"),
        ("excluded_ff",   r"Excluded flip-flops\s*:\s*(\d+)"),
        ("async_reset",   r"Reason: async_reset\s*:\s*(\d+)"),
        ("black_box",     r"Reason: black_box\s*:\s*(\d+)"),
        ("scan_exclude",  r"Reason: scan_exclude attr\s*:\s*(\d+)"),
        ("efficiency",    r"Scan efficiency\s*:\s*([\d.]+)%"),
    ]:
        m = re.search(pat, text)
        if m:
            val = m.group(1)
            results[key] = float(val) if "." in val else int(val)

    # Chain termination check
    chain_pat = re.compile(
        r"Chain\s+(\d+)\s*:\s*SI=(\S+)\s+SO=(\S+)\s+Terminated=(\S+)"
    )
    chains = []
    for m in chain_pat.finditer(text):
        terminated = m.group(4).upper() == "YES"
        chains.append({
            "id":         int(m.group(1)),
            "si":         m.group(2),
            "so":         m.group(3),
            "terminated": terminated,
            "note":       "" if terminated else m.group(4).replace("YES","").replace("NO","").strip(),
        })

    # Async reset cells
    async_cells = re.findall(r"(\S+/\S+)\s+\S+\s+async_reset", text)

    return results, chains, async_cells


def check_insertion(results, chains, async_cells):
    RED   = "\033[91m"
    GREEN = "\033[92m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    issues = []

    print("=" * 65)
    print("  SCAN INSERTION COMPLETENESS CHECK")
    print("=" * 65)

    # Metric summary
    total    = results.get("total_ff",    0)
    stitched = results.get("stitched_ff", 0)
    excluded = results.get("excluded_ff", 0)
    eff      = results.get("efficiency",  0.0)

    print(f"\n  Total FFs            : {total:,}")
    print(f"  Scan-stitched FFs    : {stitched:,}")
    print(f"  Excluded FFs         : {excluded:,}")
    print(f"    - Async reset      : {results.get('async_reset', 0)}")
    print(f"    - Black box        : {results.get('black_box', 0)}")
    print(f"    - scan_exclude     : {results.get('scan_exclude', 0)}")
    eff_color = GREEN if eff >= 90.0 else YEL if eff >= 80.0 else RED
    print(f"  Scan efficiency      : {eff_color}{eff:.2f}%{RST}  (target ≥ 90%)")

    if eff < 90.0:
        issues.append(f"Scan efficiency {eff:.2f}% < 90%")

    # Chain termination check
    print(f"\n  Chain Termination Check:")
    unterminated = [c for c in chains if not c["terminated"]]
    for c in chains:
        status = f"{GREEN}OK{RST}" if c["terminated"] else f"{RED}OPEN SO PIN!{RST}"
        print(f"    Chain {c['id']:>2}: SI={c['si']:<15} SO={c['so']:<15} {status}")

    if unterminated:
        for c in unterminated:
            issues.append(f"Chain {c['id']} has open SO pin: {c['so']}")

    # Async reset cells
    if async_cells:
        print(f"\n  Async Reset Excluded Cells ({len(async_cells)}):")
        for cell in async_cells[:5]:
            print(f"    {cell}")
        if len(async_cells) > 5:
            print(f"    ... and {len(async_cells) - 5} more")
        print(f"  Action: Verify these cells are intentionally excluded or "
              f"make reset synchronous.")

    # Final verdict
    print(f"\n  Gate Results:")
    if not issues:
        print(f"  {GREEN}SCAN INSERTION CHECK: PASS{RST}")
    else:
        print(f"  {RED}SCAN INSERTION CHECK: FAIL — {len(issues)} issue(s){RST}")
        for issue in issues:
            print(f"    • {issue}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Check scan insertion completeness")
parser.add_argument("--report", help="Scan insertion summary report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

results, chains, async_cells = parse_scan_summary(text)
check_insertion(results, chains, async_cells)
