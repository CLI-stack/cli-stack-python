"""
Project: EDA Tool Run Log Analyzer
Tool context: Spyglass / DC / Genus / PA Compiler / VC CDC / TetraMAX
What it does: Analyzes EDA tool run logs for errors, warnings, and runtime
information. Extracts tool messages, memory usage, CPU time, and flags
issues that need engineer attention. Works with any EDA tool log format.

Usage:
    python 43_run_log_analyzer.py --log spyglass_run.log
    python 43_run_log_analyzer.py --log *.log --tool spyglass
"""

import re
import argparse
import os
from collections import Counter, defaultdict

SAMPLE_LOG = """\
# Spyglass Lint Run Log
# Tool: SpyGlass 2023.06
# Start: 2024-01-15 09:00:00

Info: Reading design files...
Info: Elaborating design 'soc_top'...
Warning: CDC_CONV_RULE: Clock crossing detected in cpu_core (rtl/cpu_core.v:245)
Error: W_COMB_LOOP: Combinational loop in fifo_ctrl (rtl/fifo_ctrl.v:134)
Warning: W_REGS_NO_RESET: Register without reset in alu_unit:88
Warning: W_REGS_NO_RESET: Register without reset in dma_ctrl:120
Error: W_NET_NO_LOAD: Net has no load in cpu_core:245
Error: W_MUX_SEL_UNDRIVEN: Mux select undriven in apb_bridge:67
Info: Analysis complete.
Info: Generating reports...
Info: CPU time: 1245.3 seconds
Info: Peak memory: 8234 MB
Info: Run ended: 2024-01-15 09:20:45
Info: Exit status: 0 (success)
"""

# Common EDA tool error patterns
PATTERNS = {
    "error":   re.compile(r"\bError\b[:\s]+(.+)", re.IGNORECASE),
    "warning": re.compile(r"\bWarning\b[:\s]+(.+)", re.IGNORECASE),
    "fatal":   re.compile(r"\b(Fatal|FATAL)\b[:\s]+(.+)"),
    "cpu":     re.compile(r"CPU time[:\s]+([\d.]+)\s*(seconds?|s\b)", re.IGNORECASE),
    "mem":     re.compile(r"Peak memory[:\s]+([\d.]+)\s*(MB|GB)", re.IGNORECASE),
    "exit":    re.compile(r"Exit status[:\s]+(\d+)", re.IGNORECASE),
    "tool":    re.compile(r"Tool[:\s]+(\S+)", re.IGNORECASE),
}


def analyze_log(text):
    results = {
        "errors":   [],
        "warnings": [],
        "fatals":   [],
        "cpu_time": None,
        "mem_peak": None,
        "exit_code":None,
    }

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        m = PATTERNS["fatal"].search(line)
        if m:
            results["fatals"].append(line)
            continue

        m = PATTERNS["error"].search(line)
        if m:
            results["errors"].append(line)
            continue

        m = PATTERNS["warning"].search(line)
        if m:
            results["warnings"].append(line)

        for key in ("cpu", "mem", "exit"):
            m = PATTERNS[key].search(line)
            if m:
                val = m.group(1)
                if key == "cpu":
                    results["cpu_time"] = float(val)
                elif key == "mem":
                    unit = m.group(2).upper()
                    results["mem_peak"] = f"{val} {unit}"
                elif key == "exit":
                    results["exit_code"] = int(val)

    return results


def print_analysis(results, log_path=""):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print("=" * 65)
    print(f"  EDA RUN LOG ANALYSIS")
    if log_path:
        print(f"  File: {log_path}")
    print("=" * 65)

    # Runtime
    print("\n  Run Statistics:")
    cpu = results["cpu_time"]
    if cpu:
        cpu_min = cpu / 60
        print(f"    CPU time   : {cpu:.1f}s  ({cpu_min:.1f} min)")
        if cpu_min > 60:
            print(f"    {YEL}Note: Run took > 1 hour — consider optimizing constraints.{RST}")
    if results["mem_peak"]:
        print(f"    Peak memory: {results['mem_peak']}")
        mem_val = float(str(results["mem_peak"]).split()[0])
        if "GB" in str(results["mem_peak"]) and mem_val > 64:
            print(f"    {YEL}Note: High memory usage — may hit machine limits.{RST}")

    exit_code = results["exit_code"]
    if exit_code is not None:
        ec_col = GREEN if exit_code == 0 else RED
        print(f"    Exit code  : {ec_col}{exit_code} ({'SUCCESS' if exit_code == 0 else 'FAILURE'}){RST}")

    # Message counts
    print(f"\n  Message Summary:")
    print(f"    {RED}Fatal   : {len(results['fatals'])}{RST}")
    print(f"    {RED}Error   : {len(results['errors'])}{RST}")
    print(f"    {YEL}Warning : {len(results['warnings'])}{RST}")

    if results["fatals"]:
        print(f"\n  {RED}Fatal Messages:{RST}")
        for msg in results["fatals"][:5]:
            print(f"    {msg}")

    if results["errors"]:
        print(f"\n  {RED}Error Messages (first 10):{RST}")
        for msg in results["errors"][:10]:
            print(f"    {msg[:100]}")
        if len(results["errors"]) > 10:
            print(f"    ... and {len(results['errors']) - 10} more errors")

    if results["warnings"]:
        # Categorize warnings by rule
        rule_pat = re.compile(r"(W_\S+|CDC_\S+|DFT_\S+|PA-\S+|RDC_\S+)")
        rule_counts = Counter()
        for w in results["warnings"]:
            m = rule_pat.search(w)
            if m:
                rule_counts[m.group(1)] += 1

        if rule_counts:
            print(f"\n  Warning Distribution by Rule:")
            for rule, cnt in rule_counts.most_common(8):
                print(f"    {rule:<30} {cnt}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Analyze EDA tool run logs")
parser.add_argument("--log",  help="Log file path (or glob)")
parser.add_argument("--tool", help="Tool name hint (optional)")
args = parser.parse_args()

if args.log and os.path.exists(args.log):
    text = open(args.log).read()
    results = analyze_log(text)
    print_analysis(results, log_path=args.log)
else:
    if args.log:
        print(f"Log file not found: {args.log}  — using sample data.\n")
    else:
        print("No log file — using sample data.\n")
    results = analyze_log(SAMPLE_LOG)
    print_analysis(results)
