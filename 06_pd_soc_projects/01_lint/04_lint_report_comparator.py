"""
Project: Lint Report Comparator (Delta Report)
Tool context: Spyglass Lint / Questa Lint
What it does: Compares two lint reports (e.g., before and after an RTL fix)
and shows what violations are NEW, what were FIXED, and what REMAIN.
Critical for regression tracking and tapeout sign-off milestones.

Usage:
    python 04_lint_report_comparator.py --old run1/lint.rpt --new run2/lint.rpt
    python 04_lint_report_comparator.py --old run1/lint.rpt --new run2/lint.rpt --output delta.csv
"""

import re
import csv
import argparse

# ── Simulated old and new report texts ───────────────────────────────────────
OLD_REPORT = """\
Fatal|W_COMB_LOOP|fifo_ctrl|rtl/fifo_ctrl.v:134|Combinational loop detected
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:245|Net 'int_bus' has no load
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:312|Net 'dbg_out' has no load
Error|W_MUX_SEL_UNDRIVEN|apb_bridge|rtl/apb_bridge.v:67|Mux select undriven
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:88|Register has no reset
Warning|W_PORT_UNCONNECTED|soc_top|rtl/soc_top.v:200|Port unconnected
"""

NEW_REPORT = """\
Fatal|W_COMB_LOOP|fifo_ctrl|rtl/fifo_ctrl.v:134|Combinational loop detected
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:245|Net 'int_bus' has no load
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:88|Register has no reset
Error|W_CLK_UNGATED|pll_ctrl|rtl/pll_ctrl.v:78|Clock used without gating
Error|W_CLK_UNGATED|pll_ctrl|rtl/pll_ctrl.v:90|Clock used without gating
"""


def parse_to_set(text):
    """
    Parse violations into a set of tuples (severity, rule, module, file, line).
    Using a tuple as a key allows set-based diff operations.
    """
    pattern = re.compile(r"^(Fatal|Error|Warning|Info)\|(\S+)\|(\S+)\|(.+):(\d+)\|(.+)$")
    violations = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        m = pattern.match(line)
        if m:
            key = (m.group(1), m.group(2), m.group(3), m.group(4), int(m.group(5)))
            violations[key] = m.group(6)  # key → message
    return violations


def compare_reports(old_viols, new_viols):
    old_keys = set(old_viols.keys())
    new_keys = set(new_viols.keys())

    fixed     = old_keys - new_keys   # in old, not in new  → FIXED
    new_added = new_keys - old_keys   # in new, not in old  → NEW (regression)
    unchanged = old_keys & new_keys   # in both             → REMAIN

    return fixed, new_added, unchanged


def format_entry(key, msg, status):
    sev, rule, module, file_, line = key
    return {
        "status":   status,
        "severity": sev,
        "rule":     rule,
        "module":   module,
        "file":     file_,
        "line":     line,
        "message":  msg,
    }


COLORS = {
    "NEW":     "\033[91m",   # red    — regression
    "FIXED":   "\033[92m",   # green  — improvement
    "REMAIN":  "\033[33m",   # yellow — still open
    "RESET":   "\033[0m",
}


def print_delta(old_viols, new_viols, fixed, new_added, unchanged):
    print("=" * 65)
    print("  LINT REPORT COMPARISON (DELTA)")
    print("=" * 65)
    print(f"\n  Old report violations: {len(old_viols)}")
    print(f"  New report violations: {len(new_viols)}")
    print(f"\n  {COLORS['FIXED']}FIXED   (resolved): {len(fixed)}{COLORS['RESET']}")
    print(f"  {COLORS['NEW']}NEW     (regressed): {len(new_added)}{COLORS['RESET']}")
    print(f"  {COLORS['REMAIN']}REMAIN  (unchanged): {len(unchanged)}{COLORS['RESET']}")

    def show_section(title, keys, source_dict, color):
        if not keys:
            return
        print(f"\n  {color}── {title} ──{COLORS['RESET']}")
        print(f"  {'SEV':<8} {'RULE':<25} {'MODULE':<15} {'FILE:LINE'}")
        print("  " + "-" * 75)
        for key in sorted(keys):
            sev, rule, module, file_, line = key
            print(f"  {sev:<8} {rule:<25} {module:<15} {file_}:{line}")

    show_section("FIXED VIOLATIONS",     fixed,     old_viols, COLORS["FIXED"])
    show_section("NEW VIOLATIONS (REGRESSIONS)", new_added, new_viols, COLORS["NEW"])
    show_section("REMAINING VIOLATIONS", unchanged, old_viols, COLORS["REMAIN"])


def export_csv(old_viols, new_viols, fixed, new_added, unchanged, output):
    rows = []
    for key in fixed:
        rows.append(format_entry(key, old_viols[key], "FIXED"))
    for key in new_added:
        rows.append(format_entry(key, new_viols[key], "NEW"))
    for key in unchanged:
        rows.append(format_entry(key, old_viols[key], "REMAIN"))

    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n  Delta exported to: {output}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Compare two lint reports for delta")
parser.add_argument("--old",    help="Old (baseline) lint report file")
parser.add_argument("--new",    help="New lint report file")
parser.add_argument("--output", help="Export delta to CSV")
args = parser.parse_args()

old_text = open(args.old).read() if args.old else OLD_REPORT
new_text = open(args.new).read() if args.new else NEW_REPORT

if not args.old:
    print("No files given — using built-in sample reports.\n")

old_viols = parse_to_set(old_text)
new_viols = parse_to_set(new_text)
fixed, new_added, unchanged = compare_reports(old_viols, new_viols)
print_delta(old_viols, new_viols, fixed, new_added, unchanged)

if args.output and (fixed or new_added or unchanged):
    export_csv(old_viols, new_viols, fixed, new_added, unchanged, args.output)
