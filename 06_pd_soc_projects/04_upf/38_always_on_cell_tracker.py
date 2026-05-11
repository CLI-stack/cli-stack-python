"""
Project: Always-On Cell Tracker
Tool context: Synopsys PA Compiler / Cadence Voltus
What it does: Parses a PA report to identify all always-on (AO) cells
and buffers in the design. Verifies that AO cells are in the correct
power domain and that non-AO logic is not driving AO signals directly.

Usage:
    python 38_always_on_cell_tracker.py --report ao_cells.rpt
"""

import re
import argparse
from collections import Counter

SAMPLE_REPORT = """\
# Always-On Cell Report — PA Compiler
# Design: soc_top

ALWAYS-ON CELL INSTANCES:
Instance: ao_buf_iso_en       CELL_TYPE: AOBUFD2    DOMAIN: PD_TOP   SIGNAL: iso_en_cpu
  Powers from: VDD (always active)  Drives: PD_CPU isolation enable
  STATUS: CORRECT

Instance: ao_buf_ret_save     CELL_TYPE: AOBUFD2    DOMAIN: PD_TOP   SIGNAL: save_en_cpu
  Powers from: VDD (always active)  Drives: PD_CPU retention save
  STATUS: CORRECT

Instance: ao_inv_rst_n        CELL_TYPE: AOINVD1    DOMAIN: PD_TOP   SIGNAL: cpu_rstn
  Powers from: VDD (always active)  Drives: PD_CPU reset tree
  STATUS: CORRECT

Instance: ao_buf_illegal      CELL_TYPE: AOBUFFD4   DOMAIN: PD_CPU   SIGNAL: cpu_req
  Powers from: VDD  BUT domain is PD_CPU (switchable!)
  STATUS: ERROR — AO cell in switchable domain

REGULAR CELLS DRIVING AO SIGNALS (problematic):
Instance: std_inv_u5     CELL_TYPE: INVD1   DOMAIN: PD_CPU   SIGNAL: iso_en_dma
  Regular (non-AO) cell drives isolation enable — may fail when PD_CPU is OFF
  STATUS: ERROR

Instance: std_buf_u12    CELL_TYPE: BUFD2   DOMAIN: PD_CPU   SIGNAL: save_en_dma
  Regular cell drives retention save enable signal
  STATUS: ERROR

ALWAYS-ON CELL SUMMARY:
Correct AO cells         : 3
Errors (wrong domain)    : 1
Regular cells driving AO : 2
Total AO instances       : 4
"""


def parse_ao_report(text):
    ao_cells = []
    reg_driving_ao = []

    # Parse AO cell instances
    for m in re.finditer(
        r"Instance:\s*(\S+)\s+CELL_TYPE:\s*(\S+)\s+DOMAIN:\s*(\S+)\s+SIGNAL:\s*(\S+).*?"
        r"STATUS:\s*(\S+[^\n]*)",
        text, re.DOTALL
    ):
        ao_cells.append({
            "instance":  m.group(1),
            "cell_type": m.group(2),
            "domain":    m.group(3),
            "signal":    m.group(4),
            "status":    m.group(5).strip(),
        })

    # Parse regular cells driving AO signals
    in_section = False
    for line in text.splitlines():
        if "REGULAR CELLS DRIVING AO" in line:
            in_section = True
            continue
        if in_section and line.strip().startswith("Instance:"):
            m = re.match(
                r"\s*Instance:\s*(\S+)\s+CELL_TYPE:\s*(\S+)\s+DOMAIN:\s*(\S+)\s+SIGNAL:\s*(\S+)",
                line
            )
            if m:
                reg_driving_ao.append({
                    "instance":  m.group(1),
                    "cell_type": m.group(2),
                    "domain":    m.group(3),
                    "signal":    m.group(4),
                })
        elif in_section and "SUMMARY" in line:
            break

    # Summary
    summary = {}
    for key, pat in [
        ("correct",       r"Correct AO cells\s*:\s*(\d+)"),
        ("wrong_domain",  r"Errors.*wrong domain.*:\s*(\d+)"),
        ("reg_driving",   r"Regular cells driving AO\s*:\s*(\d+)"),
        ("total",         r"Total AO instances\s*:\s*(\d+)"),
    ]:
        m = re.search(pat, text)
        if m:
            summary[key] = int(m.group(1))

    return ao_cells, reg_driving_ao, summary


def print_report(ao_cells, reg_driving_ao, summary):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print("=" * 65)
    print("  ALWAYS-ON CELL TRACKER REPORT")
    print("=" * 65)
    print(f"\n  Total AO instances        : {summary.get('total', len(ao_cells))}")
    print(f"  Correct AO cells          : {GREEN}{summary.get('correct', 0)}{RST}")
    print(f"  AO cells in wrong domain  : {RED}{summary.get('wrong_domain', 0)}{RST}")
    print(f"  Regular cells driving AO  : {RED}{summary.get('reg_driving', 0)}{RST}")

    print(f"\n  AO Cell Instances:")
    print(f"  {'INSTANCE':<25} {'TYPE':<14} {'DOMAIN':<12} {'SIGNAL':<20} {'STATUS'}")
    print("  " + "-" * 90)
    for c in ao_cells:
        ok  = c["status"] == "CORRECT"
        col = GREEN if ok else RED
        print(f"  {c['instance']:<25} {c['cell_type']:<14} {c['domain']:<12} "
              f"{c['signal']:<20} {col}{c['status']}{RST}")

    if reg_driving_ao:
        print(f"\n  {RED}Regular Cells Driving AO Signals (Must Fix):{RST}")
        print(f"  {'INSTANCE':<20} {'TYPE':<12} {'DOMAIN':<12} {'DRIVING SIGNAL'}")
        print("  " + "-" * 65)
        for c in reg_driving_ao:
            print(f"  {c['instance']:<20} {c['cell_type']:<12} {c['domain']:<12} {c['signal']}")
        print(f"\n  Fix: Replace with AO cell (AOBUFD / AOINVD) in always-on domain (PD_TOP)")

    errors = [c for c in ao_cells if "ERROR" in c["status"]]
    if errors:
        print(f"\n  {RED}AO Cells in Wrong Domain (Must Move to AO Domain):{RST}")
        for c in errors:
            print(f"    {c['instance']} — currently in {c['domain']}")
            print(f"    Fix: Move to PD_TOP or equivalent always-on domain")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Track always-on cell usage")
parser.add_argument("--report", help="Always-on cell report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

ao_cells, reg_driving_ao, summary = parse_ao_report(text)
print_report(ao_cells, reg_driving_ao, summary)
