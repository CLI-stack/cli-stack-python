"""
Project: Lint Sign-Off Checker
Tool context: Spyglass Lint / Questa Lint
What it does: Checks whether a design meets tapeout lint sign-off criteria:
  - Zero Fatal violations
  - Zero unwaived Errors
  - All waivers validated (owner + justification)
  - Waiver count within approved limit
Prints a pass/fail gate report.

Usage:
    python 10_lint_signoff_checker.py --report lint.rpt --waivers waivers.json
"""

import re
import json
import argparse
import sys
from datetime import datetime

SAMPLE_REPORT = """\
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:245|Net has no load
Warning|W_REGS_NO_RESET|alu_unit|rtl/alu_unit.v:88|Register has no reset
Warning|W_PORT_UNCONNECTED|soc_top|rtl/soc_top.v:200|Port unconnected
"""

SAMPLE_WAIVERS = [
    {"id": "W-001", "rule": "W_NET_NO_LOAD", "module": "cpu_core",
     "justification": "Debug net", "owner": "alice", "date": "2024-01-15"},
    {"id": "W-002", "rule": "W_PORT_UNCONNECTED", "module": "soc_top",
     "justification": "Test port not used in production",
     "owner": "bob", "date": "2024-01-15"},
]

# Sign-off rules
CRITERIA = {
    "max_fatal":         0,      # Zero fatals allowed
    "max_unwaived_error":0,      # Zero unwaived errors
    "max_waivers":       50,     # Total waivers must not exceed this
}


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
                "severity": m.group(1), "rule": m.group(2), "module": m.group(3),
            })
    return violations


def check_signoff(violations, waivers):
    waiver_keys = {(w["rule"], w["module"]) for w in waivers}
    results = []

    # ── Gate 1: Zero Fatal violations ────────────────────────────────────────
    fatals = [v for v in violations if v["severity"] == "Fatal"]
    gate1  = len(fatals) == 0
    results.append({
        "gate":   "G1 — Zero Fatal violations",
        "pass":   gate1,
        "detail": f"Found {len(fatals)} Fatal(s)" if fatals else "No Fatals",
    })

    # ── Gate 2: Zero unwaived Errors ─────────────────────────────────────────
    errors         = [v for v in violations if v["severity"] == "Error"]
    unwaived_errors= [v for v in errors if (v["rule"], v["module"]) not in waiver_keys]
    gate2          = len(unwaived_errors) <= CRITERIA["max_unwaived_error"]
    results.append({
        "gate":   "G2 — Zero unwaived Error violations",
        "pass":   gate2,
        "detail": (f"{len(unwaived_errors)} unwaived Error(s): "
                   + ", ".join(f"{v['rule']}/{v['module']}" for v in unwaived_errors[:3]))
                   if unwaived_errors else "All Errors waived",
    })

    # ── Gate 3: Waiver completeness ───────────────────────────────────────────
    incomplete = [w for w in waivers if not w.get("justification") or not w.get("owner")]
    gate3      = len(incomplete) == 0
    results.append({
        "gate":   "G3 — All waivers have owner + justification",
        "pass":   gate3,
        "detail": (f"{len(incomplete)} incomplete waiver(s): "
                   + ", ".join(w["id"] for w in incomplete))
                   if incomplete else f"All {len(waivers)} waivers complete",
    })

    # ── Gate 4: Waiver count limit ────────────────────────────────────────────
    gate4 = len(waivers) <= CRITERIA["max_waivers"]
    results.append({
        "gate":   f"G4 — Total waivers ≤ {CRITERIA['max_waivers']}",
        "pass":   gate4,
        "detail": f"Waiver count: {len(waivers)} / {CRITERIA['max_waivers']}",
    })

    return results


def print_report(results, design="soc_top"):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    print("=" * 60)
    print(f"  LINT SIGN-OFF CHECK — {design}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    all_pass = all(r["pass"] for r in results)
    for r in results:
        status = f"{GREEN}PASS{RST}" if r["pass"] else f"{RED}FAIL{RST}"
        print(f"\n  [{status}] {r['gate']}")
        print(f"         {r['detail']}")

    print("\n" + "=" * 60)
    if all_pass:
        print(f"  {GREEN}OVERALL: SIGN-OFF APPROVED{RST}")
    else:
        failed = sum(1 for r in results if not r["pass"])
        print(f"  {RED}OVERALL: SIGN-OFF BLOCKED — {failed} gate(s) failed{RST}")
    print("=" * 60)

    return all_pass


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Lint tapeout sign-off gate check")
parser.add_argument("--report",  help="Lint report file")
parser.add_argument("--waivers", help="Waiver JSON file")
parser.add_argument("--design",  default="soc_top")
args = parser.parse_args()

text    = open(args.report).read()         if args.report  else SAMPLE_REPORT
waivers = json.load(open(args.waivers))   if args.waivers else SAMPLE_WAIVERS

if not args.report:
    print("No files given — using sample data.\n")

violations = parse_violations(text)
results    = check_signoff(violations, waivers)
passed     = print_report(results, design=args.design)

sys.exit(0 if passed else 1)
