"""
Project: DFT Rule Violation Parser
Tool context: SpyGlass DFT / Synopsys DFTMAX DRC
What it does: Parses DFT design rule check (DRC) violations from SpyGlass DFT
or DFTMAX. Categorizes violations by rule type (controllability, observability,
scan insertion rules) and outputs fix recommendations.

Usage:
    python 14_dft_violation_parser.py --report dft_drc.rpt
"""

import re
import argparse
from collections import defaultdict, Counter

SAMPLE_REPORT = """\
# SpyGlass DFT Report
# Design: soc_top
# Run: 2024-01-15

RULE:DFT_C01 SEVERITY:Error MODULE:cpu_core FILE:rtl/cpu_core.v LINE:245
  Signal 'dbg_en' has poor controllability from primary inputs
  Fix: Add scan enable tie-off or test-mode mux

RULE:DFT_C01 SEVERITY:Error MODULE:dma_ctrl FILE:rtl/dma_ctrl.v LINE:88
  Signal 'dma_req' has poor controllability from primary inputs
  Fix: Add scan enable tie-off or test-mode mux

RULE:DFT_O01 SEVERITY:Error MODULE:alu_unit FILE:rtl/alu_unit.v LINE:134
  Internal node 'carry_chain[3]' is unobservable
  Fix: Add scan flip-flop or test point

RULE:DFT_S01 SEVERITY:Error MODULE:pll_ctrl FILE:rtl/pll_ctrl.v LINE:78
  Asynchronous set/reset on flip-flop 'pll_lock_reg' blocks scan
  Fix: Make reset synchronous or add test-mode override

RULE:DFT_S02 SEVERITY:Warning MODULE:fifo_ctrl FILE:rtl/fifo_ctrl.v LINE:200
  Flip-flop 'fifo_full_reg' has multiple clocks — may cause scan issues
  Fix: Multiplex clocks using scan_clk during scan mode

RULE:DFT_C02 SEVERITY:Warning MODULE:apb_bridge FILE:rtl/apb_bridge.v LINE:67
  Tri-state bus 'apb_data' reduces testability
  Fix: Disable tri-state during scan using test_mode signal

RULE:DFT_O02 SEVERITY:Info MODULE:soc_top FILE:rtl/soc_top.v LINE:300
  Output port 'status_out[7:0]' partially observable (6/8 bits)
  Fix: Route all status bits to observable output
"""

# DFT rule categories
RULE_CATEGORIES = {
    "DFT_C": "Controllability",
    "DFT_O": "Observability",
    "DFT_S": "Scan",
    "DFT_M": "MBIST",
    "DFT_B": "Boundary Scan",
}

FIX_PRIORITY = {"Error": "MUST FIX", "Warning": "SHOULD FIX", "Info": "REVIEW"}


def parse_dft_report(text):
    """Parse DFT DRC violations from report text."""
    # Match rule header lines
    header_pat = re.compile(
        r"RULE:(\S+)\s+SEVERITY:(\S+)\s+MODULE:(\S+)\s+FILE:(\S+)\s+LINE:(\d+)"
    )
    # Match description line (first non-blank line after header)
    violations = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        m = header_pat.match(lines[i].strip())
        if m:
            rule, sev, module, file_, line = (
                m.group(1), m.group(2), m.group(3), m.group(4), int(m.group(5))
            )
            description = lines[i+1].strip() if i+1 < len(lines) else ""
            fix         = lines[i+2].strip() if i+2 < len(lines) else ""
            fix         = fix.replace("Fix:", "").strip() if fix.startswith("Fix:") else ""

            # Determine category
            cat = "UNKNOWN"
            for prefix, label in RULE_CATEGORIES.items():
                if rule.startswith(prefix):
                    cat = label
                    break

            violations.append({
                "rule":        rule,
                "severity":    sev,
                "category":    cat,
                "module":      module,
                "file":        file_,
                "line":        line,
                "description": description,
                "fix":         fix,
                "priority":    FIX_PRIORITY.get(sev, "REVIEW"),
            })
            i += 3
            continue
        i += 1
    return violations


def print_dft_report(violations):
    RED   = "\033[31m"
    YEL   = "\033[33m"
    CYN   = "\033[36m"
    RST   = "\033[0m"
    SEV_COLOR = {"Error": RED, "Warning": YEL, "Info": CYN}

    sev_counts = Counter(v["severity"] for v in violations)
    cat_counts = Counter(v["category"] for v in violations)

    print("=" * 65)
    print("  DFT DRC VIOLATION REPORT")
    print("=" * 65)
    print(f"\n  Total violations: {len(violations)}")

    print("\n  Severity Breakdown:")
    for sev in ["Error", "Warning", "Info"]:
        c = sev_counts.get(sev, 0)
        print(f"    {SEV_COLOR.get(sev,'')}{sev:<10}{RST}  {c}")

    print("\n  By Category:")
    for cat, cnt in cat_counts.most_common():
        print(f"    {cat:<20} {cnt}")

    print("\n  Violation Details (Errors first):")
    print("  " + "-" * 70)
    for v in sorted(violations, key=lambda x: {"Error":0,"Warning":1,"Info":2}.get(x["severity"],3)):
        col = SEV_COLOR.get(v["severity"], "")
        print(f"\n  [{col}{v['severity']}{RST}] {v['rule']} — {v['category']}")
        print(f"    Module : {v['module']}  ({v['file']}:{v['line']})")
        print(f"    Issue  : {v['description']}")
        if v["fix"]:
            print(f"    Fix    : {v['fix']}")
        print(f"    Action : {v['priority']}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Parse DFT DRC violations")
parser.add_argument("--report", help="DFT DRC report file")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

violations = parse_dft_report(text)
print_dft_report(violations)
