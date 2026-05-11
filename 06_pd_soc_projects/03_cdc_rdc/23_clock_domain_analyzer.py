"""
Project: Clock Domain Analyzer
Tool context: Spyglass CDC / VC CDC / SDC
What it does: Parses a CDC clock domain report and builds a map of
all clock domains, their frequencies, source, and which modules belong
to each domain. Also identifies domain crossings between all domain pairs.

Usage:
    python 23_clock_domain_analyzer.py --report cdc_clocks.rpt
"""

import re
import argparse
from collections import defaultdict

SAMPLE_REPORT = """\
# Spyglass CDC — Clock Domain Report
# Design: soc_top

CLOCK DOMAINS:
Domain: clk_core    Source: PLL_CORE    Freq: 500MHz   Type: Synchronous
Domain: clk_axi     Source: PLL_CORE    Freq: 200MHz   Type: Synchronous
Domain: clk_apb     Source: PLL_APB     Freq: 100MHz   Type: Synchronous
Domain: clk_pll     Source: CRYSTAL     Freq: 25MHz    Type: Asynchronous
Domain: clk_uart    Source: EXTERNAL    Freq: 115200   Type: Asynchronous
Domain: clk_spi     Source: EXTERNAL    Freq: 50MHz    Type: Asynchronous

MODULE CLOCK ASSIGNMENTS:
Module: cpu_core         Domain: clk_core
Module: alu_unit         Domain: clk_core
Module: l1_cache         Domain: clk_core
Module: dma_ctrl         Domain: clk_axi
Module: axi_interconnect Domain: clk_axi
Module: apb_bridge       Domain: clk_apb
Module: gpio_ctrl        Domain: clk_apb
Module: pll_ctrl         Domain: clk_pll
Module: clk_ctrl         Domain: clk_pll
Module: uart_ctrl        Domain: clk_uart
Module: spi_ctrl         Domain: clk_spi
Module: soc_top          Domain: clk_core

DOMAIN CROSSINGS:
Crossing: clk_core  -> clk_axi    Signals: 24   Synchronized: 24  Unsynced: 0
Crossing: clk_axi   -> clk_core   Signals: 18   Synchronized: 16  Unsynced: 2
Crossing: clk_core  -> clk_apb    Signals: 12   Synchronized: 12  Unsynced: 0
Crossing: clk_apb   -> clk_core   Signals: 8    Synchronized: 8   Unsynced: 0
Crossing: clk_uart  -> clk_core   Signals: 5    Synchronized: 4   Unsynced: 1
Crossing: clk_spi   -> clk_core   Signals: 7    Synchronized: 7   Unsynced: 0
Crossing: clk_pll   -> clk_core   Signals: 3    Synchronized: 2   Unsynced: 1
"""


def parse_cdc_clocks(text):
    domains  = {}
    modules  = defaultdict(list)
    crossings = []

    # Parse domain entries
    for m in re.finditer(
        r"Domain:\s*(\S+)\s+Source:\s*(\S+)\s+Freq:\s*(\S+)\s+Type:\s*(\S+)", text
    ):
        domains[m.group(1)] = {
            "source": m.group(2),
            "freq":   m.group(3),
            "type":   m.group(4),
        }

    # Parse module-to-domain assignments
    for m in re.finditer(r"Module:\s*(\S+)\s+Domain:\s*(\S+)", text):
        modules[m.group(2)].append(m.group(1))

    # Parse crossing pairs
    for m in re.finditer(
        r"Crossing:\s*(\S+)\s*->\s*(\S+)\s+Signals:\s*(\d+)\s+Synchronized:\s*(\d+)\s+Unsynced:\s*(\d+)",
        text
    ):
        crossings.append({
            "src":   m.group(1),
            "dst":   m.group(2),
            "total": int(m.group(3)),
            "sync":  int(m.group(4)),
            "unsync":int(m.group(5)),
        })

    return domains, modules, crossings


def print_analysis(domains, modules, crossings):
    RED  = "\033[31m"
    GRN  = "\033[92m"
    YEL  = "\033[33m"
    RST  = "\033[0m"

    print("=" * 65)
    print("  CLOCK DOMAIN ANALYSIS")
    print("=" * 65)

    print(f"\n  Total clock domains : {len(domains)}")
    print(f"\n  {'DOMAIN':<18} {'SOURCE':<15} {'FREQ':<12} {'TYPE':<14} {'MODULES'}")
    print("  " + "-" * 80)
    for name, info in domains.items():
        mods = ", ".join(modules.get(name, []))
        ttype_col = YEL if info["type"] == "Asynchronous" else GRN
        print(f"  {name:<18} {info['source']:<15} {info['freq']:<12} "
              f"{ttype_col}{info['type']:<14}{RST} {mods}")

    print(f"\n  Total domain crossings: {len(crossings)}")
    total_signals = sum(c["total"] for c in crossings)
    total_unsync  = sum(c["unsync"] for c in crossings)
    print(f"  Total crossing signals : {total_signals}")
    print(f"  Total unsynchronized   : {RED if total_unsync else GRN}{total_unsync}{RST}")

    print(f"\n  {'SRC':<15} {'DST':<15} {'SIGNALS':>8} {'SYNCED':>8} "
          f"{'UNSYNCED':>9} {'STATUS'}")
    print("  " + "-" * 70)
    for c in sorted(crossings, key=lambda x: -x["unsync"]):
        status = f"{RED}REVIEW{RST}" if c["unsync"] > 0 else f"{GRN}OK{RST}"
        print(f"  {c['src']:<15} {c['dst']:<15} {c['total']:>8} "
              f"{c['sync']:>8} {c['unsync']:>9} {status}")

    # Highlight asynchronous domain pairs
    async_domains = {n for n, i in domains.items() if i["type"] == "Asynchronous"}
    if async_domains:
        print(f"\n  Asynchronous domains requiring special attention:")
        for d in async_domains:
            related = [c for c in crossings if c["src"] == d or c["dst"] == d]
            for cr in related:
                if cr["unsync"] > 0:
                    print(f"    {RED}{cr['src']} → {cr['dst']}: "
                          f"{cr['unsync']} unsynced signal(s){RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Analyze clock domain report from CDC tool")
parser.add_argument("--report", help="CDC clock domain report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

domains, modules, crossings = parse_cdc_clocks(text)
print_analysis(domains, modules, crossings)
