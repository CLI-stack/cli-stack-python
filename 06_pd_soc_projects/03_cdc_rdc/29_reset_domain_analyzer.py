"""
Project: Reset Domain Analyzer
Tool context: Spyglass RDC
What it does: Parses a reset domain report and maps which modules belong
to which reset domain, checks for reset domain crossings, and flags
missing reset synchronizers.

Usage:
    python 29_reset_domain_analyzer.py --report rdc_domains.rpt
"""

import re
import argparse
from collections import defaultdict

SAMPLE_REPORT = """\
# SpyGlass RDC — Reset Domain Report
# Design: soc_top

RESET DOMAINS:
Domain: rstn_core    Source: por_rstn AND pll_lock    Type: Synchronous   Active: Low
Domain: rstn_axi     Source: por_rstn AND axi_rstn    Type: Synchronous   Active: Low
Domain: rstn_apb     Source: por_rstn                 Type: Synchronous   Active: Low
Domain: rstn_pll     Source: por_rstn                 Type: Asynchronous  Active: Low
Domain: rstn_uart    Source: EXTERNAL                 Type: Asynchronous  Active: Low
Domain: rstn_pd_off  Source: pm_ctrl                  Type: Synchronous   Active: Low

MODULE RESET ASSIGNMENTS:
Module: cpu_core         Reset: rstn_core
Module: alu_unit         Reset: rstn_core
Module: l1_cache         Reset: rstn_core
Module: dma_ctrl         Reset: rstn_axi
Module: axi_interconnect Reset: rstn_axi
Module: apb_bridge       Reset: rstn_apb
Module: gpio_ctrl        Reset: rstn_apb
Module: pll_ctrl         Reset: rstn_pll
Module: uart_ctrl        Reset: rstn_uart
Module: soc_top          Reset: rstn_core

RESET DOMAIN CROSSINGS:
Crossing: rstn_core  -> rstn_axi    Synchronized: YES  Cell: reset_sync_u1
Crossing: rstn_core  -> rstn_apb    Synchronized: YES  Cell: reset_sync_u2
Crossing: rstn_pll   -> rstn_core   Synchronized: NO   Cell: N/A
Crossing: rstn_uart  -> rstn_core   Synchronized: NO   Cell: N/A
Crossing: rstn_core  -> rstn_pd_off Synchronized: YES  Cell: reset_sync_u3
"""


def parse_reset_report(text):
    domains   = {}
    modules   = defaultdict(list)
    crossings = []

    for m in re.finditer(
        r"Domain:\s*(\S+)\s+Source:\s*(.+?)\s+Type:\s*(\S+)\s+Active:\s*(\S+)", text
    ):
        domains[m.group(1)] = {
            "source": m.group(2).strip(),
            "type":   m.group(3),
            "active": m.group(4),
        }

    for m in re.finditer(r"Module:\s*(\S+)\s+Reset:\s*(\S+)", text):
        modules[m.group(2)].append(m.group(1))

    for m in re.finditer(
        r"Crossing:\s*(\S+)\s*->\s*(\S+)\s+Synchronized:\s*(\S+)\s+Cell:\s*(\S+)", text
    ):
        crossings.append({
            "src":   m.group(1),
            "dst":   m.group(2),
            "sync":  m.group(3).upper() == "YES",
            "cell":  m.group(4),
        })

    return domains, modules, crossings


def print_analysis(domains, modules, crossings):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    unsync = [c for c in crossings if not c["sync"]]

    print("=" * 65)
    print("  RESET DOMAIN ANALYSIS")
    print("=" * 65)
    print(f"\n  Total reset domains   : {len(domains)}")
    print(f"  Total crossings       : {len(crossings)}")
    print(f"  Unsynchronized        : {RED if unsync else GREEN}{len(unsync)}{RST}")

    print(f"\n  {'DOMAIN':<18} {'SOURCE':<30} {'TYPE':<14} {'MODULES'}")
    print("  " + "-" * 90)
    for name, info in domains.items():
        mods    = ", ".join(modules.get(name, ["-"]))
        tc      = YEL if info["type"] == "Asynchronous" else GREEN
        print(f"  {name:<18} {info['source']:<30} {tc}{info['type']:<14}{RST} {mods}")

    print(f"\n  Reset Domain Crossings:")
    print(f"  {'SRC RESET':<18} {'DST RESET':<18} {'SYNC':<6} {'CELL'}")
    print("  " + "-" * 65)
    for c in crossings:
        sc = GREEN if c["sync"] else RED
        st = f"{sc}{'YES' if c['sync'] else 'NO'}{RST}"
        print(f"  {c['src']:<18} {c['dst']:<18} {st:<15} {c['cell']}")

    if unsync:
        print(f"\n  {RED}Missing Reset Synchronizers:{RST}")
        for c in unsync:
            print(f"    {c['src']} → {c['dst']}")
            print(f"    Action: Instantiate reset_sync cell between these domains")
            print()


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Analyze reset domain report")
parser.add_argument("--report", help="RDC domain report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

domains, modules, crossings = parse_reset_report(text)
print_analysis(domains, modules, crossings)
