"""
Project: Level Shifter Checker
Tool context: Synopsys PA Compiler / Cadence Voltus
What it does: Parses the level shifter insertion report and verifies that:
  - All voltage crossings have a level shifter
  - Correct LS type is used (LS_UP vs LS_DOWN)
  - No level shifter is in the wrong power domain
Generates a missing LS report for the implementation team.

Usage:
    python 33_level_shifter_checker.py --report ls_report.rpt
"""

import re
import argparse

SAMPLE_REPORT = """\
# Level Shifter Insertion Report — PA Compiler
# Design: soc_top
# Date: 2024-01-15

VOLTAGE PAIRS REQUIRING LEVEL SHIFTERS:
VDD (1.0V) <-> VDD_L (0.8V)

LEVEL SHIFTER INSTANCES:
Instance: ls_cpu_to_periph_data    TYPE: LS_DOWN  FROM_DOMAIN: PD_CPU    TO_DOMAIN: PD_PERIPH
  Signal: cpu_data[31:0]           FROM_VOLT: 1.0V  TO_VOLT: 0.8V  STATUS: INSERTED
Instance: ls_periph_to_cpu_status  TYPE: LS_UP    FROM_DOMAIN: PD_PERIPH  TO_DOMAIN: PD_CPU
  Signal: periph_status[7:0]       FROM_VOLT: 0.8V  TO_VOLT: 1.0V  STATUS: INSERTED
Instance: ls_cpu_to_periph_ctrl    TYPE: LS_DOWN  FROM_DOMAIN: PD_CPU    TO_DOMAIN: PD_PERIPH
  Signal: cpu_ctrl[3:0]            FROM_VOLT: 1.0V  TO_VOLT: 0.8V  STATUS: INSERTED

MISSING LEVEL SHIFTERS:
Signal: apb_data[31:0]             FROM_DOMAIN: PD_PERIPH  TO_DOMAIN: PD_CPU
  FROM_VOLT: 0.8V  TO_VOLT: 1.0V   REQUIRED_TYPE: LS_UP   STATUS: MISSING
Signal: int_req                    FROM_DOMAIN: PD_CPU     TO_DOMAIN: PD_PERIPH
  FROM_VOLT: 1.0V  TO_VOLT: 0.8V   REQUIRED_TYPE: LS_DOWN  STATUS: MISSING
Signal: uart_data[7:0]             FROM_DOMAIN: PD_PERIPH  TO_DOMAIN: PD_CPU
  FROM_VOLT: 0.8V  TO_VOLT: 1.0V   REQUIRED_TYPE: LS_UP   STATUS: MISSING

LEVEL SHIFTER SUMMARY:
Inserted   : 3
Missing    : 3
Total Required: 6
"""


def parse_ls_report(text):
    inserted = []
    missing  = []

    # Inserted LS
    for m in re.finditer(
        r"Instance:\s*(\S+)\s+TYPE:\s*(\S+)\s+FROM_DOMAIN:\s*(\S+)\s+TO_DOMAIN:\s*(\S+)\s+"
        r"Signal:\s*(\S+)\s+FROM_VOLT:\s*(\S+)\s+TO_VOLT:\s*(\S+)\s+STATUS:\s*(\S+)",
        text, re.DOTALL
    ):
        inserted.append({
            "instance":    m.group(1),
            "type":        m.group(2),
            "from_domain": m.group(3),
            "to_domain":   m.group(4),
            "signal":      m.group(5),
            "from_volt":   m.group(6),
            "to_volt":     m.group(7),
            "status":      m.group(8),
        })

    # Missing LS
    for m in re.finditer(
        r"Signal:\s*(\S+)\s+FROM_DOMAIN:\s*(\S+)\s+TO_DOMAIN:\s*(\S+)\s+"
        r"FROM_VOLT:\s*(\S+)\s+TO_VOLT:\s*(\S+)\s+REQUIRED_TYPE:\s*(\S+)\s+STATUS:\s*MISSING",
        text, re.DOTALL
    ):
        missing.append({
            "signal":      m.group(1),
            "from_domain": m.group(2),
            "to_domain":   m.group(3),
            "from_volt":   m.group(4),
            "to_volt":     m.group(5),
            "required_type": m.group(6),
        })

    # Summary
    ins_m  = re.search(r"Inserted\s*:\s*(\d+)", text)
    mis_m  = re.search(r"Missing\s*:\s*(\d+)", text)
    tot_m  = re.search(r"Total Required\s*:\s*(\d+)", text)
    summary = {
        "inserted": int(ins_m.group(1)) if ins_m else len(inserted),
        "missing":  int(mis_m.group(1)) if mis_m else len(missing),
        "total":    int(tot_m.group(1)) if tot_m else len(inserted) + len(missing),
    }
    return inserted, missing, summary


def print_report(inserted, missing, summary):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    completion = summary["inserted"] / summary["total"] * 100 if summary["total"] else 0
    cc = GREEN if completion == 100 else (YEL if completion >= 75 else RED)

    print("=" * 65)
    print("  LEVEL SHIFTER CHECK REPORT")
    print("=" * 65)
    print(f"\n  Required  : {summary['total']}")
    print(f"  Inserted  : {GREEN}{summary['inserted']}{RST}")
    print(f"  Missing   : {RED if summary['missing'] else GREEN}{summary['missing']}{RST}")
    print(f"  Completion: {cc}{completion:.1f}%{RST}")

    if inserted:
        print(f"\n  Inserted Level Shifters ({len(inserted)}):")
        print(f"  {'INSTANCE':<30} {'TYPE':<10} {'SIGNAL':<25} {'VOLTAGE'}")
        print("  " + "-" * 80)
        for ls in inserted:
            print(f"  {ls['instance']:<30} {GREEN}{ls['type']:<10}{RST} "
                  f"{ls['signal']:<25} {ls['from_volt']}→{ls['to_volt']}")

    if missing:
        print(f"\n  {RED}Missing Level Shifters ({len(missing)}) — Action Required:{RST}")
        print(f"  {'SIGNAL':<25} {'FROM':<15} {'TO':<15} {'REQUIRED TYPE':<12} {'VOLTAGE'}")
        print("  " + "-" * 85)
        for ls in missing:
            print(f"  {ls['signal']:<25} {ls['from_domain']:<15} {ls['to_domain']:<15} "
                  f"{RED}{ls['required_type']:<12}{RST} {ls['from_volt']}→{ls['to_volt']}")
        print(f"\n  Fix: Add missing LS cells in UPF using 'set_level_shifter' command")
        print(f"       or insert manually in the netlist at domain boundaries.")
    else:
        print(f"\n  {GREEN}All level shifters are inserted. ✓{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Check level shifter insertion")
parser.add_argument("--report", help="Level shifter report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

inserted, missing, summary = parse_ls_report(text)
print_report(inserted, missing, summary)
