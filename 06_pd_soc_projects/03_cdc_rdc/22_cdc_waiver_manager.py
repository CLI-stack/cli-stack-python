"""
Project: CDC Waiver Manager
Tool context: Spyglass CDC / VC CDC
What it does: Manages CDC waivers with full tracking of justification,
clock domains, signal names, and approval status.
Exports Spyglass-compatible waiver TCL commands.

Usage:
    python 22_cdc_waiver_manager.py --action list
    python 22_cdc_waiver_manager.py --action add --rule CDC_CONV_RULE \
           --module uart_ctrl --signal rx_data --src-clk clk_uart --dst-clk clk_core \
           --justification "Bus crossing — gray code encoded upstream" --owner alice
    python 22_cdc_waiver_manager.py --action export-tcl
    python 22_cdc_waiver_manager.py --action validate
"""

import json
import argparse
import os
from datetime import datetime

WAIVER_DB = "cdc_waivers.json"

SAMPLE_WAIVERS = [
    {
        "id":            "CDC-W001",
        "rule":          "CDC_ASYNC_RST",
        "module":        "pll_ctrl",
        "signal":        "pll_rstn",
        "src_clk":       "clk_pll",
        "dst_clk":       "clk_core",
        "justification": "Reset synchronizer instantiated in parent module — IP verified",
        "owner":         "alice",
        "date":          "2024-01-10",
        "approved":      True,
    },
    {
        "id":            "CDC-W002",
        "rule":          "CDC_NO_SYNC",
        "module":        "uart_ctrl",
        "signal":        "rx_data[7:0]",
        "src_clk":       "clk_uart",
        "dst_clk":       "clk_core",
        "justification": "Gray-code encoding applied in uart_rx module before crossing",
        "owner":         "bob",
        "date":          "2024-01-12",
        "approved":      True,
    },
    {
        "id":            "CDC-W003",
        "rule":          "CDC_MUX_SEL",
        "module":        "apb_bridge",
        "signal":        "apb_sel",
        "src_clk":       "clk_core",
        "dst_clk":       "clk_apb",
        "justification": "",   # incomplete
        "owner":         "",
        "date":          "2024-01-14",
        "approved":      False,
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
    return f"CDC-W{(max(nums)+1 if nums else 1):03d}"


def action_list(waivers):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"
    print(f"\n  {'ID':<10} {'RULE':<16} {'MODULE':<14} {'SIGNAL':<20} "
          f"{'SRC CLK':<12} {'DST CLK':<12} {'APPR'}")
    print("  " + "-" * 100)
    for w in waivers:
        appr = f"{GREEN}YES{RST}" if w["approved"] else f"{RED}NO{RST}"
        print(f"  {w['id']:<10} {w['rule']:<16} {w['module']:<14} "
              f"{w.get('signal','*'):<20} {w.get('src_clk','?'):<12} "
              f"{w.get('dst_clk','?'):<12} {appr}")
    print(f"\n  Total: {len(waivers)}  Approved: {sum(1 for w in waivers if w['approved'])}")


def action_add(waivers, rule, module, signal, src_clk, dst_clk, justification, owner):
    w = {
        "id":            next_id(waivers),
        "rule":          rule or "",
        "module":        module or "",
        "signal":        signal or "*",
        "src_clk":       src_clk or "",
        "dst_clk":       dst_clk or "",
        "justification": justification or "",
        "owner":         owner or "",
        "date":          datetime.today().strftime("%Y-%m-%d"),
        "approved":      False,
    }
    waivers.append(w)
    save_db(waivers)
    print(f"Added {w['id']}: {rule} on {module}/{signal} ({src_clk}→{dst_clk})")


def action_validate(waivers):
    issues = []
    for w in waivers:
        if not w.get("justification"):
            issues.append(f"  {w['id']} — missing justification")
        if not w.get("owner"):
            issues.append(f"  {w['id']} — missing owner")
        if not w.get("src_clk") or not w.get("dst_clk"):
            issues.append(f"  {w['id']} — missing src_clk or dst_clk")

    if issues:
        print(f"\nValidation FAILED — {len(issues)} issue(s):")
        for i in issues:
            print(i)
    else:
        print(f"\nValidation PASSED — all {len(waivers)} waivers complete.")


def action_export_tcl(waivers, output):
    """Generate Spyglass CDC waiver TCL."""
    lines = [
        "# CDC Waiver File — Spyglass CDC format",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]
    for w in waivers:
        if not w.get("approved"):
            continue
        lines.append(f"# {w['id']} | {w['owner']} | {w['date']}")
        lines.append(f"# {w['justification']}")
        lines.append(
            f"waive -rule {{{w['rule']}}} -module {{{w['module']}}} "
            f"-signal {{{w['signal']}}} "
            f"-comment {{{w['justification']}}}"
        )
        lines.append("")

    with open(output, "w") as f:
        f.write("\n".join(lines))

    approved = sum(1 for w in waivers if w["approved"])
    print(f"Exported {approved} approved CDC waivers to: {output}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="CDC waiver database manager")
parser.add_argument("--action",        required=True,
                    choices=["list", "add", "validate", "export-tcl"])
parser.add_argument("--rule",          help="CDC rule e.g. CDC_CONV_RULE")
parser.add_argument("--module",        help="Module name")
parser.add_argument("--signal",        help="Signal name")
parser.add_argument("--src-clk",      help="Source clock domain")
parser.add_argument("--dst-clk",      help="Destination clock domain")
parser.add_argument("--justification", help="Justification text")
parser.add_argument("--owner",         help="Owner engineer")
parser.add_argument("--output",        default="cdc_waivers.tcl")
args = parser.parse_args()

waivers = load_db()

if args.action == "list":
    action_list(waivers)
elif args.action == "add":
    action_add(waivers, args.rule, args.module, args.signal,
                getattr(args, "src_clk", None), getattr(args, "dst_clk", None),
                args.justification, args.owner)
elif args.action == "validate":
    action_validate(waivers)
elif args.action == "export-tcl":
    action_export_tcl(waivers, args.output)
