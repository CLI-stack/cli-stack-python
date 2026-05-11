"""
Project: Scan Chain Analyzer
Tool context: Synopsys DFTMAX / Tessent / TetraMAX
What it does: Parses a scan chain report to verify scan insertion results.
Checks chain count, chain lengths, load/unload time, and flags imbalanced chains.
Imbalanced scan chains increase test time and can cause scan pattern failures.

Usage:
    python 12_scan_chain_analyzer.py --report scan_chains.rpt
    python 12_scan_chain_analyzer.py --report scan_chains.rpt --max-imbalance 15
"""

import re
import argparse
from statistics import mean, stdev

# Simulated scan chain insertion report (DFTMAX style)
SAMPLE_REPORT = """\
# DFTMAX Scan Chain Report
# Design: soc_top
# Mode: Internal_scan

Total scan cells inserted  : 48520
Total scan chains created  : 8
Scan enable signal         : scan_en
Test clock                 : scan_clk (25 MHz)

CHAIN DETAILS:
Chain  1 : Length=6120  SI=scan_si[0]  SO=scan_so[0]  Clock=scan_clk  Domain=CORE
Chain  2 : Length=6089  SI=scan_si[1]  SO=scan_so[1]  Clock=scan_clk  Domain=CORE
Chain  3 : Length=6134  SI=scan_si[2]  SO=scan_so[2]  Clock=scan_clk  Domain=CORE
Chain  4 : Length=6050  SI=scan_si[3]  SO=scan_so[3]  Clock=scan_clk  Domain=CORE
Chain  5 : Length=5980  SI=scan_si[4]  SO=scan_so[4]  Clock=scan_clk  Domain=CORE
Chain  6 : Length=6110  SI=scan_si[5]  SO=scan_so[5]  Clock=scan_clk  Domain=CORE
Chain  7 : Length=6042  SI=scan_si[6]  SO=scan_so[6]  Clock=scan_clk  Domain=CORE
Chain  8 : Length=6995  SI=scan_si[7]  SO=scan_so[7]  Clock=scan_clk  Domain=CORE
"""


def parse_scan_report(text):
    """Extract total cells, chain count, and per-chain details."""
    metrics = {}

    # Global metrics
    for key, pattern in [
        ("total_cells",   r"Total scan cells inserted\s*:\s*(\d+)"),
        ("total_chains",  r"Total scan chains created\s*:\s*(\d+)"),
        ("scan_enable",   r"Scan enable signal\s*:\s*(\S+)"),
        ("test_clock",    r"Test clock\s*:\s*(.+)"),
    ]:
        m = re.search(pattern, text)
        if m:
            val = m.group(1).strip()
            metrics[key] = int(val) if val.isdigit() else val

    # Per-chain details
    chain_pattern = re.compile(
        r"Chain\s+(\d+)\s*:\s*Length=(\d+)\s+SI=(\S+)\s+SO=(\S+)\s+Clock=(\S+)\s+Domain=(\S+)"
    )
    chains = []
    for m in chain_pattern.finditer(text):
        chains.append({
            "id":     int(m.group(1)),
            "length": int(m.group(2)),
            "si":     m.group(3),
            "so":     m.group(4),
            "clock":  m.group(5),
            "domain": m.group(6),
        })

    return metrics, chains


def analyze_chains(metrics, chains, max_imbalance_pct):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    lengths = [c["length"] for c in chains]
    avg_len = mean(lengths) if lengths else 0
    max_len = max(lengths) if lengths else 0
    min_len = min(lengths) if lengths else 0
    std_len = stdev(lengths) if len(lengths) > 1 else 0

    # Imbalance = (max - min) / avg * 100
    imbalance_pct = (max_len - min_len) / avg_len * 100 if avg_len else 0
    load_time_cycles = max_len  # longest chain determines scan load/unload time

    print("=" * 65)
    print("  SCAN CHAIN ANALYSIS REPORT")
    print("=" * 65)
    print(f"\n  Total scan cells  : {metrics.get('total_cells', 0):,}")
    print(f"  Total chains      : {metrics.get('total_chains', len(chains))}")
    print(f"  Scan enable       : {metrics.get('scan_enable', 'N/A')}")
    print(f"  Test clock        : {metrics.get('test_clock', 'N/A')}")
    print(f"\n  Chain Statistics:")
    print(f"    Average length  : {avg_len:,.1f} cells")
    print(f"    Max length      : {max_len:,} cells")
    print(f"    Min length      : {min_len:,} cells")
    print(f"    Std deviation   : {std_len:,.1f}")
    print(f"    Imbalance       : {imbalance_pct:.1f}%  (limit: {max_imbalance_pct}%)")
    print(f"    Scan load cycles: {load_time_cycles:,} (limited by longest chain)")

    # Flag imbalanced chains
    print(f"\n  Chain Detail:")
    print(f"  {'ID':<6} {'LENGTH':>8} {'SI':<15} {'SO':<15} {'DOMAIN':<10} {'STATUS'}")
    print("  " + "-" * 70)
    for c in chains:
        deviation_pct = abs(c["length"] - avg_len) / avg_len * 100 if avg_len else 0
        if c["length"] == max_len and imbalance_pct > max_imbalance_pct:
            status = f"{RED}LONGEST — adds {c['length']-int(avg_len)} extra cycles{RST}"
        elif deviation_pct > max_imbalance_pct / 2:
            status = f"{YEL}SLIGHTLY IMBALANCED ({deviation_pct:.1f}% off avg){RST}"
        else:
            status = f"{GREEN}OK{RST}"
        print(f"  {c['id']:<6} {c['length']:>8,} {c['si']:<15} {c['so']:<15} {c['domain']:<10} {status}")

    # Gate check
    print(f"\n  Scan Imbalance Gate:")
    if imbalance_pct <= max_imbalance_pct:
        print(f"  {GREEN}PASS — Imbalance {imbalance_pct:.1f}% ≤ {max_imbalance_pct}%{RST}")
    else:
        print(f"  {RED}FAIL — Imbalance {imbalance_pct:.1f}% > {max_imbalance_pct}% limit{RST}")
        print(f"  Recommendation: Rebalance chains by adjusting DFTMAX constraints.")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Analyze scan chain insertion report")
parser.add_argument("--report",        help="Scan chain report file")
parser.add_argument("--max-imbalance", type=float, default=10.0,
                    help="Max allowed chain length imbalance %% (default: 10)")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

metrics, chains = parse_scan_report(text)
analyze_chains(metrics, chains, args.max_imbalance)
