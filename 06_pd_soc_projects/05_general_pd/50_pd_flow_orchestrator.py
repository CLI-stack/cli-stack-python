"""
Project: PD Flow Orchestrator
Tool context: Cross-flow automation (Spyglass / TetraMAX / VC CDC / PA Compiler)
What it does: Orchestrates the physical design sign-off flow.
Defines the order of tool runs, tracks completion status, manages dependencies
between flows (e.g., CDC must run after RTL lint clean), and generates a
run script for the EDA cluster.

Usage:
    python 50_pd_flow_orchestrator.py --status
    python 50_pd_flow_orchestrator.py --generate-script --output run_pd.sh
    python 50_pd_flow_orchestrator.py --update --flow lint --status done
"""

import json
import argparse
import os
from datetime import datetime

FLOW_DB = "pd_flow_status.json"

# Flow definitions: id, name, dependencies, tool, script, status
FLOWS = [
    {
        "id":           "rtl_check",
        "name":         "RTL Compilation Check",
        "depends_on":   [],
        "tool":         "Synopsys VCS",
        "cmd":          "vcs -f rtl_filelist.f -sverilog -full64",
        "status":       "done",
        "owner":        "alice",
        "duration_est": "30m",
    },
    {
        "id":           "lint",
        "name":         "SpyGlass Lint",
        "depends_on":   ["rtl_check"],
        "tool":         "SpyGlass Lint",
        "cmd":          "spyglass -project lint/soc_top.prj -goal lint/lint_rtl",
        "status":       "done",
        "owner":        "alice",
        "duration_est": "2h",
    },
    {
        "id":           "cdc",
        "name":         "SpyGlass CDC",
        "depends_on":   ["rtl_check"],
        "tool":         "SpyGlass CDC",
        "cmd":          "spyglass -project cdc/soc_top.prj -goal cdc/clock_domain_crossing",
        "status":       "in_progress",
        "owner":        "charlie",
        "duration_est": "3h",
    },
    {
        "id":           "rdc",
        "name":         "SpyGlass RDC",
        "depends_on":   ["rtl_check"],
        "tool":         "SpyGlass RDC",
        "cmd":          "spyglass -project rdc/soc_top.prj -goal rdc/reset_domain_crossing",
        "status":       "in_progress",
        "owner":        "charlie",
        "duration_est": "2h",
    },
    {
        "id":           "synthesis",
        "name":         "Synthesis (DC/Genus)",
        "depends_on":   ["lint"],
        "tool":         "Synopsys DC",
        "cmd":          "dc_shell -f scripts/syn.tcl | tee logs/syn.log",
        "status":       "pending",
        "owner":        "diana",
        "duration_est": "6h",
    },
    {
        "id":           "upf_pa",
        "name":         "PA Compiler (UPF Check)",
        "depends_on":   ["synthesis"],
        "tool":         "Synopsys PA Compiler",
        "cmd":          "pa_compiler -f scripts/pa_run.tcl | tee logs/pa.log",
        "status":       "pending",
        "owner":        "diana",
        "duration_est": "2h",
    },
    {
        "id":           "dft_insert",
        "name":         "Scan Insertion (DFTMAX)",
        "depends_on":   ["synthesis"],
        "tool":         "Synopsys DFTMAX",
        "cmd":          "dftmax -f scripts/dft_insert.tcl | tee logs/dft_insert.log",
        "status":       "pending",
        "owner":        "bob",
        "duration_est": "3h",
    },
    {
        "id":           "atpg",
        "name":         "ATPG Pattern Generation",
        "depends_on":   ["dft_insert"],
        "tool":         "Synopsys TetraMAX",
        "cmd":          "tmax -f scripts/atpg.tcl | tee logs/atpg.log",
        "status":       "pending",
        "owner":        "bob",
        "duration_est": "4h",
    },
    {
        "id":           "pnr",
        "name":         "Place and Route",
        "depends_on":   ["upf_pa", "dft_insert"],
        "tool":         "Synopsys ICC2",
        "cmd":          "icc2_shell -f scripts/pnr.tcl | tee logs/pnr.log",
        "status":       "pending",
        "owner":        "frank",
        "duration_est": "12h",
    },
    {
        "id":           "sta",
        "name":         "Static Timing Analysis",
        "depends_on":   ["pnr"],
        "tool":         "Synopsys PrimeTime",
        "cmd":          "pt_shell -f scripts/sta.tcl | tee logs/sta.log",
        "status":       "pending",
        "owner":        "eve",
        "duration_est": "4h",
    },
    {
        "id":           "drc_lvs",
        "name":         "DRC + LVS",
        "depends_on":   ["pnr"],
        "tool":         "Mentor Calibre",
        "cmd":          "calibre -drc -hier scripts/calibre_drc.rules | tee logs/drc.log",
        "status":       "pending",
        "owner":        "frank",
        "duration_est": "3h",
    },
]

STATUS_ICON = {
    "done":        "\033[92m✓\033[0m",
    "in_progress": "\033[33m►\033[0m",
    "pending":     "\033[90m○\033[0m",
    "blocked":     "\033[91m✗\033[0m",
}


def load_flows():
    if os.path.exists(FLOW_DB):
        with open(FLOW_DB) as f:
            db = json.load(f)
        # Merge saved status into FLOWS
        status_map = {e["id"]: e["status"] for e in db}
        for flow in FLOWS:
            if flow["id"] in status_map:
                flow["status"] = status_map[flow["id"]]
    return FLOWS


def save_flows(flows):
    with open(FLOW_DB, "w") as f:
        json.dump([{"id": fl["id"], "status": fl["status"]} for fl in flows], f, indent=2)


def get_ready_flows(flows):
    """Flows whose dependencies are all done."""
    done_ids = {fl["id"] for fl in flows if fl["status"] == "done"}
    return [fl for fl in flows
            if fl["status"] == "pending"
            and all(dep in done_ids for dep in fl["depends_on"])]


def print_status(flows):
    done  = sum(1 for fl in flows if fl["status"] == "done")
    total = len(flows)
    print("=" * 70)
    print(f"  PD FLOW STATUS — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Progress: {done}/{total} flows complete ({done/total*100:.0f}%)")
    print("=" * 70)

    print(f"\n  {'ID':<15} {'FLOW NAME':<30} {'TOOL':<20} {'OWNER':<10} {'STATUS'}")
    print("  " + "-" * 85)

    for fl in flows:
        icon = STATUS_ICON.get(fl["status"], "?")
        print(f"  {fl['id']:<15} {fl['name']:<30} {fl['tool']:<20} {fl['owner']:<10} {icon} {fl['status'].upper()}")

    ready = get_ready_flows(flows)
    if ready:
        print(f"\n  \033[93mReady to run (dependencies satisfied):\033[0m")
        for fl in ready:
            print(f"    ► {fl['id']}: {fl['name']}")


def generate_script(flows, output):
    """Generate a shell script that runs flows in dependency order."""
    lines = [
        "#!/bin/bash",
        f"# PD Flow Run Script — Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "set -e",
        "",
    ]
    # Topological sort (simple: just order by dependencies)
    ordered = []
    remaining = list(flows)
    done_ids  = set()

    while remaining:
        progress = False
        for fl in list(remaining):
            if all(dep in done_ids for dep in fl["depends_on"]):
                if fl["status"] != "done":
                    ordered.append(fl)
                done_ids.add(fl["id"])
                remaining.remove(fl)
                progress = True
        if not progress:
            break

    for fl in ordered:
        lines.append(f"# ── {fl['name']} ({fl['tool']}) ──")
        lines.append(f'echo "[$(date)] Starting: {fl["name"]}"')
        lines.append(fl["cmd"])
        lines.append(f'echo "[$(date)] Done: {fl["name"]}"')
        lines.append("")

    with open(output, "w") as f:
        f.write("\n".join(lines))
    os.chmod(output, 0o755)
    print(f"Run script generated: {output}  ({len(ordered)} flows)")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="PD flow orchestrator")
parser.add_argument("--status",          action="store_true", help="Show flow status")
parser.add_argument("--generate-script", action="store_true", help="Generate run shell script")
parser.add_argument("--output",          default="run_pd.sh")
parser.add_argument("--update",          action="store_true", help="Update a flow status")
parser.add_argument("--flow",            help="Flow ID to update")
parser.add_argument("--set-status",      dest="new_status",
                    choices=["done","in_progress","pending","blocked"])
args = parser.parse_args()

flows = load_flows()

if args.update:
    if not args.flow or not args.new_status:
        parser.error("--update requires --flow and --set-status")
    for fl in flows:
        if fl["id"] == args.flow:
            fl["status"] = args.new_status
            save_flows(flows)
            print(f"Updated {args.flow} → {args.new_status}")
            break

elif args.generate_script:
    generate_script(flows, args.output)

else:
    print_status(flows)
