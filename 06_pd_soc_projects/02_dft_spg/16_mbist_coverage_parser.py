"""
Project: MBIST Coverage Parser
Tool context: Synopsys STAR Memory System / Mentor Tessent MBIST
What it does: Parses MBIST (Memory Built-In Self Test) coverage reports.
Extracts per-memory instance coverage, algorithm used, and repair status.
Flags memories that fail the coverage target.

Usage:
    python 16_mbist_coverage_parser.py --report mbist_coverage.rpt
    python 16_mbist_coverage_parser.py --report mbist_coverage.rpt --target 100.0
"""

import re
import argparse
from collections import Counter

SAMPLE_REPORT = """\
# MBIST Coverage Report
# Tool: Synopsys STAR Memory System
# Design: soc_top
# Date: 2024-01-15

================================================
MEMORY INSTANCE COVERAGE SUMMARY
================================================

Instance: cpu_core/icache_data_ram
  Type          : SRAM
  Depth x Width : 4096 x 64
  Algorithm     : MARCH_C+
  Coverage      : 100.00%
  Stuck-At      : 100.00%
  Transition    : 100.00%
  Repair        : Enabled (2 rows repaired)
  Status        : PASS

Instance: cpu_core/dcache_data_ram
  Type          : SRAM
  Depth x Width : 4096 x 64
  Algorithm     : MARCH_C+
  Coverage      : 100.00%
  Stuck-At      : 100.00%
  Transition    : 100.00%
  Repair        : Enabled (0 rows repaired)
  Status        : PASS

Instance: dma_ctrl/descriptor_ram
  Type          : SRAM
  Depth x Width : 256 x 32
  Algorithm     : MATS+
  Coverage      : 98.44%
  Stuck-At      : 98.44%
  Transition    : 97.90%
  Repair        : Disabled
  Status        : FAIL

Instance: spi_ctrl/rx_fifo_ram
  Type          : SRAM
  Depth x Width : 64 x 8
  Algorithm     : MARCH_B
  Coverage      : 100.00%
  Stuck-At      : 100.00%
  Transition    : 100.00%
  Repair        : N/A
  Status        : PASS

Instance: apb_bridge/config_rom
  Type          : ROM
  Depth x Width : 512 x 32
  Algorithm     : ROM_VERIFY
  Coverage      : 100.00%
  Status        : PASS

================================================
SUMMARY
================================================
Total memories tested    : 5
PASS                     : 4
FAIL                     : 1
Total bits covered       : 2,365,440
"""


def parse_mbist_report(text):
    """Parse per-memory MBIST coverage from report."""
    memories = []
    current  = None

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Instance:"):
            if current:
                memories.append(current)
            current = {"instance": line.split(":", 1)[1].strip()}
        elif current:
            for key, pattern in [
                ("type",       r"Type\s*:\s*(.+)"),
                ("size",       r"Depth x Width\s*:\s*(.+)"),
                ("algorithm",  r"Algorithm\s*:\s*(.+)"),
                ("coverage",   r"^Coverage\s*:\s*([\d.]+)%"),
                ("stuck_at",   r"Stuck-At\s*:\s*([\d.]+)%"),
                ("transition", r"Transition\s*:\s*([\d.]+)%"),
                ("repair",     r"Repair\s*:\s*(.+)"),
                ("status",     r"Status\s*:\s*(.+)"),
            ]:
                m = re.match(pattern, line)
                if m:
                    val = m.group(1).strip()
                    if key in ("coverage", "stuck_at", "transition"):
                        current[key] = float(val)
                    else:
                        current[key] = val

    if current:
        memories.append(current)

    return memories


def print_mbist_report(memories, target):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    passed  = [m for m in memories if m.get("status", "").upper() == "PASS"]
    failed  = [m for m in memories if m.get("status", "").upper() == "FAIL"]

    print("=" * 70)
    print("  MBIST COVERAGE REPORT")
    print("=" * 70)
    print(f"\n  Total memories  : {len(memories)}")
    print(f"  {GREEN}PASS{RST}            : {len(passed)}")
    print(f"  {RED}FAIL{RST}            : {len(failed)}")
    print(f"  Coverage target : {target}%")

    print(f"\n  {'INSTANCE':<35} {'TYPE':<6} {'COVERAGE':>10} {'S/A':>8} "
          f"{'TR':>8} {'REPAIR':<20} {'STATUS'}")
    print("  " + "-" * 105)

    for m in sorted(memories, key=lambda x: x.get("coverage", 100)):
        cov   = m.get("coverage",   "N/A")
        sa    = m.get("stuck_at",   "N/A")
        tr    = m.get("transition", "N/A")
        inst  = m.get("instance",   "?")
        mtype = m.get("type",       "?")
        rep   = m.get("repair",     "N/A")
        stat  = m.get("status",     "?").upper()

        cov_str = f"{cov:.2f}%" if isinstance(cov, float) else str(cov)
        sa_str  = f"{sa:.2f}%"  if isinstance(sa,  float) else str(sa)
        tr_str  = f"{tr:.2f}%"  if isinstance(tr,  float) else str(tr)

        passed_gate = isinstance(cov, float) and cov >= target
        stat_col    = f"{GREEN}PASS{RST}" if stat == "PASS" else f"{RED}FAIL{RST}"
        cov_col     = f"{GREEN}{cov_str}{RST}" if passed_gate else f"{RED}{cov_str}{RST}"

        print(f"  {inst:<35} {mtype:<6} {cov_col:>19} {sa_str:>8} "
              f"{tr_str:>8} {rep:<20} {stat_col}")

    if failed:
        print(f"\n  {RED}Failed Memories — Action Required:{RST}")
        for m in failed:
            print(f"    {m['instance']}")
            print(f"      Coverage: {m.get('coverage','?')}%  (target {target}%)")
            print(f"      Algorithm: {m.get('algorithm','?')}")
            print(f"      Action: Switch to stronger algorithm (e.g. MARCH_C+) "
                  f"or enable repair.")
    else:
        print(f"\n  {GREEN}All memories meet the {target}% coverage target.{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Parse MBIST coverage report")
parser.add_argument("--report", help="MBIST coverage report file")
parser.add_argument("--target", type=float, default=100.0,
                    help="Coverage target %% (default: 100.0)")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

memories = parse_mbist_report(text)
print_mbist_report(memories, args.target)
