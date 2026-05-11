"""
Project: DFT Waiver Manager
Tool context: SpyGlass DFT / Synopsys DFTMAX
What it does: Manages DFT-specific waivers (controllability, observability,
scan rule violations). Tracks waiver status, approval, and expiry.
Generates waiver TCL files for tool input.

Usage:
    python 17_dft_waiver_manager.py --action list
    python 17_dft_waiver_manager.py --action add --rule DFT_C01 --module cpu_core \
           --justification "Debug port, not required for production test" --owner alice
    python 17_dft_waiver_manager.py --action export-tcl --output dft_waivers.tcl
"""

import json
import argparse
import os
from datetime import datetime

WAIVER_DB = "dft_waivers.json"

SAMPLE_WAIVERS = [
    {
        "id":            "DFT-W001",
        "rule":          "DFT_C01",
        "module":        "cpu_core",
        "signal":        "dbg_en",
        "justification": "Debug-only signal, controlled by JTAG TAP in test mode",
        "owner":         "alice",
        "date":          "2024-01-10",
        "approved":      True,
        "expiry":        "2024-12-31",
    },
    {
        "id":            "DFT-W002",
        "rule":          "DFT_S01",
        "module":        "pll_ctrl",
        "signal":        "pll_lock_reg",
        "justification": "PLL lock register uses async reset — handled by PLL IP vendor",
        "owner":         "bob",
        "date":          "2024-01-12",
        "approved":      True,
        "expiry":        "2024-12-31",
    },
    {
        "id":            "DFT-W003",
        "rule":          "DFT_O01",
        "module":        "alu_unit",
        "signal":        "carry_chain[3]",
        "justification": "",   # intentionally incomplete
        "owner":         "",
        "date":          "2024-01-14",
        "approved":      False,
        "expiry":        "",
    },
]


def load_db():
    if os.path.exists(WAIVER_DB):
        with open(WAIVER_DB) as f:
            return json.load(f)
    return SAMPLE_WAIVERS


def save_db(waivers):
    with open(WAIVER_DB, "w") as f:
        json.dump(waivers, f, indent=2)


def next_id(waivers):
    nums = [int(w["id"].split("-W")[1]) for w in waivers if "-W" in w["id"]]
    return f"DFT-W{(max(nums)+1 if nums else 1):03d}"


def action_list(waivers):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"
    print(f"\n  {'ID':<10} {'RULE':<10} {'MODULE':<15} {'SIGNAL':<20} {'OWNER':<8} {'APPROVED'}")
    print("  " + "-" * 80)
    for w in waivers:
        appr = f"{GREEN}YES{RST}" if w["approved"] else f"{RED}NO{RST}"
        print(f"  {w['id']:<10} {w['rule']:<10} {w['module']:<15} "
              f"{w.get('signal',''):<20} {w['owner']:<8} {appr}")
    print(f"\n  Total: {len(waivers)} waivers  "
          f"(Approved: {sum(1 for w in waivers if w['approved'])})")


def action_add(waivers, rule, module, signal, justification, owner):
    w = {
        "id":            next_id(waivers),
        "rule":          rule,
        "module":        module,
        "signal":        signal or "",
        "justification": justification or "",
        "owner":         owner or "",
        "date":          datetime.today().strftime("%Y-%m-%d"),
        "approved":      False,
        "expiry":        "",
    }
    waivers.append(w)
    save_db(waivers)
    print(f"Added {w['id']}: {rule} on {module}/{signal or '*'}")


def action_validate(waivers):
    issues = []
    for w in waivers:
        if not w.get("justification"):
            issues.append(f"  {w['id']} — missing justification")
        if not w.get("owner"):
            issues.append(f"  {w['id']} — missing owner")
        if not w.get("approved"):
            issues.append(f"  {w['id']} — not yet approved")

    if issues:
        print(f"\n  Validation FAILED — {len(issues)} issue(s):")
        for i in issues:
            print(i)
    else:
        print(f"\n  Validation PASSED — all {len(waivers)} waivers complete and approved.")


def action_export_tcl(waivers, output):
    """Generate a Spyglass waiver TCL file."""
    lines = [
        "# DFT Waiver File — Auto-generated",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]
    for w in waivers:
        if w.get("approved"):
            lines.append(f"# {w['id']} | Owner: {w['owner']} | Date: {w['date']}")
            lines.append(f"# Justification: {w['justification']}")
            sig_clause = f" -signal {{{w['signal']}}}" if w.get("signal") else ""
            lines.append(
                f"waive -rule {w['rule']} -module {{{w['module']}}}{sig_clause}"
            )
            lines.append("")

    with open(output, "w") as f:
        f.write("\n".join(lines))

    approved = sum(1 for w in waivers if w["approved"])
    print(f"Exported {approved} approved waivers to TCL: {output}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="DFT waiver database manager")
parser.add_argument("--action",        required=True,
                    choices=["list", "add", "validate", "export-tcl"])
parser.add_argument("--rule",          help="DFT rule e.g. DFT_C01")
parser.add_argument("--module",        help="RTL module")
parser.add_argument("--signal",        help="Signal name")
parser.add_argument("--justification", help="Justification text")
parser.add_argument("--owner",         help="Owner engineer name")
parser.add_argument("--output",        default="dft_waivers.tcl")
args = parser.parse_args()

waivers = load_db()

if args.action == "list":
    action_list(waivers)
elif args.action == "add":
    action_add(waivers, args.rule, args.module, args.signal,
                args.justification, args.owner)
elif args.action == "validate":
    action_validate(waivers)
elif args.action == "export-tcl":
    action_export_tcl(waivers, args.output)
