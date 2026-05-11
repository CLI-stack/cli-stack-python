"""
Project: Isolation Cell Checker
Tool context: Synopsys PA Compiler / Cadence Voltus
What it does: Verifies that all power domain outputs have isolation cells
when driving a logic cone in a different (or always-on) domain.
Checks: isolation present, correct enable polarity, enable from AO domain.

Usage:
    python 34_isolation_cell_checker.py --report iso_report.rpt
"""

import re
import argparse

SAMPLE_REPORT = """\
# Isolation Cell Report — PA Compiler
# Design: soc_top

ISOLATION INSTANCES:
Instance: iso_cpu_req     DOMAIN: PD_CPU  PORT: cpu_req     ISO_TYPE: ISO_HIGH
  ISO_ENABLE: iso_en_cpu  ISO_EN_DOMAIN: PD_TOP  STATUS: CORRECT
  When PD_CPU is OFF, output held HIGH to prevent X-propagation

Instance: iso_cpu_data    DOMAIN: PD_CPU  PORT: cpu_data[31:0]  ISO_TYPE: ISO_LOW
  ISO_ENABLE: iso_en_cpu  ISO_EN_DOMAIN: PD_TOP  STATUS: CORRECT
  When PD_CPU is OFF, output held LOW

Instance: iso_dma_grant   DOMAIN: PD_DMA  PORT: dma_grant   ISO_TYPE: ISO_HIGH
  ISO_ENABLE: iso_en_dma_wrong  ISO_EN_DOMAIN: PD_DMA  STATUS: ERROR_ENABLE_NOT_AO
  ISO enable signal comes from gated domain PD_DMA — must come from always-on domain

MISSING ISOLATION:
Port: cpu_status[7:0]  DOMAIN: PD_CPU  DRIVEN_DOMAIN: PD_TOP  REQUIRED: YES
  STATUS: MISSING — Port drives logic in always-on domain without isolation
Port: dma_burst_len    DOMAIN: PD_DMA  DRIVEN_DOMAIN: PD_CPU  REQUIRED: YES
  STATUS: MISSING — Control signal drives clock-gating in PD_CPU

ISOLATION SUMMARY:
Correct    : 2
Errors     : 1
Missing    : 2
Total Required: 5
"""


def parse_iso_report(text):
    instances = []
    missing   = []

    for m in re.finditer(
        r"Instance:\s*(\S+)\s+DOMAIN:\s*(\S+)\s+PORT:\s*(\S+)\s+ISO_TYPE:\s*(\S+)\s+"
        r"ISO_ENABLE:\s*(\S+)\s+ISO_EN_DOMAIN:\s*(\S+)\s+STATUS:\s*(\S+)",
        text, re.DOTALL
    ):
        instances.append({
            "instance":      m.group(1),
            "domain":        m.group(2),
            "port":          m.group(3),
            "iso_type":      m.group(4),
            "iso_enable":    m.group(5),
            "enable_domain": m.group(6),
            "status":        m.group(7),
        })

    for m in re.finditer(
        r"Port:\s*(\S+)\s+DOMAIN:\s*(\S+)\s+DRIVEN_DOMAIN:\s*(\S+)\s+REQUIRED:\s*YES\s+"
        r"STATUS:\s*MISSING",
        text, re.DOTALL
    ):
        missing.append({
            "port":          m.group(1),
            "domain":        m.group(2),
            "driven_domain": m.group(3),
        })

    correct = sum(1 for i in instances if i["status"] == "CORRECT")
    errors  = sum(1 for i in instances if "ERROR" in i["status"])
    return instances, missing, correct, errors


def print_report(instances, missing, correct, errors):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    total = correct + errors + len(missing)

    print("=" * 65)
    print("  ISOLATION CELL CHECK REPORT")
    print("=" * 65)
    print(f"\n  Total Required : {total}")
    print(f"  Correct        : {GREEN}{correct}{RST}")
    print(f"  Errors         : {RED}{errors}{RST}")
    print(f"  Missing        : {RED}{len(missing)}{RST}")

    if instances:
        print(f"\n  Isolation Instances:")
        print(f"  {'INSTANCE':<20} {'DOMAIN':<10} {'PORT':<22} {'TYPE':<10} {'EN DOMAIN':<12} {'STATUS'}")
        print("  " + "-" * 90)
        for iso in instances:
            col = GREEN if iso["status"] == "CORRECT" else RED
            print(f"  {iso['instance']:<20} {iso['domain']:<10} {iso['port']:<22} "
                  f"{iso['iso_type']:<10} {iso['enable_domain']:<12} {col}{iso['status']}{RST}")

    if missing:
        print(f"\n  {RED}Missing Isolation Cells:{RST}")
        for m in missing:
            print(f"    Port: {m['port']:<25}  {m['domain']} → {m['driven_domain']}")
            print(f"    Fix: Add ISO cell in UPF: set_isolation <port> -domain {m['domain']} "
                  f"-applies_to outputs -clamp_value 0/1")

    # Error details
    error_instances = [i for i in instances if "ERROR" in i["status"]]
    if error_instances:
        print(f"\n  {RED}Isolation Cell Errors:{RST}")
        for iso in error_instances:
            if "ENABLE_NOT_AO" in iso["status"]:
                print(f"    {iso['instance']}: ISO enable '{iso['iso_enable']}' comes from "
                      f"gated domain '{iso['enable_domain']}'")
                print(f"    Fix: Route ISO enable from always-on domain (e.g., PD_TOP)")

    verdict = correct == total and errors == 0 and len(missing) == 0
    print(f"\n  {'ISOLATION CHECK: '+GREEN+'PASS ✓'+RST if verdict else 'ISOLATION CHECK: '+RED+'FAIL'+RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Check isolation cell placement")
parser.add_argument("--report", help="Isolation cell report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

instances, missing, correct, errors = parse_iso_report(text)
print_report(instances, missing, correct, errors)
