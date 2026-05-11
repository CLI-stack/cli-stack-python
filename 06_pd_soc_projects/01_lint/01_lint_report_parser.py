"""
Project: Lint Report Parser
Tool context: Spyglass Lint / Questa Lint / Cadence HAL
What it does: Parses a lint report file and extracts all violations
with their rule name, severity, module, file path, and line number.
Outputs a clean structured summary to the terminal and optionally to CSV.

Usage:
    python 01_lint_report_parser.py --report spyglass_lint.rpt
    python 01_lint_report_parser.py --report spyglass_lint.rpt --output violations.csv
"""

import re
import csv
import argparse
from collections import defaultdict

# ── Sample Spyglass lint report format ──────────────────────────────────────
# Each violation line looks like:
#   <severity>|<rule>|<module>|<file>:<line>|<message>
# e.g.:
#   Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:245|Net 'int_bus' has no load
# ────────────────────────────────────────────────────────────────────────────

SAMPLE_REPORT = """\
# SpyGlass Lint Report - Run: 2024-01-15 09:00:00
# Design: soc_top
# Rules: ALL
#
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:245|Net 'int_bus' has no load
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:312|Net 'dbg_out' has no load
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:88|Register 'result_reg' has no reset
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:91|Register 'carry_reg' has no reset
Fatal|W_COMB_LOOP|fifo_ctrl|rtl/fifo_ctrl.v:134|Combinational loop detected through 'fifo_full'
Error|W_MUX_SEL_UNDRIVEN|apb_bridge|rtl/apb_bridge.v:67|Mux select 'sel[2]' undriven
Warning|W_PORT_UNCONNECTED|soc_top|rtl/soc_top.v:200|Port 'test_out' unconnected
Info|W_CONST_DRIVER|dma_ctrl|rtl/dma_ctrl.v:55|Signal 'burst_en' driven by constant 1
Warning|W_REGS_NO_RESET|dma_ctrl|rtl/dma_ctrl.v:120|Register 'addr_latch' has no reset
Error|W_CLK_UNGATED|pll_ctrl|rtl/pll_ctrl.v:78|Clock 'ref_clk' used without gating
"""

# ── Severity priority for sorting ────────────────────────────────────────────
SEVERITY_RANK = {"Fatal": 0, "Error": 1, "Warning": 2, "Info": 3}


def parse_lint_report(filepath=None, text=None):
    """
    Parse a lint report file (or raw text) into a list of violation dicts.
    Each dict contains: severity, rule, module, file, line, message.
    """
    violations = []
    # Regex to match one violation line:  severity|rule|module|file:line|message
    pattern = re.compile(r"^(Fatal|Error|Warning|Info)\|(\S+)\|(\S+)\|(.+):(\d+)\|(.+)$")

    lines = text.splitlines() if text else open(filepath).readlines()

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("#") or not line:
            continue  # skip comments and blank lines

        match = pattern.match(line)
        if match:
            violations.append({
                "severity": match.group(1),
                "rule":     match.group(2),
                "module":   match.group(3),
                "file":     match.group(4),
                "line":     int(match.group(5)),
                "message":  match.group(6),
            })

    return violations


def print_summary(violations):
    """Print a grouped summary of violations."""
    # Count by severity
    by_severity = defaultdict(int)
    by_rule     = defaultdict(int)
    by_module   = defaultdict(int)

    for v in violations:
        by_severity[v["severity"]] += 1
        by_rule[v["rule"]]         += 1
        by_module[v["module"]]     += 1

    print("=" * 60)
    print("  LINT REPORT SUMMARY")
    print("=" * 60)
    print(f"\n  Total violations: {len(violations)}\n")

    print("  By Severity:")
    for sev in ["Fatal", "Error", "Warning", "Info"]:
        count = by_severity.get(sev, 0)
        bar   = "#" * count
        print(f"    {sev:<10} {count:>4}  {bar}")

    print("\n  Top Rules:")
    for rule, count in sorted(by_rule.items(), key=lambda x: -x[1])[:5]:
        print(f"    {rule:<30} {count}")

    print("\n  Top Modules:")
    for mod, count in sorted(by_module.items(), key=lambda x: -x[1])[:5]:
        print(f"    {mod:<30} {count}")

    print("\n  Violation Detail (sorted by severity):")
    print(f"  {'SEV':<8} {'RULE':<25} {'MODULE':<15} {'FILE:LINE':<30} {'MESSAGE'}")
    print("  " + "-" * 100)

    sorted_viols = sorted(violations, key=lambda v: SEVERITY_RANK.get(v["severity"], 9))
    for v in sorted_viols:
        file_line = f"{v['file']}:{v['line']}"
        print(f"  {v['severity']:<8} {v['rule']:<25} {v['module']:<15} {file_line:<30} {v['message']}")


def export_to_csv(violations, output_path):
    """Write violations to a CSV file."""
    fieldnames = ["severity", "rule", "module", "file", "line", "message"]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(violations)
    print(f"\n  Exported {len(violations)} violations to: {output_path}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Parse Spyglass/Questa lint reports")
parser.add_argument("--report", help="Path to lint report file")
parser.add_argument("--output", help="Output CSV file (optional)")
args = parser.parse_args()

if args.report:
    violations = parse_lint_report(filepath=args.report)
else:
    print("No report file given — using built-in sample data.\n")
    violations = parse_lint_report(text=SAMPLE_REPORT)

print_summary(violations)

if args.output:
    export_to_csv(violations, args.output)
