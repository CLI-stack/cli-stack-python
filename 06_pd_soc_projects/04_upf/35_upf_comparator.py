"""
Project: UPF File Comparator
Tool context: Synopsys PA Compiler / Cadence Voltus
What it does: Compares two UPF files (e.g., v1 vs v2) and reports
what commands were added, removed, or changed. Critical for tracking
power intent changes between design milestones.

Usage:
    python 35_upf_comparator.py --old upf_v1.upf --new upf_v2.upf
"""

import re
import argparse

OLD_UPF = """\
create_power_domain PD_TOP  -include_scope
create_power_domain PD_CPU  -elements {cpu_core alu_unit}
create_power_domain PD_DMA  -elements {dma_ctrl}
create_supply_net VDD   -domain soc_top
create_supply_net VSS   -domain soc_top
create_supply_set SS_CPU -function {power VDD} -function {ground VSS}
add_power_state PD_CPU -state {ON  -supply_expr {power == {FULL_ON, 1.0}}}
add_power_state PD_CPU -state {OFF -supply_expr {power == {OFF}}}
"""

NEW_UPF = """\
create_power_domain PD_TOP  -include_scope
create_power_domain PD_CPU  -elements {cpu_core alu_unit l1_cache}
create_power_domain PD_DMA  -elements {dma_ctrl axi_interconnect}
create_power_domain PD_PERIPH -elements {apb_bridge uart_ctrl}
create_supply_net VDD   -domain soc_top
create_supply_net VDD_L -domain soc_top
create_supply_net VSS   -domain soc_top
create_supply_set SS_CPU    -function {power VDD}   -function {ground VSS}
create_supply_set SS_PERIPH -function {power VDD_L} -function {ground VSS}
add_power_state PD_CPU -state {ON  -supply_expr {power == {FULL_ON, 1.0}}}
add_power_state PD_CPU -state {OFF -supply_expr {power == {OFF}}}
add_power_state PD_CPU -state {RET -supply_expr {power == {PARTIAL_ON, 0.6}}}
"""

COMMAND_TYPES = [
    "create_power_domain",
    "create_supply_net",
    "create_supply_port",
    "create_supply_set",
    "add_power_state",
    "associate_supply_set",
    "set_isolation",
    "set_level_shifter",
    "set_retention",
]


def extract_commands(text):
    """Parse UPF file into a dict of {command_line → True}."""
    commands = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        # Normalize whitespace
        normalized = " ".join(line.split())
        # Categorize
        for ct in COMMAND_TYPES:
            if normalized.startswith(ct):
                commands[normalized] = ct
                break
    return commands


def compare_upf(old, new):
    old_keys = set(old.keys())
    new_keys = set(new.keys())
    added    = new_keys - old_keys
    removed  = old_keys - new_keys
    unchanged= old_keys & new_keys

    # Find modified (same command type, different arguments)
    old_by_type = {}
    for cmd, ctype in old.items():
        key = (ctype, cmd.split()[1] if len(cmd.split()) > 1 else cmd)
        old_by_type[key] = cmd

    new_by_type = {}
    for cmd, ctype in new.items():
        key = (ctype, cmd.split()[1] if len(cmd.split()) > 1 else cmd)
        new_by_type[key] = cmd

    modified = []
    for key in set(old_by_type) & set(new_by_type):
        if old_by_type[key] != new_by_type[key]:
            modified.append((old_by_type[key], new_by_type[key]))

    return added, removed, unchanged, modified


def print_delta(added, removed, unchanged, modified):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print("=" * 65)
    print("  UPF FILE COMPARISON (DELTA)")
    print("=" * 65)
    print(f"\n  {GREEN}ADDED    : {len(added)}{RST}  (new power intent)")
    print(f"  {RED}REMOVED  : {len(removed)}{RST}  (removed power intent)")
    print(f"  {YEL}MODIFIED : {len(modified)}{RST}  (changed parameters)")
    print(f"  UNCHANGED: {len(unchanged)}")

    def show(title, items, color, prefix=""):
        if not items:
            return
        print(f"\n  {color}── {title} ──{RST}")
        for item in sorted(items):
            cmd = item if isinstance(item, str) else item[0]
            cmd_type = cmd.split()[0] if cmd.split() else "?"
            print(f"    [{cmd_type}] {' '.join(cmd.split()[1:])}")

    show("ADDED COMMANDS", added, GREEN)
    show("REMOVED COMMANDS", removed, RED)

    if modified:
        print(f"\n  {YEL}── MODIFIED COMMANDS ──{RST}")
        for old_cmd, new_cmd in modified:
            print(f"    OLD: {old_cmd}")
            print(f"    NEW: {new_cmd}")
            print()

    # Impact summary
    added_domains  = [c for c in added   if c.startswith("create_power_domain")]
    removed_domains= [c for c in removed if c.startswith("create_power_domain")]

    if added_domains or removed_domains:
        print(f"\n  Power Domain Changes (high impact):")
        for d in added_domains:
            print(f"    {GREEN}+ {d}{RST}")
        for d in removed_domains:
            print(f"    {RED}- {d}{RST}")

    added_supplies = [c for c in added if c.startswith("create_supply_net")]
    if added_supplies:
        print(f"\n  New Supply Nets (verify voltage levels):")
        for s in added_supplies:
            print(f"    {GREEN}+ {s}{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Compare two UPF files for differences")
parser.add_argument("--old", help="Old UPF file")
parser.add_argument("--new", help="New UPF file")
args = parser.parse_args()

old_text = open(args.old).read() if args.old else OLD_UPF
new_text = open(args.new).read() if args.new else NEW_UPF
if not args.old:
    print("No files given — using sample data.\n")

old_cmds = extract_commands(old_text)
new_cmds = extract_commands(new_text)
added, removed, unchanged, modified = compare_upf(old_cmds, new_cmds)
print_delta(added, removed, unchanged, modified)
