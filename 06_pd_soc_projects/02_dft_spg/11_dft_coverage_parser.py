"""
Project: DFT Fault Coverage Parser
Tool context: Synopsys TetraMAX / DFTMAX / SpyGlass DFT
What it does: Parses an ATPG/DFT fault coverage report and extracts
stuck-at fault coverage, ATPG pattern count, and undetected fault list.
Gives a quick pass/fail against the tapeout coverage target.

Usage:
    python 11_dft_coverage_parser.py --report atpg_coverage.rpt
    python 11_dft_coverage_parser.py --report atpg_coverage.rpt --target 99.0
"""

import re
import argparse

# Simulated TetraMAX-style ATPG report
SAMPLE_REPORT = """\
# TetraMAX ATPG Report
# Design: soc_top
# Date: 2024-01-15

====================================
 ATPG FAULT COVERAGE SUMMARY
====================================

 Fault class      : Stuck-at
 Total faults     : 285340
 Detected faults  : 281872
 Undetected faults:   3468
 ATPG untestable  :   1200
 Fault coverage   :  98.78 %
 Test coverage    :  99.20 %
 Pattern count    :   4215

====================================
 UNDETECTED FAULT LIST (Top 20)
====================================
 cpu_core/alu/adder/carry_out                  SA0
 cpu_core/alu/adder/carry_out                  SA1
 dma_ctrl/fifo/rd_ptr[3]                       SA0
 dma_ctrl/fifo/rd_ptr[3]                       SA1
 apb_bridge/decoder/sel_out[7]                 SA1
 pll_ctrl/divider/clk_div[0]                   SA0
 pll_ctrl/divider/clk_div[0]                   SA1
 uart_ctrl/tx_fsm/state[2]                     SA0
 uart_ctrl/tx_fsm/state[2]                     SA1
 spi_ctrl/shift_reg/bit_cnt[3]                 SA0
"""


def parse_coverage_report(text):
    """Extract key metrics from ATPG coverage report."""
    metrics = {}

    patterns = {
        "fault_class":   r"Fault class\s*:\s*(.+)",
        "total_faults":  r"Total faults\s*:\s*(\d+)",
        "detected":      r"Detected faults\s*:\s*(\d+)",
        "undetected":    r"Undetected faults\s*:\s*(\d+)",
        "untestable":    r"ATPG untestable\s*:\s*(\d+)",
        "fault_cov":     r"Fault coverage\s*:\s*([\d.]+)\s*%",
        "test_cov":      r"Test coverage\s*:\s*([\d.]+)\s*%",
        "pattern_count": r"Pattern count\s*:\s*(\d+)",
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, text)
        if m:
            val = m.group(1).strip()
            # Convert numeric fields
            if key in ("total_faults", "detected", "undetected", "untestable", "pattern_count"):
                metrics[key] = int(val)
            elif key in ("fault_cov", "test_cov"):
                metrics[key] = float(val)
            else:
                metrics[key] = val

    # Extract undetected faults
    undetected_faults = []
    in_undetected = False
    for line in text.splitlines():
        if "UNDETECTED FAULT LIST" in line:
            in_undetected = True
            continue
        if in_undetected and line.strip() and not line.startswith("#") and not line.startswith("="):
            parts = line.split()
            if len(parts) >= 2:
                undetected_faults.append({"net": parts[0], "type": parts[1]})

    return metrics, undetected_faults


def print_report(metrics, undetected_faults, target):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print("=" * 60)
    print("  DFT FAULT COVERAGE REPORT")
    print("=" * 60)

    fc = metrics.get("fault_cov", 0)
    tc = metrics.get("test_cov",  0)

    cov_color = GREEN if fc >= target else RED
    print(f"\n  Fault Class      : {metrics.get('fault_class','N/A')}")
    print(f"  Total Faults     : {metrics.get('total_faults', 0):>10,}")
    print(f"  Detected         : {metrics.get('detected', 0):>10,}")
    print(f"  Undetected       : {metrics.get('undetected', 0):>10,}")
    print(f"  ATPG Untestable  : {metrics.get('untestable', 0):>10,}")
    print(f"  Pattern Count    : {metrics.get('pattern_count', 0):>10,}")
    print(f"\n  Fault Coverage   : {cov_color}{fc:>7.2f}%{RST}  (target: {target}%)")
    print(f"  Test Coverage    : {tc:>8.2f}%")

    if fc >= target:
        print(f"\n  {GREEN}COVERAGE GATE: PASS — Target {target}% met.{RST}")
    else:
        gap = target - fc
        print(f"\n  {RED}COVERAGE GATE: FAIL — {gap:.2f}% below target.{RST}")
        print(f"  Action: Review undetected faults and add targeted patterns.")

    # Group undetected by module
    if undetected_faults:
        from collections import Counter
        modules = Counter(f["net"].split("/")[0] for f in undetected_faults)
        print(f"\n  Undetected Faults by Module (top modules):")
        for mod, cnt in modules.most_common(5):
            print(f"    {mod:<35} {cnt:>4} faults")

        print(f"\n  Sample Undetected Faults (first 5):")
        for f in undetected_faults[:5]:
            print(f"    {f['net']:<50} {f['type']}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Parse DFT ATPG fault coverage report")
parser.add_argument("--report", help="ATPG report file")
parser.add_argument("--target", type=float, default=99.0,
                    help="Fault coverage target %% (default: 99.0)")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

metrics, undetected_faults = parse_coverage_report(text)
print_report(metrics, undetected_faults, args.target)
