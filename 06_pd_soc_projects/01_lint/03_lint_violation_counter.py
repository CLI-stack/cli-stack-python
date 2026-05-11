"""
Project: Lint Violation Counter and Top Offender Report
Tool context: Spyglass Lint / Questa Lint
What it does: Reads a lint report and produces ranked summaries —
top modules, top rules, and severity breakdown. Useful for prioritizing
what to fix first before a tapeout milestone.

Usage:
    python 03_lint_violation_counter.py --report lint.rpt
    python 03_lint_violation_counter.py --report lint.rpt --top 10 --severity Error
"""

import re
import argparse
from collections import Counter, defaultdict

SAMPLE_REPORT = """\
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:245|Net has no load
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:312|Net has no load
Error|W_NET_NO_LOAD|alu_unit|rtl/alu_unit.v:100|Net has no load
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:88|Register has no reset
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:91|Register has no reset
Warning|W_REGS_NO_RESET|dma_ctrl|rtl/dma_ctrl.v:120|Register has no reset
Warning|W_REGS_NO_RESET|dma_ctrl|rtl/dma_ctrl.v:130|Register has no reset
Fatal|W_COMB_LOOP|fifo_ctrl|rtl/fifo_ctrl.v:134|Combinational loop detected
Error|W_MUX_SEL_UNDRIVEN|apb_bridge|rtl/apb_bridge.v:67|Mux select undriven
Error|W_MUX_SEL_UNDRIVEN|apb_bridge|rtl/apb_bridge.v:72|Mux select undriven
Warning|W_PORT_UNCONNECTED|soc_top|rtl/soc_top.v:200|Port unconnected
Info|W_CONST_DRIVER|dma_ctrl|rtl/dma_ctrl.v:55|Signal driven by constant
Error|W_CLK_UNGATED|pll_ctrl|rtl/pll_ctrl.v:78|Clock used without gating
Error|W_CLK_UNGATED|pll_ctrl|rtl/pll_ctrl.v:90|Clock used without gating
Warning|W_REGS_NO_RESET|cpu_core|rtl/cpu_core.v:400|Register has no reset
"""

SEV_COLOR = {
    "Fatal":   "\033[91m",  # bright red
    "Error":   "\033[31m",  # red
    "Warning": "\033[33m",  # yellow
    "Info":    "\033[36m",  # cyan
    "RESET":   "\033[0m",
}


def parse_violations(text, severity_filter=None):
    pattern = re.compile(r"^(Fatal|Error|Warning|Info)\|(\S+)\|(\S+)\|(.+):(\d+)\|(.+)$")
    violations = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        m = pattern.match(line)
        if m:
            sev = m.group(1)
            if severity_filter and sev not in severity_filter:
                continue
            violations.append({
                "severity": sev,
                "rule":     m.group(2),
                "module":   m.group(3),
                "file":     m.group(4),
                "line":     int(m.group(5)),
                "message":  m.group(6),
            })
    return violations


def colored(text, sev):
    return f"{SEV_COLOR.get(sev, '')}{text}{SEV_COLOR['RESET']}"


def bar_chart(counts, top_n, label):
    """Print a simple horizontal bar chart."""
    sorted_items = sorted(counts.items(), key=lambda x: -x[1])[:top_n]
    max_count = sorted_items[0][1] if sorted_items else 1

    print(f"\n  Top {top_n} {label}:")
    print(f"  {'NAME':<35} {'COUNT':>6}  {'BAR'}")
    print("  " + "-" * 70)
    for name, count in sorted_items:
        bar_len = int(40 * count / max_count)
        bar = "█" * bar_len
        print(f"  {name:<35} {count:>6}  {bar}")


def print_report(violations, top_n):
    total = len(violations)
    sev_counts   = Counter(v["severity"] for v in violations)
    rule_counts  = Counter(v["rule"]     for v in violations)
    mod_counts   = Counter(v["module"]   for v in violations)

    print("=" * 60)
    print("  LINT VIOLATION COUNTER REPORT")
    print("=" * 60)
    print(f"\n  Total violations : {total}")

    print("\n  Severity Breakdown:")
    for sev in ["Fatal", "Error", "Warning", "Info"]:
        count = sev_counts.get(sev, 0)
        pct   = count / total * 100 if total else 0
        print(f"    {colored(sev, sev):<20} {count:>5}  ({pct:.1f}%)")

    bar_chart(rule_counts,  top_n, "Rules  (most violations)")
    bar_chart(mod_counts,   top_n, "Modules (most violations)")

    # Show modules with Fatal/Error only
    critical = [v for v in violations if v["severity"] in ("Fatal", "Error")]
    if critical:
        crit_mods = Counter(v["module"] for v in critical)
        print(f"\n  Modules with Fatal/Error ({len(critical)} violations):")
        for mod, count in crit_mods.most_common():
            print(f"    {mod:<30} {count}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Lint violation counter and ranker")
parser.add_argument("--report",   help="Lint report file path")
parser.add_argument("--top",      type=int, default=5, help="Top N items to show (default: 5)")
parser.add_argument("--severity", help="Filter by severity e.g. 'Fatal,Error'")
args = parser.parse_args()

sev_filter = set(args.severity.split(",")) if args.severity else None

if args.report:
    text = open(args.report).read()
else:
    print("No report file given — using sample data.\n")
    text = SAMPLE_REPORT

violations = parse_violations(text, severity_filter=sev_filter)
print_report(violations, args.top)
