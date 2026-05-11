"""
Project: RTL Module Hierarchy Parser
Tool context: Synopsys DC / Cadence Genus / any elaboration log
What it does: Parses an elaboration or synthesis log to extract the RTL
module hierarchy. Builds a tree of instances and their types.
Useful for understanding design structure and validating CDC/UPF domain assignments.

Usage:
    python 41_rtl_hierarchy_parser.py --log elab.log
"""

import re
import argparse
from collections import defaultdict

SAMPLE_LOG = """\
Information: Elaborating design 'soc_top'. (DP-001)
  Inferred module cpu_core from rtl/cpu_core.v
    Inferred module alu_unit from rtl/alu_unit.v
    Inferred module l1_cache from rtl/l1_cache.v
      Inferred module cache_ctrl from rtl/cache_ctrl.v
      Inferred module sram_wrapper from rtl/sram_wrapper.v (black-box)
  Inferred module dma_ctrl from rtl/dma_ctrl.v
    Inferred module axi_master from rtl/axi_master.v
    Inferred module fifo_ctrl from rtl/fifo_ctrl.v
  Inferred module apb_bridge from rtl/apb_bridge.v
    Inferred module apb_decoder from rtl/apb_decoder.v
    Inferred module uart_ctrl from rtl/uart_ctrl.v
    Inferred module spi_ctrl from rtl/spi_ctrl.v
    Inferred module gpio_ctrl from rtl/gpio_ctrl.v
  Inferred module pll_ctrl from rtl/pll_ctrl.v (black-box)
  Inferred module clk_ctrl from rtl/clk_ctrl.v
Information: Elaboration complete. Total modules: 15
"""


def parse_hierarchy(text):
    """Parse indentation-based hierarchy from elaboration log."""
    root = {"name": "soc_top", "type": "soc_top", "children": [], "blackbox": False, "depth": 0}
    stack = [root]

    # Try to detect module hierarchy lines
    mod_pat = re.compile(r"^(\s*)Inferred module (\S+) from (\S+)(.*)")

    for line in text.splitlines():
        m = mod_pat.match(line)
        if not m:
            continue
        indent   = len(m.group(1))
        name     = m.group(2)
        rtl_file = m.group(3)
        flags    = m.group(4)
        blackbox = "black-box" in flags
        depth    = indent // 2 + 1

        node = {"name": name, "file": rtl_file, "blackbox": blackbox,
                "children": [], "depth": depth}

        # Pop stack until we find the right parent depth
        while len(stack) > 1 and stack[-1]["depth"] >= depth:
            stack.pop()

        stack[-1]["children"].append(node)
        stack.append(node)

    return root


def count_nodes(node):
    total    = 1
    blackbox = 1 if node.get("blackbox") else 0
    for child in node.get("children", []):
        t, b = count_nodes(child)
        total    += t
        blackbox += b
    return total, blackbox


def print_tree(node, prefix="", is_last=True):
    CYN  = "\033[36m"
    YEL  = "\033[33m"
    RST  = "\033[0m"

    connector = "└── " if is_last else "├── "
    bb_tag    = f" {YEL}[blackbox]{RST}" if node.get("blackbox") else ""
    file_tag  = f" ({node.get('file','')})" if node.get("depth", 0) > 0 else ""

    print(f"  {prefix}{connector}{CYN}{node['name']}{RST}{bb_tag}{file_tag}")

    children  = node.get("children", [])
    extension = "    " if is_last else "│   "
    for i, child in enumerate(children):
        print_tree(child, prefix + extension, i == len(children) - 1)


def print_stats(root):
    total, blackbox = count_nodes(root)
    total -= 1  # exclude root

    print("=" * 65)
    print("  RTL MODULE HIERARCHY")
    print("=" * 65)
    print()
    print_tree(root, is_last=True)

    print(f"\n  {'─'*50}")
    print(f"  Total modules  : {total}")
    print(f"  Black-box IPs  : {blackbox}")
    print(f"  Synthesizable  : {total - blackbox}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Parse RTL hierarchy from elaboration log")
parser.add_argument("--log", help="Elaboration or synthesis log file")
args = parser.parse_args()

text = open(args.log).read() if args.log else SAMPLE_LOG
if not args.log:
    print("No log file — using sample data.\n")

root = parse_hierarchy(text)
print_stats(root)
