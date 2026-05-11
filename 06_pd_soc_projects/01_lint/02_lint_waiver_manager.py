"""
Project: Lint Waiver Manager
Tool context: Spyglass Lint / Questa Lint
What it does: Manages a lint waiver database stored as JSON.
Supports adding, listing, searching, validating, and exporting waivers.
Ensures every waiver has a justification, owner, and date.

Usage:
    python 02_lint_waiver_manager.py --action list
    python 02_lint_waiver_manager.py --action add --rule W_NET_NO_LOAD --module cpu_core \
        --owner john --justification "Intentional debug net, not used in production"
    python 02_lint_waiver_manager.py --action search --rule W_REGS_NO_RESET
    python 02_lint_waiver_manager.py --action validate
    python 02_lint_waiver_manager.py --action export --output waivers.csv
"""

import json
import csv
import argparse
import os
from datetime import datetime

WAIVER_DB = "lint_waivers.json"

# ── Waiver schema ─────────────────────────────────────────────────────────────
# Each waiver entry:
# {
#   "id":            "W-001",
#   "rule":          "W_NET_NO_LOAD",
#   "module":        "cpu_core",
#   "file":          "rtl/cpu_core.v",        # optional
#   "line":          245,                      # optional, 0 = all lines
#   "justification": "Intentional debug net",
#   "owner":         "john",
#   "date":          "2024-01-15",
#   "approved":      true
# }
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_WAIVERS = [
    {"id": "W-001", "rule": "W_NET_NO_LOAD",   "module": "cpu_core",
     "file": "rtl/cpu_core.v", "line": 245,
     "justification": "Debug net, tied off in synthesis",
     "owner": "alice", "date": "2024-01-10", "approved": True},
    {"id": "W-002", "rule": "W_PORT_UNCONNECTED", "module": "soc_top",
     "file": "rtl/soc_top.v", "line": 200,
     "justification": "Test port, not used in functional mode",
     "owner": "bob", "date": "2024-01-12", "approved": True},
    {"id": "W-003", "rule": "W_CONST_DRIVER",  "module": "dma_ctrl",
     "file": "rtl/dma_ctrl.v", "line": 55,
     "justification": "",       # intentionally empty to test validation
     "owner": "", "date": "2024-01-14", "approved": False},
]


def load_db():
    if os.path.exists(WAIVER_DB):
        with open(WAIVER_DB) as f:
            return json.load(f)
    return SAMPLE_WAIVERS  # start with sample data


def save_db(waivers):
    with open(WAIVER_DB, "w") as f:
        json.dump(waivers, f, indent=2)


def next_id(waivers):
    if not waivers:
        return "W-001"
    nums = [int(w["id"].split("-")[1]) for w in waivers]
    return f"W-{max(nums)+1:03d}"


def action_list(waivers):
    print(f"\n{'ID':<8} {'RULE':<25} {'MODULE':<15} {'OWNER':<10} {'APPROVED'}")
    print("-" * 75)
    for w in waivers:
        approved = "YES" if w["approved"] else "NO"
        print(f"{w['id']:<8} {w['rule']:<25} {w['module']:<15} {w['owner']:<10} {approved}")
    print(f"\nTotal waivers: {len(waivers)}")


def action_add(waivers, rule, module, file, line, justification, owner):
    new_waiver = {
        "id":            next_id(waivers),
        "rule":          rule,
        "module":        module,
        "file":          file or "",
        "line":          int(line) if line else 0,
        "justification": justification,
        "owner":         owner,
        "date":          datetime.today().strftime("%Y-%m-%d"),
        "approved":      False,  # requires review before approval
    }
    waivers.append(new_waiver)
    save_db(waivers)
    print(f"Added waiver {new_waiver['id']} for rule '{rule}' in module '{module}'")


def action_search(waivers, rule=None, module=None):
    results = waivers
    if rule:
        results = [w for w in results if rule.upper() in w["rule"].upper()]
    if module:
        results = [w for w in results if module.lower() in w["module"].lower()]
    print(f"\nFound {len(results)} matching waivers:")
    action_list(results)


def action_validate(waivers):
    """Check that all waivers have required fields filled in."""
    issues = []
    for w in waivers:
        if not w.get("justification"):
            issues.append(f"  {w['id']} — missing justification")
        if not w.get("owner"):
            issues.append(f"  {w['id']} — missing owner")
        if not w.get("date"):
            issues.append(f"  {w['id']} — missing date")

    if issues:
        print(f"\nValidation FAILED — {len(issues)} issue(s) found:")
        for issue in issues:
            print(issue)
    else:
        print(f"\nValidation PASSED — all {len(waivers)} waivers are complete.")


def action_export(waivers, output):
    fields = ["id", "rule", "module", "file", "line", "justification", "owner", "date", "approved"]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(waivers)
    print(f"Exported {len(waivers)} waivers to {output}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Lint waiver database manager")
parser.add_argument("--action",        required=True,
                    choices=["list", "add", "search", "validate", "export"])
parser.add_argument("--rule",          help="Lint rule name")
parser.add_argument("--module",        help="RTL module name")
parser.add_argument("--file",          help="RTL file path")
parser.add_argument("--line",          help="Line number")
parser.add_argument("--justification", help="Waiver justification text")
parser.add_argument("--owner",         help="Waiver owner (engineer name)")
parser.add_argument("--output",        help="Output file for export")
args = parser.parse_args()

waivers = load_db()

if args.action == "list":
    action_list(waivers)
elif args.action == "add":
    action_add(waivers, args.rule, args.module, args.file,
                args.line, args.justification or "", args.owner or "")
elif args.action == "search":
    action_search(waivers, rule=args.rule, module=args.module)
elif args.action == "validate":
    action_validate(waivers)
elif args.action == "export":
    action_export(waivers, args.output or "waivers.csv")
