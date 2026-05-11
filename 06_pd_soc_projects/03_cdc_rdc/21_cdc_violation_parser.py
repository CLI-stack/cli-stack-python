"""
Project: CDC Violation Parser
Tool context: Spyglass CDC / Synopsys VC CDC / Mentor Questa CDC
What it does: Parses CDC violations from a Spyglass CDC report.
Extracts crossing type, source/destination clock domains, module, and
recommended fix. Groups violations by type for prioritized fixing.

Usage:
    python 21_cdc_violation_parser.py --report cdc_report.rpt
    python 21_cdc_violation_parser.py --report cdc_report.rpt --severity Error
"""

import re
import argparse
from collections import Counter, defaultdict

SAMPLE_REPORT = """\
# SpyGlass CDC Report
# Design: soc_top
# Date: 2024-01-15

RULE:CDC_CONV_RULE  SEVERITY:Error  MODULE:cpu_core  LINE:245
  Signal 'cpu_req' crosses from domain 'clk_core' to 'clk_axi' without synchronizer
  SRC_CLOCK: clk_core (500MHz)  DEST_CLOCK: clk_axi (200MHz)
  CROSSING_TYPE: Data

RULE:CDC_CONV_RULE  SEVERITY:Error  MODULE:dma_ctrl  LINE:88
  Signal 'dma_grant' crosses from domain 'clk_axi' to 'clk_core' without synchronizer
  SRC_CLOCK: clk_axi (200MHz)  DEST_CLOCK: clk_core (500MHz)
  CROSSING_TYPE: Control

RULE:CDC_MUX_SEL    SEVERITY:Error  MODULE:apb_bridge  LINE:134
  MUX select 'apb_sel' driven by multi-domain signals without reconvergence check
  SRC_CLOCK: clk_core  DEST_CLOCK: clk_apb
  CROSSING_TYPE: Control

RULE:CDC_GLITCH     SEVERITY:Fatal  MODULE:clk_ctrl  LINE:312
  Glitch possible on clock signal 'clk_div' — clock mux without sync handshake
  SRC_CLOCK: clk_pll  DEST_CLOCK: clk_safe
  CROSSING_TYPE: Clock

RULE:CDC_NO_SYNC    SEVERITY:Warning  MODULE:uart_ctrl  LINE:67
  Signal 'rx_data[7:0]' bus crossing without gray-code encoding
  SRC_CLOCK: clk_uart  DEST_CLOCK: clk_core
  CROSSING_TYPE: Data_Bus

RULE:CDC_ASYNC_RST  SEVERITY:Warning  MODULE:pll_ctrl  LINE:200
  Async reset 'pll_rstn' asserted from different domain than de-assertion
  SRC_CLOCK: clk_pll  DEST_CLOCK: clk_core
  CROSSING_TYPE: Reset

RULE:CDC_CONV_RULE  SEVERITY:Error  MODULE:spi_ctrl  LINE:445
  Signal 'spi_done' crosses from domain 'clk_spi' to 'clk_core' without synchronizer
  SRC_CLOCK: clk_spi (50MHz)  DEST_CLOCK: clk_core (500MHz)
  CROSSING_TYPE: Control
"""

# Fix recommendations per crossing type
FIX_RECS = {
    "Data":     "Add 2-FF synchronizer or use handshaking/FIFO for multi-bit data",
    "Control":  "Add 2-FF synchronizer (e.g., sync_2ff cell)",
    "Clock":    "Use a glitch-free clock mux with synchronization handshake",
    "Data_Bus": "Use gray-code encoding or asynchronous FIFO for bus crossings",
    "Reset":    "Use reset synchronizer with proper assert/deassert sequencing",
}

SEV_RANK = {"Fatal": 0, "Error": 1, "Warning": 2, "Info": 3}


def parse_cdc_report(text, sev_filter=None):
    violations = []
    header_pat = re.compile(
        r"RULE:(\S+)\s+SEVERITY:(\S+)\s+MODULE:(\S+)\s+LINE:(\d+)"
    )
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = header_pat.match(lines[i].strip())
        if m:
            rule, sev, module, line = m.group(1), m.group(2), m.group(3), int(m.group(4))
            desc = lines[i+1].strip() if i+1 < len(lines) else ""
            clk_line = lines[i+2].strip() if i+2 < len(lines) else ""
            type_line = lines[i+3].strip() if i+3 < len(lines) else ""

            src_clk = re.search(r"SRC_CLOCK:\s*(\S+)", clk_line)
            dst_clk = re.search(r"DEST_CLOCK:\s*(\S+)", clk_line)
            ctype   = re.search(r"CROSSING_TYPE:\s*(\S+)", type_line)

            if sev_filter and sev not in sev_filter:
                i += 1
                continue

            violations.append({
                "rule":    rule,
                "severity":sev,
                "module":  module,
                "line":    line,
                "desc":    desc,
                "src_clk": src_clk.group(1) if src_clk else "?",
                "dst_clk": dst_clk.group(1) if dst_clk else "?",
                "type":    ctype.group(1) if ctype else "Unknown",
                "fix":     FIX_RECS.get(ctype.group(1) if ctype else "", "Review crossing"),
            })
            i += 4
            continue
        i += 1
    return violations


def print_cdc_report(violations):
    RED  = "\033[31m"
    YEL  = "\033[33m"
    CYN  = "\033[36m"
    GRN  = "\033[92m"
    RST  = "\033[0m"
    SEV_COL = {"Fatal": "\033[91m", "Error": RED, "Warning": YEL, "Info": CYN}

    sev_counts  = Counter(v["severity"] for v in violations)
    type_counts = Counter(v["type"]     for v in violations)
    mod_counts  = Counter(v["module"]   for v in violations)

    print("=" * 65)
    print("  CDC VIOLATION REPORT")
    print("=" * 65)
    print(f"\n  Total violations: {len(violations)}")

    for sev in ["Fatal", "Error", "Warning", "Info"]:
        c   = sev_counts.get(sev, 0)
        col = SEV_COL.get(sev, "")
        print(f"    {col}{sev:<10}{RST} {c}")

    print("\n  By Crossing Type:")
    for t, cnt in type_counts.most_common():
        print(f"    {t:<20} {cnt}  → Fix: {FIX_RECS.get(t,'Review')[:50]}")

    print("\n  Violation Detail:")
    print("  " + "-" * 90)
    for v in sorted(violations, key=lambda x: SEV_RANK.get(x["severity"], 9)):
        col = SEV_COL.get(v["severity"], "")
        print(f"\n  [{col}{v['severity']}{RST}] {v['rule']} — {v['type']} crossing")
        print(f"    Module  : {v['module']}:{v['line']}")
        print(f"    Clocks  : {v['src_clk']} → {v['dst_clk']}")
        print(f"    Issue   : {v['desc']}")
        print(f"    Fix     : {v['fix']}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Parse CDC violation report")
parser.add_argument("--report",   help="CDC report file")
parser.add_argument("--severity", help="Filter severity e.g. Fatal,Error")
args = parser.parse_args()

sev_filter = set(args.severity.split(",")) if args.severity else None
text       = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

violations = parse_cdc_report(text, sev_filter=sev_filter)
print_cdc_report(violations)
