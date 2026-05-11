"""
Project: CDC Report Comparator
Tool context: Spyglass CDC / VC CDC
What it does: Compares two CDC reports to track new violations (regressions)
and resolved violations across design iterations.

Usage:
    python 24_cdc_report_comparator.py --old run1/cdc.rpt --new run2/cdc.rpt
"""

import re
import argparse

OLD_REPORT = """\
RULE:CDC_CONV_RULE SEVERITY:Error MODULE:cpu_core LINE:245 SRC:clk_core DST:clk_axi
RULE:CDC_CONV_RULE SEVERITY:Error MODULE:dma_ctrl LINE:88 SRC:clk_axi DST:clk_core
RULE:CDC_GLITCH SEVERITY:Fatal MODULE:clk_ctrl LINE:312 SRC:clk_pll DST:clk_safe
RULE:CDC_MUX_SEL SEVERITY:Error MODULE:apb_bridge LINE:134 SRC:clk_core DST:clk_apb
RULE:CDC_NO_SYNC SEVERITY:Warning MODULE:uart_ctrl LINE:67 SRC:clk_uart DST:clk_core
"""

NEW_REPORT = """\
RULE:CDC_CONV_RULE SEVERITY:Error MODULE:cpu_core LINE:245 SRC:clk_core DST:clk_axi
RULE:CDC_GLITCH SEVERITY:Fatal MODULE:clk_ctrl LINE:312 SRC:clk_pll DST:clk_safe
RULE:CDC_NO_SYNC SEVERITY:Warning MODULE:uart_ctrl LINE:67 SRC:clk_uart DST:clk_core
RULE:CDC_ASYNC_RST SEVERITY:Warning MODULE:pll_ctrl LINE:200 SRC:clk_pll DST:clk_core
RULE:CDC_CONV_RULE SEVERITY:Error MODULE:spi_ctrl LINE:445 SRC:clk_spi DST:clk_core
"""


def parse_report(text):
    pat = re.compile(
        r"RULE:(\S+)\s+SEVERITY:(\S+)\s+MODULE:(\S+)\s+LINE:(\d+)"
        r"(?:\s+SRC:(\S+)\s+DST:(\S+))?"
    )
    result = {}
    for m in pat.finditer(text):
        key = (m.group(1), m.group(3), int(m.group(4)))
        result[key] = {
            "severity": m.group(2),
            "src":      m.group(5) or "?",
            "dst":      m.group(6) or "?",
        }
    return result


def compare(old, new):
    ok  = set(old.keys())
    nk  = set(new.keys())
    return ok - nk, nk - ok, ok & nk


def print_delta(old, new, fixed, new_added, unchanged):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print("=" * 65)
    print("  CDC REPORT DELTA COMPARISON")
    print("=" * 65)
    print(f"\n  Old report: {len(old)} violations")
    print(f"  New report: {len(new)} violations  (delta: {len(new)-len(old):+d})")
    print(f"\n  {GREEN}FIXED  : {len(fixed)}{RST}")
    print(f"  {RED}NEW    : {len(new_added)}{RST}")
    print(f"  {YEL}REMAIN : {len(unchanged)}{RST}")

    def show(title, keys, source, color):
        if not keys:
            return
        print(f"\n  {color}── {title} ({len(keys)}) ──{RST}")
        print(f"  {'RULE':<18} {'SEV':<9} {'MODULE':<15} {'LINE':>5} {'SRC→DST'}")
        print("  " + "-" * 70)
        for key in sorted(keys):
            rule, mod, line = key
            info = source.get(key, {})
            print(f"  {rule:<18} {info.get('severity','?'):<9} {mod:<15} "
                  f"{line:>5} {info.get('src','?')}→{info.get('dst','?')}")

    show("FIXED VIOLATIONS",         fixed,     old, GREEN)
    show("NEW VIOLATIONS (REGRESSIONS)", new_added, new, RED)
    show("REMAINING VIOLATIONS",     unchanged, old, YEL)

    # Highlight fatal regressions
    fatal_new = [k for k in new_added if new.get(k, {}).get("severity") == "Fatal"]
    if fatal_new:
        print(f"\n  {RED}CRITICAL: {len(fatal_new)} new Fatal CDC violation(s)! Must fix before milestone.{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Compare two CDC violation reports")
parser.add_argument("--old", help="Old CDC report")
parser.add_argument("--new", help="New CDC report")
args = parser.parse_args()

old_text = open(args.old).read() if args.old else OLD_REPORT
new_text = open(args.new).read() if args.new else NEW_REPORT
if not args.old:
    print("No files given — using sample data.\n")

old = parse_report(old_text)
new = parse_report(new_text)
fixed, new_added, unchanged = compare(old, new)
print_delta(old, new, fixed, new_added, unchanged)
