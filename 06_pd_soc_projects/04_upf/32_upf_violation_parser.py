"""
Project: UPF Violation Parser
Tool context: Synopsys PA Compiler / Cadence Voltus / Mentor Calibre Power
What it does: Parses UPF-related violations from a power analysis tool report.
Categories: missing isolation, missing level shifter, invalid power state,
power domain connectivity issues.

Usage:
    python 32_upf_violation_parser.py --report pa_violations.rpt
"""

import re
import argparse
from collections import Counter

SAMPLE_REPORT = """\
# PA Compiler — UPF Violations Report
# Design: soc_top
# Date: 2024-01-15

VIOLATION: PA-ISO-001  SEVERITY: Error  DOMAIN: PD_CPU  MODULE: cpu_core  LINE: 245
  Missing isolation cell on output port 'cpu_req' from PD_CPU to PD_TOP
  Port drives logic in PD_TOP when PD_CPU is OFF
  Fix: Add ISO_HIGH or ISO_LOW cell at domain boundary

VIOLATION: PA-ISO-001  SEVERITY: Error  DOMAIN: PD_DMA  MODULE: dma_ctrl  LINE: 88
  Missing isolation cell on output port 'dma_grant' from PD_DMA to PD_TOP
  Fix: Add isolation cell, ensure ISO enable comes from always-on domain

VIOLATION: PA-LS-001   SEVERITY: Error  DOMAIN: PD_PERIPH  MODULE: apb_bridge  LINE: 134
  Missing level shifter on signal 'apb_data[31:0]' from VDD_L (0.8V) to VDD (1.0V)
  Crossing from PD_PERIPH (VDD_L) to PD_CPU (VDD) without level shifting
  Fix: Insert LS_UP level shifter between the domains

VIOLATION: PA-LS-001   SEVERITY: Error  DOMAIN: PD_CPU  MODULE: cpu_core  LINE: 312
  Missing level shifter on signal 'int_req' from VDD (1.0V) to VDD_L (0.8V)
  Fix: Insert LS_DOWN level shifter

VIOLATION: PA-RET-001  SEVERITY: Warning  DOMAIN: PD_CPU  MODULE: cpu_core  LINE: 200
  Register 'state_reg[7:0]' in PD_CPU has no retention strategy
  Register content lost when PD_CPU transitions to OFF state
  Fix: Replace with retention flip-flop or add save/restore logic

VIOLATION: PA-AO-001   SEVERITY: Warning  DOMAIN: PD_DMA  MODULE: dma_ctrl  LINE: 67
  Always-on signal 'dma_en' routed through power-gated domain PD_DMA
  Signal may be corrupted during power-down
  Fix: Reroute through always-on domain or add isolation

VIOLATION: PA-STATE-001 SEVERITY: Fatal  DOMAIN: PD_TOP  MODULE: soc_top  LINE: 400
  Invalid power state transition: PD_CPU cannot be ON when PD_TOP is OFF
  Power state table violation in UPF add_power_state commands
  Fix: Update power state table to enforce valid state combinations
"""

RULE_DESC = {
    "PA-ISO-001":   "Missing isolation cell at power domain boundary",
    "PA-LS-001":    "Missing level shifter for voltage crossing",
    "PA-RET-001":   "Register has no retention strategy",
    "PA-AO-001":    "Always-on signal routed through gated domain",
    "PA-STATE-001": "Invalid power state table entry",
    "PA-CONN-001":  "Power domain connectivity error",
}

SEV_RANK = {"Fatal": 0, "Error": 1, "Warning": 2, "Info": 3}


def parse_pa_violations(text):
    violations = []
    header_pat = re.compile(
        r"VIOLATION:\s*(\S+)\s+SEVERITY:\s*(\S+)\s+DOMAIN:\s*(\S+)\s+MODULE:\s*(\S+)\s+LINE:\s*(\d+)"
    )
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = header_pat.match(lines[i].strip())
        if m:
            rule, sev, domain, module, line_no = (
                m.group(1), m.group(2), m.group(3), m.group(4), int(m.group(5))
            )
            desc = lines[i+1].strip() if i+1 < len(lines) else ""
            extra = lines[i+2].strip() if i+2 < len(lines) else ""
            fix   = lines[i+3].strip() if i+3 < len(lines) else ""
            fix   = fix.replace("Fix:", "").strip() if "Fix:" in fix else ""

            violations.append({
                "rule":    rule,
                "severity":sev,
                "domain":  domain,
                "module":  module,
                "line":    line_no,
                "desc":    desc,
                "extra":   extra if not extra.startswith("Fix:") else "",
                "fix":     fix,
                "category":RULE_DESC.get(rule, rule),
            })
            i += 4
            continue
        i += 1
    return violations


def print_pa_report(violations):
    RED  = "\033[31m"
    YEL  = "\033[33m"
    GRN  = "\033[92m"
    RST  = "\033[0m"
    SEV_C= {"Fatal": "\033[91m", "Error": RED, "Warning": YEL}

    sev_counts  = Counter(v["severity"] for v in violations)
    rule_counts = Counter(v["rule"]     for v in violations)
    dom_counts  = Counter(v["domain"]   for v in violations)

    print("=" * 65)
    print("  UPF / POWER ANALYSIS VIOLATION REPORT")
    print("=" * 65)
    print(f"\n  Total violations : {len(violations)}")
    for sev in ["Fatal", "Error", "Warning"]:
        print(f"    {SEV_C.get(sev,'')}{sev:<10}{RST} {sev_counts.get(sev,0)}")

    print("\n  By Rule Category:")
    for rule, cnt in rule_counts.most_common():
        print(f"    {rule:<15} {cnt}  — {RULE_DESC.get(rule,'')}")

    print("\n  By Power Domain:")
    for domain, cnt in dom_counts.most_common():
        print(f"    {domain:<15} {cnt}")

    print("\n  Violation Details:")
    print("  " + "-" * 80)
    for v in sorted(violations, key=lambda x: SEV_RANK.get(x["severity"], 9)):
        col = SEV_C.get(v["severity"], "")
        print(f"\n  [{col}{v['severity']}{RST}] {v['rule']} — {v['category']}")
        print(f"    Domain  : {v['domain']}  Module: {v['module']} (line {v['line']})")
        print(f"    Issue   : {v['desc']}")
        if v["extra"]:
            print(f"            {v['extra']}")
        if v["fix"]:
            print(f"    Fix     : {v['fix']}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Parse UPF power analysis violations")
parser.add_argument("--report", help="PA violation report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

violations = parse_pa_violations(text)
print_pa_report(violations)
