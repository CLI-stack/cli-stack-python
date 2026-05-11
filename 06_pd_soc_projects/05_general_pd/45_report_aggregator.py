"""
Project: Multi-Flow Report Aggregator
Tool context: Spyglass / TetraMAX / VC CDC / PA Compiler
What it does: Scans a run directory, finds all flow reports (lint, DFT, CDC, RDC, UPF),
extracts key counts from each, and generates a single aggregated summary.
Useful for milestone emails and status updates.

Usage:
    python 45_report_aggregator.py --rundir /path/to/run
    python 45_report_aggregator.py  (uses built-in sample)
"""

import re
import os
import argparse
from datetime import datetime

# Map of report filename patterns to extractors
REPORT_PARSERS = {
    "lint": {
        "pattern": ["lint.rpt", "spyglass_lint.rpt"],
        "extract": lambda t: {
            "fatal":   len(re.findall(r"^Fatal\|", t, re.MULTILINE)),
            "error":   len(re.findall(r"^Error\|", t, re.MULTILINE)),
            "warning": len(re.findall(r"^Warning\|", t, re.MULTILINE)),
        },
    },
    "cdc": {
        "pattern": ["cdc.rpt", "spyglass_cdc.rpt"],
        "extract": lambda t: {
            "fatal":   len(re.findall(r"SEVERITY:Fatal",  t)),
            "error":   len(re.findall(r"SEVERITY:Error",  t)),
            "warning": len(re.findall(r"SEVERITY:Warning",t)),
        },
    },
    "rdc": {
        "pattern": ["rdc.rpt", "spyglass_rdc.rpt"],
        "extract": lambda t: {
            "fatal":   len(re.findall(r"SEVERITY:Fatal",  t)),
            "error":   len(re.findall(r"SEVERITY:Error",  t)),
            "warning": len(re.findall(r"SEVERITY:Warning",t)),
        },
    },
    "dft": {
        "pattern": ["dft.rpt", "atpg_coverage.rpt"],
        "extract": lambda t: {
            "sa_cov":    float(m.group(1)) if (m:=re.search(r"Fault coverage\s*:\s*([\d.]+)%", t)) else None,
            "patterns":  int(m.group(1))   if (m:=re.search(r"Pattern count\s*:\s*(\d+)", t)) else None,
        },
    },
    "upf": {
        "pattern": ["pa.rpt", "pa_violations.rpt"],
        "extract": lambda t: {
            "fatal":   len(re.findall(r"SEVERITY:\s*Fatal",  t)),
            "error":   len(re.findall(r"SEVERITY:\s*Error",  t)),
            "warning": len(re.findall(r"SEVERITY:\s*Warning",t)),
        },
    },
}

# Simulate in-memory reports (would read from disk in production)
SAMPLE_REPORTS = {
    "lint": "Fatal|W_COMB_LOOP|fifo_ctrl|f.v:1|loop\nError|W_NET|cpu|f.v:2|net\nWarning|W_RST|alu|f.v:3|rst\n",
    "cdc":  "RULE:CDC_GLITCH SEVERITY:Fatal MODULE:a LINE:1\nRULE:CDC SEVERITY:Error MODULE:b LINE:2\n",
    "rdc":  "RULE:RDC SEVERITY:Error MODULE:c LINE:1\nRULE:RDC SEVERITY:Warning MODULE:d LINE:2\n",
    "dft":  "Fault coverage   :  98.78 %\nPattern count    :   4215\n",
    "upf":  "VIOLATION:PA-ISO SEVERITY: Error DOMAIN:D MODULE:m LINE:1\nVIOLATION:PA-LS SEVERITY: Warning DOMAIN:E MODULE:n LINE:2\n",
}


def find_and_parse_reports(rundir):
    """Scan rundir for known report files and parse them."""
    results = {}
    if not os.path.isdir(rundir):
        return results

    for flow, config in REPORT_PARSERS.items():
        for pattern in config["pattern"]:
            filepath = os.path.join(rundir, pattern)
            if os.path.exists(filepath):
                text = open(filepath).read()
                results[flow] = config["extract"](text)
                results[flow]["_file"] = filepath
                break

    return results


def aggregate_samples():
    """Use built-in samples when no real files are available."""
    results = {}
    for flow, text in SAMPLE_REPORTS.items():
        extractor = REPORT_PARSERS[flow]["extract"]
        results[flow] = extractor(text)
        results[flow]["_file"] = f"(sample:{flow}.rpt)"
    return results


def print_summary(results, rundir=""):
    RED  = "\033[91m"
    GRN  = "\033[92m"
    YEL  = "\033[33m"
    RST  = "\033[0m"

    print("=" * 65)
    print(f"  MULTI-FLOW REPORT AGGREGATOR")
    print(f"  Run dir : {rundir or '(sample data)'}")
    print(f"  Date    : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 65)

    any_fatal = False
    for flow in ["lint", "cdc", "rdc", "dft", "upf"]:
        data = results.get(flow)
        if not data:
            print(f"\n  [{flow.upper():<5}] {YEL}No report found{RST}")
            continue

        file_name = data.get("_file", "?")
        print(f"\n  [{flow.upper():<5}] {file_name}")

        if flow == "dft":
            cov = data.get("sa_cov")
            pat = data.get("patterns")
            cov_col = GRN if (cov and cov >= 99.0) else RED
            print(f"           SA Coverage  : {cov_col}{cov:.2f}%{RST}" if cov else "           SA Coverage  : N/A")
            print(f"           Patterns     : {pat:,}" if pat else "           Patterns     : N/A")
        else:
            fatal   = data.get("fatal",   0)
            error   = data.get("error",   0)
            warning = data.get("warning", 0)
            if fatal: any_fatal = True
            f_col = RED if fatal else GRN
            e_col = RED if error else GRN
            print(f"           Fatal   : {f_col}{fatal}{RST}  Error : {e_col}{error}{RST}  Warning : {warning}")

    print("\n" + "=" * 65)
    if any_fatal:
        print(f"  {RED}SIGN-OFF BLOCKED — Fatal violations found in one or more flows.{RST}")
    else:
        print(f"  {GRN}No Fatals detected — review Errors before sign-off.{RST}")
    print("=" * 65)


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Aggregate reports from multiple flows")
parser.add_argument("--rundir", help="Run directory containing report files")
args = parser.parse_args()

if args.rundir:
    results = find_and_parse_reports(args.rundir)
    if not results:
        print(f"No reports found in {args.rundir}  — using sample data.\n")
        results = aggregate_samples()
else:
    print("No rundir given — using sample data.\n")
    results = aggregate_samples()

print_summary(results, rundir=args.rundir or "")
