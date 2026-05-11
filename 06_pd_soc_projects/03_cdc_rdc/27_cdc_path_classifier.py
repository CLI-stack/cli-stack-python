"""
Project: CDC Path Classifier
Tool context: Spyglass CDC / VC CDC
What it does: Classifies CDC crossing paths by their synchronization method
(2-FF sync, MUX reconvergence, handshake, FIFO, gray-code, unsynchronized).
Helps engineers quickly understand the synchronization strategy for each path.

Usage:
    python 27_cdc_path_classifier.py --report cdc_paths.rpt
"""

import re
import argparse
from collections import Counter

SAMPLE_REPORT = """\
# CDC Path Classification Report — VC CDC
# Design: soc_top

PATH: cpu_req
  SRC_MODULE: cpu_core   SRC_CLOCK: clk_core
  DST_MODULE: dma_ctrl   DST_CLOCK: clk_axi
  SYNC_TYPE: TWO_FF_SYNC   SYNC_CELL: sync_2ff_u1
  STATUS: SYNCHRONIZED

PATH: dma_grant
  SRC_MODULE: dma_ctrl   SRC_CLOCK: clk_axi
  DST_MODULE: cpu_core   DST_CLOCK: clk_core
  SYNC_TYPE: TWO_FF_SYNC   SYNC_CELL: sync_2ff_u2
  STATUS: SYNCHRONIZED

PATH: uart_rx_data[7:0]
  SRC_MODULE: uart_ctrl   SRC_CLOCK: clk_uart
  DST_MODULE: cpu_core    DST_CLOCK: clk_core
  SYNC_TYPE: FIFO          SYNC_CELL: async_fifo_u1
  STATUS: SYNCHRONIZED

PATH: apb_addr[31:0]
  SRC_MODULE: cpu_core    SRC_CLOCK: clk_core
  DST_MODULE: apb_bridge  DST_CLOCK: clk_apb
  SYNC_TYPE: HANDSHAKE     SYNC_CELL: req_ack_sync_u1
  STATUS: SYNCHRONIZED

PATH: pll_lock
  SRC_MODULE: pll_ctrl   SRC_CLOCK: clk_pll
  DST_MODULE: clk_ctrl   DST_CLOCK: clk_core
  SYNC_TYPE: NONE         SYNC_CELL: N/A
  STATUS: UNSYNCHRONIZED

PATH: spi_done
  SRC_MODULE: spi_ctrl   SRC_CLOCK: clk_spi
  DST_MODULE: cpu_core   DST_CLOCK: clk_core
  SYNC_TYPE: TWO_FF_SYNC  SYNC_CELL: sync_2ff_u3
  STATUS: SYNCHRONIZED

PATH: config_reg[15:0]
  SRC_MODULE: apb_bridge  SRC_CLOCK: clk_apb
  DST_MODULE: cpu_core    DST_CLOCK: clk_core
  SYNC_TYPE: NONE          SYNC_CELL: N/A
  STATUS: UNSYNCHRONIZED

PATH: int_status[3:0]
  SRC_MODULE: gpio_ctrl   SRC_CLOCK: clk_apb
  DST_MODULE: cpu_core    DST_CLOCK: clk_core
  SYNC_TYPE: GRAY_CODE    SYNC_CELL: gray_sync_u1
  STATUS: SYNCHRONIZED
"""

SYNC_TYPE_DESC = {
    "TWO_FF_SYNC":  "2-FF synchronizer (good for single-bit control signals)",
    "FIFO":         "Async FIFO (good for multi-bit data buses)",
    "HANDSHAKE":    "Req/Ack handshake (good for wide data with back-pressure)",
    "GRAY_CODE":    "Gray-code encoded (good for counters/pointers)",
    "MUX_RECONV":   "MUX reconvergence (structural CDC, review carefully)",
    "NONE":         "NO synchronizer — potential metastability risk",
}


def parse_paths(text):
    paths = []
    current = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("PATH:"):
            if current:
                paths.append(current)
            current = {"signal": line.split(":", 1)[1].strip()}
        elif current:
            for key, pat in [
                ("src_module", r"SRC_MODULE:\s*(\S+)"),
                ("src_clock",  r"SRC_CLOCK:\s*(\S+)"),
                ("dst_module", r"DST_MODULE:\s*(\S+)"),
                ("dst_clock",  r"DST_CLOCK:\s*(\S+)"),
                ("sync_type",  r"SYNC_TYPE:\s*(\S+)"),
                ("sync_cell",  r"SYNC_CELL:\s*(\S+)"),
                ("status",     r"STATUS:\s*(\S+)"),
            ]:
                m = re.search(pat, line)
                if m:
                    current[key] = m.group(1)
    if current:
        paths.append(current)
    return paths


def print_classification(paths):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    sync_counts = Counter(p.get("sync_type", "UNKNOWN") for p in paths)
    unsync      = [p for p in paths if p.get("status", "").upper() == "UNSYNCHRONIZED"]

    print("=" * 70)
    print("  CDC PATH CLASSIFICATION REPORT")
    print("=" * 70)
    print(f"\n  Total crossing paths : {len(paths)}")
    print(f"  Synchronized         : {len(paths) - len(unsync)}")
    print(f"  {RED}Unsynchronized       : {len(unsync)}{RST}")

    print(f"\n  Synchronization Methods Used:")
    for stype, cnt in sync_counts.most_common():
        desc = SYNC_TYPE_DESC.get(stype, stype)
        col  = RED if stype == "NONE" else GRN if cnt >= 0 else ""
        print(f"    {stype:<15} {cnt:>3} paths  — {desc}")

    print(f"\n  Path Details:")
    print(f"  {'SIGNAL':<22} {'SRC CLK':<12} {'DST CLK':<12} {'SYNC TYPE':<14} {'STATUS'}")
    print("  " + "-" * 80)
    for p in sorted(paths, key=lambda x: 0 if x.get("status") == "UNSYNCHRONIZED" else 1):
        status = p.get("status", "?")
        col    = RED if status == "UNSYNCHRONIZED" else GREEN
        print(f"  {p.get('signal','?'):<22} {p.get('src_clock','?'):<12} "
              f"{p.get('dst_clock','?'):<12} {p.get('sync_type','?'):<14} {col}{status}{RST}")

    if unsync:
        print(f"\n  {RED}Action Required — Unsynchronized Paths:{RST}")
        for p in unsync:
            print(f"    Signal : {p.get('signal')}")
            print(f"    Path   : {p.get('src_module')}/{p.get('src_clock')} → "
                  f"{p.get('dst_module')}/{p.get('dst_clock')}")
            bit_cnt = re.search(r"\[(\d+):", p.get("signal", ""))
            if bit_cnt:
                print(f"    Rec    : Multi-bit bus — use Async FIFO or gray-code encoding")
            else:
                print(f"    Rec    : Single-bit — add 2-FF synchronizer cell")
            print()


# ── Main ─────────────────────────────────────────────────────────────────────
GRN = "\033[92m"
parser = argparse.ArgumentParser(description="Classify CDC crossing paths by sync type")
parser.add_argument("--report", help="CDC path report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

paths = parse_paths(text)
print_classification(paths)
