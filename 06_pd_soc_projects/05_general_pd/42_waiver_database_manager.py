"""
Project: Central Waiver Database Manager (All Flows)
Tool context: Cross-flow (Lint / DFT / CDC / RDC / UPF)
What it does: Manages a single unified waiver database covering all flows.
Each waiver has a flow tag (lint/dft/cdc/rdc/upf), preventing duplicate
waivers and providing a single source of truth for sign-off packages.

Usage:
    python 42_waiver_database_manager.py --action list
    python 42_waiver_database_manager.py --action list --flow cdc
    python 42_waiver_database_manager.py --action summary
    python 42_waiver_database_manager.py --action add --flow lint --rule W_NET_NO_LOAD \
           --module cpu_core --justification "Debug net" --owner alice
    python 42_waiver_database_manager.py --action validate
    python 42_waiver_database_manager.py --action export --flow all --output all_waivers.csv
"""

import json
import csv
import argparse
import os
from datetime import datetime
from collections import Counter

WAIVER_DB = "central_waivers.json"

SAMPLE_WAIVERS = [
    {"id":"L-001","flow":"lint","rule":"W_NET_NO_LOAD","module":"cpu_core","signal":"int_bus",
     "justification":"Debug net tied off in synthesis","owner":"alice","date":"2024-01-10","approved":True},
    {"id":"D-001","flow":"dft","rule":"DFT_C01","module":"cpu_core","signal":"dbg_en",
     "justification":"Debug-only, controlled by JTAG","owner":"alice","date":"2024-01-11","approved":True},
    {"id":"C-001","flow":"cdc","rule":"CDC_ASYNC_RST","module":"pll_ctrl","signal":"pll_rstn",
     "justification":"Reset synchronizer in parent","owner":"bob","date":"2024-01-12","approved":True},
    {"id":"R-001","flow":"rdc","rule":"RDC_ASSERT_DEASSERT","module":"pll_ctrl","signal":"pll_rstn",
     "justification":"Reset sequenced by power controller","owner":"bob","date":"2024-01-12","approved":True},
    {"id":"U-001","flow":"upf","rule":"PA-ISO-001","module":"cpu_core","signal":"cpu_req",
     "justification":"","owner":"","date":"2024-01-14","approved":False},  # incomplete
]

FLOW_PREFIXES = {"lint":"L","dft":"D","cdc":"C","rdc":"R","upf":"U"}


def load_db():
    if os.path.exists(WAIVER_DB):
        with open(WAIVER_DB) as f:
            return json.load(f)
    return SAMPLE_WAIVERS


def save_db(waivers):
    with open(WAIVER_DB, "w") as f:
        json.dump(waivers, f, indent=2)


def next_id(waivers, flow):
    prefix = FLOW_PREFIXES.get(flow, "W")
    nums   = [int(w["id"].split("-")[1]) for w in waivers
              if w["id"].startswith(prefix + "-")]
    return f"{prefix}-{(max(nums)+1 if nums else 1):03d}"


def action_list(waivers, flow_filter=None):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    filtered = [w for w in waivers if not flow_filter or w["flow"] == flow_filter]
    print(f"\n  {'ID':<8} {'FLOW':<6} {'RULE':<22} {'MODULE':<15} {'OWNER':<8} {'APPROVED'}")
    print("  " + "-" * 75)
    for w in filtered:
        appr = f"{GREEN}YES{RST}" if w["approved"] else f"{RED}NO{RST}"
        print(f"  {w['id']:<8} {w['flow']:<6} {w['rule']:<22} {w['module']:<15} {w['owner']:<8} {appr}")
    print(f"\n  Showing {len(filtered)}/{len(waivers)} waivers")


def action_summary(waivers):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RST   = "\033[0m"

    by_flow = Counter(w["flow"] for w in waivers)
    approved= sum(1 for w in waivers if w["approved"])
    incomplete = sum(1 for w in waivers if not w.get("justification") or not w.get("owner"))

    print("\n  CENTRAL WAIVER DATABASE SUMMARY")
    print("  " + "=" * 50)
    print(f"  Total waivers  : {len(waivers)}")
    print(f"  Approved       : {GREEN}{approved}{RST}  ({approved/len(waivers)*100:.0f}%)")
    print(f"  Incomplete     : {RED if incomplete else GREEN}{incomplete}{RST}")
    print(f"\n  By Flow:")
    for flow in ["lint","dft","cdc","rdc","upf"]:
        cnt = by_flow.get(flow, 0)
        print(f"    {flow.upper():<8} {cnt}")


def action_add(waivers, flow, rule, module, signal, justification, owner):
    w = {
        "id":            next_id(waivers, flow),
        "flow":          flow,
        "rule":          rule or "",
        "module":        module or "",
        "signal":        signal or "",
        "justification": justification or "",
        "owner":         owner or "",
        "date":          datetime.today().strftime("%Y-%m-%d"),
        "approved":      False,
    }
    waivers.append(w)
    save_db(waivers)
    print(f"Added {w['id']} [{flow.upper()}]: {rule} on {module}")


def action_validate(waivers):
    issues = []
    for w in waivers:
        if not w.get("justification"):
            issues.append(f"  {w['id']} ({w['flow'].upper()}) — missing justification")
        if not w.get("owner"):
            issues.append(f"  {w['id']} ({w['flow'].upper()}) — missing owner")
        if not w.get("approved"):
            issues.append(f"  {w['id']} ({w['flow'].upper()}) — not approved")

    if issues:
        print(f"\nValidation FAILED — {len(issues)} issue(s):")
        for i in issues:
            print(i)
    else:
        print(f"\nValidation PASSED — all {len(waivers)} waivers are complete and approved.")


def action_export(waivers, flow_filter, output):
    filtered = [w for w in waivers if flow_filter == "all" or w["flow"] == flow_filter]
    fields   = ["id","flow","rule","module","signal","justification","owner","date","approved"]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(filtered)
    print(f"Exported {len(filtered)} waivers to {output}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Central waiver database for all flows")
parser.add_argument("--action",        required=True,
                    choices=["list","add","summary","validate","export"])
parser.add_argument("--flow",          help="Flow: lint/dft/cdc/rdc/upf/all", default="all")
parser.add_argument("--rule",          help="Rule name")
parser.add_argument("--module",        help="Module name")
parser.add_argument("--signal",        help="Signal name")
parser.add_argument("--justification", help="Justification text")
parser.add_argument("--owner",         help="Owner engineer")
parser.add_argument("--output",        default="all_waivers.csv")
args = parser.parse_args()

waivers = load_db()

if args.action == "list":
    action_list(waivers, flow_filter=None if args.flow == "all" else args.flow)
elif args.action == "summary":
    action_summary(waivers)
elif args.action == "add":
    if not args.flow or args.flow == "all":
        parser.error("--flow must specify a single flow (lint/dft/cdc/rdc/upf)")
    action_add(waivers, args.flow, args.rule, args.module,
                args.signal, args.justification, args.owner)
elif args.action == "validate":
    action_validate(waivers)
elif args.action == "export":
    action_export(waivers, args.flow, args.output)
