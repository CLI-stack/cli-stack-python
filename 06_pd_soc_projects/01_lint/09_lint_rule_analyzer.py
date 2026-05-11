"""
Project: Lint Rule Analyzer
Tool context: Spyglass Lint / Questa Lint
What it does: Analyzes which lint rules fire most across an entire project,
grouped by rule category (clock, reset, connectivity, etc.).
Helps prioritize rule enablement and waiver strategy.

Usage:
    python 09_lint_rule_analyzer.py --report lint.rpt
    python 09_lint_rule_analyzer.py --report lint.rpt --category CLOCK
"""

import re
import argparse
from collections import Counter, defaultdict

SAMPLE_REPORT = """\
Fatal|W_COMB_LOOP|fifo_ctrl|rtl/fifo_ctrl.v:134|Combinational loop
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:245|Net has no load
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:312|Net has no load
Error|W_NET_NO_LOAD|alu_unit|rtl/alu_unit.v:100|Net has no load
Error|W_MUX_SEL_UNDRIVEN|apb_bridge|rtl/apb_bridge.v:67|Mux select undriven
Error|W_CLK_UNGATED|pll_ctrl|rtl/pll_ctrl.v:78|Clock used without gating
Error|W_CLK_UNGATED|pll_ctrl|rtl/pll_ctrl.v:90|Clock used without gating
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:88|Register has no reset
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:91|Register has no reset
Warning|W_REGS_NO_RESET|dma_ctrl|rtl/dma_ctrl.v:120|Register has no reset
Warning|W_PORT_UNCONNECTED|soc_top|rtl/soc_top.v:200|Port unconnected
Info|W_CONST_DRIVER|dma_ctrl|rtl/dma_ctrl.v:55|Constant driver
"""

# Rule → category mapping (subset of common Spyglass rules)
RULE_CATEGORIES = {
    "W_COMB_LOOP":       "COMBO",
    "W_NET_NO_LOAD":     "CONNECTIVITY",
    "W_MUX_SEL_UNDRIVEN":"CONNECTIVITY",
    "W_PORT_UNCONNECTED":"CONNECTIVITY",
    "W_REGS_NO_RESET":   "RESET",
    "W_REGS_ASYNC_RST":  "RESET",
    "W_CLK_UNGATED":     "CLOCK",
    "W_CLK_GLITCH":      "CLOCK",
    "W_CONST_DRIVER":    "MISC",
    "W_HIER_FANOUT":     "MISC",
}


def categorize(rule):
    for pattern, cat in RULE_CATEGORIES.items():
        if rule.startswith(pattern.split("_")[0] + "_" + pattern.split("_")[1]):
            return RULE_CATEGORIES.get(rule, "UNCATEGORIZED")
    return RULE_CATEGORIES.get(rule, "UNCATEGORIZED")


def parse_violations(text):
    pattern = re.compile(r"^(Fatal|Error|Warning|Info)\|(\S+)\|(\S+)\|(.+):(\d+)\|(.+)$")
    violations = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = pattern.match(line)
        if m:
            violations.append({
                "severity": m.group(1),
                "rule":     m.group(2),
                "module":   m.group(3),
            })
    return violations


def analyze(violations, category_filter=None):
    by_rule     = Counter(v["rule"] for v in violations)
    by_category = defaultdict(lambda: defaultdict(int))

    for v in violations:
        cat = categorize(v["rule"])
        by_category[cat][v["rule"]] += 1

    if category_filter:
        category_filter = category_filter.upper()

    print("=" * 65)
    print("  LINT RULE ANALYZER")
    print("=" * 65)

    # Top rules overall
    print(f"\n  Top Rules (all categories):")
    print(f"  {'RULE':<30} {'COUNT':>6}  {'SEV BREAKDOWN'}")
    print("  " + "-" * 70)

    sev_by_rule = defaultdict(Counter)
    for v in violations:
        sev_by_rule[v["rule"]][v["severity"]] += 1

    for rule, count in by_rule.most_common():
        sev_str = "  ".join(f"{s}:{sev_by_rule[rule][s]}"
                            for s in ["Fatal","Error","Warning","Info"]
                            if sev_by_rule[rule][s] > 0)
        print(f"  {rule:<30} {count:>6}  {sev_str}")

    # By category
    print(f"\n  By Category:")
    print("  " + "-" * 65)
    for cat, rules in sorted(by_category.items()):
        if category_filter and cat != category_filter:
            continue
        cat_total = sum(rules.values())
        print(f"\n  [{cat}] — {cat_total} violations")
        for rule, cnt in sorted(rules.items(), key=lambda x: -x[1]):
            bar = "█" * min(cnt * 3, 30)
            print(f"    {rule:<30} {cnt:>4}  {bar}")

    # Sign-off risk assessment
    print(f"\n  Sign-off Risk Assessment:")
    fatal_rules = {v["rule"] for v in violations if v["severity"] == "Fatal"}
    error_rules = {v["rule"] for v in violations if v["severity"] == "Error"}

    if fatal_rules:
        print(f"  CRITICAL — Fatal rules must be fixed or waived:")
        for r in fatal_rules:
            print(f"    • {r}")
    if error_rules:
        print(f"  HIGH     — Error rules require waiver or fix:")
        for r in error_rules:
            print(f"    • {r}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Analyze lint rule distribution")
parser.add_argument("--report",   help="Lint report file")
parser.add_argument("--category", help="Filter by category e.g. CLOCK, RESET, CONNECTIVITY")
args = parser.parse_args()

text = open(args.report).read() if args.report else SAMPLE_REPORT
if not args.report:
    print("No report file — using sample data.\n")

violations = parse_violations(text)
analyze(violations, category_filter=args.category)
