"""
Project: Lint Waiver Validator
Tool context: Spyglass Lint / Questa Lint
What it does: Cross-validates a waiver file against the current lint report.
Finds: (1) waivers with no matching violation (stale waivers),
       (2) violations with no waiver (unwaived), and
       (3) waivers missing mandatory fields (incomplete).
Essential before submitting a lint sign-off package.

Usage:
    python 06_lint_waiver_validator.py --report lint.rpt --waivers waivers.json
"""

import re
import json
import argparse
import os

SAMPLE_REPORT = """\
Error|W_NET_NO_LOAD|cpu_core|rtl/cpu_core.v:245|Net 'int_bus' has no load
Error|W_MUX_SEL_UNDRIVEN|apb_bridge|rtl/apb_bridge.v:67|Mux select undriven
Warning|W_PORT_UNCONNECTED|soc_top|rtl/soc_top.v:200|Port unconnected
Fatal|W_COMB_LOOP|fifo_ctrl|rtl/fifo_ctrl.v:134|Combinational loop detected
"""

SAMPLE_WAIVERS = [
    # Valid waiver that matches a violation
    {"id": "W-001", "rule": "W_NET_NO_LOAD", "module": "cpu_core",
     "justification": "Debug net, tied off in synthesis", "owner": "alice", "date": "2024-01-10"},
    # Stale waiver — no matching violation in the report
    {"id": "W-002", "rule": "W_REGS_NO_RESET", "module": "alu_unit",
     "justification": "Reset handled externally", "owner": "bob", "date": "2024-01-12"},
    # Incomplete waiver — missing justification
    {"id": "W-003", "rule": "W_PORT_UNCONNECTED", "module": "soc_top",
     "justification": "", "owner": "", "date": "2024-01-14"},
    # Valid waiver for a fatal — must have owner and justification
    {"id": "W-004", "rule": "W_COMB_LOOP", "module": "fifo_ctrl",
     "justification": "Loop is in test logic, not functional path", "owner": "charlie", "date": "2024-01-15"},
]

MANDATORY_FIELDS = ["justification", "owner", "date"]


def parse_violations(text):
    """Return list of violation dicts from lint report text."""
    pattern = re.compile(r"^(Fatal|Error|Warning|Info)\|(\S+)\|(\S+)\|(.+):(\d+)\|(.+)$")
    violations = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        m = pattern.match(line)
        if m:
            violations.append({
                "severity": m.group(1),
                "rule":     m.group(2),
                "module":   m.group(3),
            })
    return violations


def validate(violations, waivers):
    # Build a lookup: (rule, module) → violation severity
    viol_lookup = {(v["rule"], v["module"]): v["severity"] for v in violations}
    waiver_keys = {(w["rule"], w["module"]) for w in waivers}

    issues      = {"incomplete": [], "stale": [], "unwaived_fatal": [], "unwaived_error": []}
    valid_count = 0

    for w in waivers:
        key = (w["rule"], w["module"])

        # Check completeness
        missing = [f for f in MANDATORY_FIELDS if not w.get(f)]
        if missing:
            issues["incomplete"].append((w["id"], w["rule"], w["module"], missing))
            continue  # skip further checks for incomplete waivers

        # Check if waiver matches any violation in the report
        if key not in viol_lookup:
            issues["stale"].append((w["id"], w["rule"], w["module"]))
        else:
            valid_count += 1

    # Find violations that have no corresponding waiver
    for v in violations:
        key = (v["rule"], v["module"])
        if key not in waiver_keys:
            if v["severity"] == "Fatal":
                issues["unwaived_fatal"].append((v["rule"], v["module"], v["severity"]))
            elif v["severity"] == "Error":
                issues["unwaived_error"].append((v["rule"], v["module"], v["severity"]))

    return valid_count, issues


def print_validation_report(valid_count, issues, total_waivers, total_viols):
    RED   = "\033[31m"
    GREEN = "\033[32m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print("=" * 60)
    print("  LINT WAIVER VALIDATION REPORT")
    print("=" * 60)
    print(f"\n  Total violations in report : {total_viols}")
    print(f"  Total waivers in database  : {total_waivers}")
    print(f"  Valid matched waivers      : {GREEN}{valid_count}{RST}")

    # Incomplete waivers
    if issues["incomplete"]:
        print(f"\n  {RED}INCOMPLETE WAIVERS ({len(issues['incomplete'])}){RST} — missing mandatory fields:")
        for wid, rule, mod, missing in issues["incomplete"]:
            print(f"    {wid} | {rule} | {mod} | missing: {', '.join(missing)}")

    # Stale waivers
    if issues["stale"]:
        print(f"\n  {YEL}STALE WAIVERS ({len(issues['stale'])}){RST} — no matching violation:")
        for wid, rule, mod in issues["stale"]:
            print(f"    {wid} | {rule} | {mod}")

    # Unwaived fatal/errors
    if issues["unwaived_fatal"]:
        print(f"\n  {RED}UNWAIVED FATAL VIOLATIONS ({len(issues['unwaived_fatal'])}){RST}:")
        for rule, mod, sev in issues["unwaived_fatal"]:
            print(f"    {sev:<8} | {rule} | {mod}")

    if issues["unwaived_error"]:
        print(f"\n  {RED}UNWAIVED ERROR VIOLATIONS ({len(issues['unwaived_error'])}){RST}:")
        for rule, mod, sev in issues["unwaived_error"]:
            print(f"    {sev:<8} | {rule} | {mod}")

    total_issues = sum(len(v) for v in issues.values())
    if total_issues == 0:
        print(f"\n  {GREEN}VALIDATION PASSED — All waivers are valid and complete.{RST}")
    else:
        print(f"\n  {RED}VALIDATION FAILED — {total_issues} issue(s) found. Resolve before sign-off.{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Validate lint waivers against a lint report")
parser.add_argument("--report",  help="Lint report file")
parser.add_argument("--waivers", help="Waiver JSON file")
args = parser.parse_args()

report_text = open(args.report).read()  if args.report  else SAMPLE_REPORT
waivers     = json.load(open(args.waivers)) if args.waivers else SAMPLE_WAIVERS

if not args.report:
    print("No files given — using built-in sample data.\n")

violations = parse_violations(report_text)
valid_count, issues = validate(violations, waivers)
print_validation_report(valid_count, issues, len(waivers), len(violations))
