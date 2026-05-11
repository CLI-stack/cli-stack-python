"""
Project: RDC Violation Parser
Tool context: Spyglass RDC / Synopsys VC RDC
What it does: Parses Reset Domain Crossing (RDC) violations.
RDC issues occur when signals cross between different reset domains,
leading to potential X-propagation or metastability at power-up.

Usage:
    python 25_rdc_violation_parser.py --report rdc_report.rpt
"""

import re
import argparse
from collections import Counter

SAMPLE_REPORT = """\
# SpyGlass RDC Report
# Design: soc_top
# Date: 2024-01-15

RULE:RDC_RESET_SYNC    SEVERITY:Error  MODULE:cpu_core  LINE:245
  Signal 'cpu_srst_n' driven by reset domain 'rstn_core' feeds module in 'rstn_axi'
  SRC_RESET: rstn_core   DEST_RESET: rstn_axi
  Fix: Add reset synchronizer between rstn_core and rstn_axi

RULE:RDC_RESET_FANOUT  SEVERITY:Error  MODULE:dma_ctrl  LINE:88
  Reset 'dma_rstn' has fanout into multiple reset domains without isolation
  SRC_RESET: rstn_axi   DEST_RESET: rstn_core, rstn_apb
  Fix: Isolate reset fanout per domain

RULE:RDC_ASSERT_DEASSERT  SEVERITY:Warning  MODULE:pll_ctrl  LINE:134
  Reset 'pll_rstn' asserted and de-asserted by different clock domains
  SRC_RESET: rstn_pll   DEST_RESET: rstn_core
  Fix: Use reset synchronizer to handle proper de-assertion sequencing

RULE:RDC_GLITCH_RST    SEVERITY:Fatal  MODULE:clk_ctrl  LINE:312
  Combinational logic on reset path 'glb_rstn' may glitch
  SRC_RESET: rstn_core   DEST_RESET: rstn_safe
  Fix: Register reset signal or use dedicated glitch-free reset mux

RULE:RDC_RESET_SYNC    SEVERITY:Error  MODULE:uart_ctrl  LINE:67
  Signal 'uart_rstn' missing synchronizer between rstn_uart and rstn_core
  SRC_RESET: rstn_uart   DEST_RESET: rstn_core
  Fix: Instantiate a 2-stage reset synchronizer cell

RULE:RDC_POWER_DOMAIN  SEVERITY:Warning  MODULE:soc_top  LINE:200
  Reset 'pd_rstn' crosses a power domain boundary without ISO cell on reset
  SRC_RESET: rstn_core   DEST_RESET: rstn_pd_off
  Fix: Add isolation cell on reset path at power domain boundary
"""

SEV_RANK = {"Fatal": 0, "Error": 1, "Warning": 2, "Info": 3}

RULE_DESC = {
    "RDC_RESET_SYNC":        "Missing reset synchronizer between domains",
    "RDC_RESET_FANOUT":      "Reset fanout into multiple domains without isolation",
    "RDC_ASSERT_DEASSERT":   "Improper reset assert/de-assert sequencing",
    "RDC_GLITCH_RST":        "Combinational glitch on reset path",
    "RDC_POWER_DOMAIN":      "Reset crossing power domain without isolation",
}


def parse_rdc_report(text):
    violations = []
    header_pat = re.compile(
        r"RULE:(\S+)\s+SEVERITY:(\S+)\s+MODULE:(\S+)\s+LINE:(\d+)"
    )
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = header_pat.match(lines[i].strip())
        if m:
            rule, sev, module, line_no = m.group(1), m.group(2), m.group(3), int(m.group(4))
            desc  = lines[i+1].strip() if i+1 < len(lines) else ""
            rst_l = lines[i+2].strip() if i+2 < len(lines) else ""
            fix_l = lines[i+3].strip() if i+3 < len(lines) else ""

            src_rst = re.search(r"SRC_RESET:\s*(\S+)", rst_l)
            dst_rst = re.search(r"DEST_RESET:\s*(.+)", rst_l)
            fix     = fix_l.replace("Fix:", "").strip() if "Fix:" in fix_l else ""

            violations.append({
                "rule":    rule,
                "severity":sev,
                "module":  module,
                "line":    line_no,
                "desc":    desc,
                "src_rst": src_rst.group(1) if src_rst else "?",
                "dst_rst": dst_rst.group(1).strip() if dst_rst else "?",
                "fix":     fix,
                "category":RULE_DESC.get(rule, rule),
            })
            i += 4
            continue
        i += 1
    return violations


def print_rdc_report(violations):
    RED  = "\033[31m"
    YEL  = "\033[33m"
    GRN  = "\033[92m"
    RST  = "\033[0m"
    SEV_C= {"Fatal": "\033[91m", "Error": RED, "Warning": YEL}

    sev_counts  = Counter(v["severity"] for v in violations)
    rule_counts = Counter(v["rule"]     for v in violations)

    print("=" * 65)
    print("  RDC VIOLATION REPORT")
    print("=" * 65)
    print(f"\n  Total violations: {len(violations)}")
    for sev in ["Fatal", "Error", "Warning"]:
        c = sev_counts.get(sev, 0)
        print(f"    {SEV_C.get(sev,'')}{sev:<12}{RST} {c}")

    print("\n  By Rule Type:")
    for rule, cnt in rule_counts.most_common():
        print(f"    {rule:<25} {cnt}  — {RULE_DESC.get(rule,'')}")

    print("\n  Violation Details:")
    print("  " + "-" * 80)
    for v in sorted(violations, key=lambda x: SEV_RANK.get(x["severity"], 9)):
        col = SEV_C.get(v["severity"], "")
        print(f"\n  [{col}{v['severity']}{RST}] {v['rule']}")
        print(f"    Module   : {v['module']} (line {v['line']})")
        print(f"    Resets   : {v['src_rst']} → {v['dst_rst']}")
        print(f"    Issue    : {v['desc']}")
        if v["fix"]:
            print(f"    Fix      : {v['fix']}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Parse RDC violation report")
parser.add_argument("--report", help="RDC report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

violations = parse_rdc_report(text)
print_rdc_report(violations)
