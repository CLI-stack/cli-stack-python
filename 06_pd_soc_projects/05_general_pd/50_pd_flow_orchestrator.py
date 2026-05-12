"""
Project: PD Flow Orchestrator
Tool context: Cross-flow automation (Spyglass / TetraMAX / VC CDC / PA Compiler)

What it does: Manages the sequence of EDA tool runs for chip tapeout sign-off.
Real chip design requires many tools to run in a specific order — you can't run
Static Timing Analysis (STA) before Place-and-Route (PNR) is complete, for example.
This script tracks which flows are done, which are ready, and which are waiting.

Key concept — Dependency graph:
  rtl_check → lint → synthesis → upf_pa  ─┐
                   └→ cdc               └→ pnr → sta
                   └→ rdc                      └→ drc_lvs
                             └→ dft_insert ─┘
                                        └→ atpg

Usage:
    python 50_pd_flow_orchestrator.py --status
    python 50_pd_flow_orchestrator.py --generate-script --output run_pd.sh
    python 50_pd_flow_orchestrator.py --update --flow lint --set-status done
"""

import json
import argparse
import os
from datetime import datetime

# File that stores the current status of each flow between script runs
FLOW_DB = "pd_flow_status.json"

# ── Flow definitions ──────────────────────────────────────────────────────────
# Each flow is a dict with:
#   id          — short name used for dependency references
#   name        — human-readable display name
#   depends_on  — list of flow IDs that must be 'done' before this can start
#   tool        — EDA tool that runs this flow
#   cmd         — the actual shell command to run
#   status      — current state: done / in_progress / pending / blocked
#   owner       — engineer responsible for this flow
#   duration_est — estimated wall-clock run time on the compute cluster
FLOWS = [
    {
        "id":           "rtl_check",
        "name":         "RTL Compilation Check",
        "depends_on":   [],            # no dependencies — this runs first
        "tool":         "Synopsys VCS",
        "cmd":          "vcs -f rtl_filelist.f -sverilog -full64",
        "status":       "done",
        "owner":        "alice",
        "duration_est": "30m",
    },
    {
        "id":           "lint",
        "name":         "SpyGlass Lint",
        "depends_on":   ["rtl_check"],  # RTL must compile cleanly first
        "tool":         "SpyGlass Lint",
        "cmd":          "spyglass -project lint/soc_top.prj -goal lint/lint_rtl",
        "status":       "done",
        "owner":        "alice",
        "duration_est": "2h",
    },
    {
        "id":           "cdc",
        "name":         "SpyGlass CDC",
        "depends_on":   ["rtl_check"],  # can run in parallel with lint
        "tool":         "SpyGlass CDC",
        "cmd":          "spyglass -project cdc/soc_top.prj -goal cdc/clock_domain_crossing",
        "status":       "in_progress",
        "owner":        "charlie",
        "duration_est": "3h",
    },
    {
        "id":           "rdc",
        "name":         "SpyGlass RDC",
        "depends_on":   ["rtl_check"],  # can run in parallel with lint and CDC
        "tool":         "SpyGlass RDC",
        "cmd":          "spyglass -project rdc/soc_top.prj -goal rdc/reset_domain_crossing",
        "status":       "in_progress",
        "owner":        "charlie",
        "duration_est": "2h",
    },
    {
        "id":           "synthesis",
        "name":         "Synthesis (DC/Genus)",
        "depends_on":   ["lint"],       # lint must be clean before synthesis
        "tool":         "Synopsys DC",
        "cmd":          "dc_shell -f scripts/syn.tcl | tee logs/syn.log",
        "status":       "pending",
        "owner":        "diana",
        "duration_est": "6h",
    },
    {
        "id":           "upf_pa",
        "name":         "PA Compiler (UPF Check)",
        "depends_on":   ["synthesis"],  # needs the synthesized netlist
        "tool":         "Synopsys PA Compiler",
        "cmd":          "pa_compiler -f scripts/pa_run.tcl | tee logs/pa.log",
        "status":       "pending",
        "owner":        "diana",
        "duration_est": "2h",
    },
    {
        "id":           "dft_insert",
        "name":         "Scan Insertion (DFTMAX)",
        "depends_on":   ["synthesis"],  # scan cells inserted into synthesized netlist
        "tool":         "Synopsys DFTMAX",
        "cmd":          "dftmax -f scripts/dft_insert.tcl | tee logs/dft_insert.log",
        "status":       "pending",
        "owner":        "bob",
        "duration_est": "3h",
    },
    {
        "id":           "atpg",
        "name":         "ATPG Pattern Generation",
        "depends_on":   ["dft_insert"],  # needs scan chains inserted first
        "tool":         "Synopsys TetraMAX",
        "cmd":          "tmax -f scripts/atpg.tcl | tee logs/atpg.log",
        "status":       "pending",
        "owner":        "bob",
        "duration_est": "4h",
    },
    {
        "id":           "pnr",
        "name":         "Place and Route",
        "depends_on":   ["upf_pa", "dft_insert"],  # needs power intent + scan netlist
        "tool":         "Synopsys ICC2",
        "cmd":          "icc2_shell -f scripts/pnr.tcl | tee logs/pnr.log",
        "status":       "pending",
        "owner":        "frank",
        "duration_est": "12h",
    },
    {
        "id":           "sta",
        "name":         "Static Timing Analysis",
        "depends_on":   ["pnr"],        # timing analysis on the final placed & routed netlist
        "tool":         "Synopsys PrimeTime",
        "cmd":          "pt_shell -f scripts/sta.tcl | tee logs/sta.log",
        "status":       "pending",
        "owner":        "eve",
        "duration_est": "4h",
    },
    {
        "id":           "drc_lvs",
        "name":         "DRC + LVS",
        "depends_on":   ["pnr"],        # physical verification on the final layout
        "tool":         "Mentor Calibre",
        "cmd":          "calibre -drc -hier scripts/calibre_drc.rules | tee logs/drc.log",
        "status":       "pending",
        "owner":        "frank",
        "duration_est": "3h",
    },
]

# Terminal color codes for each status (ANSI escape codes)
STATUS_ICON = {
    "done":        "\033[92m✓\033[0m",   # green checkmark
    "in_progress": "\033[33m►\033[0m",   # yellow arrow
    "pending":     "\033[90m○\033[0m",   # grey circle
    "blocked":     "\033[91m✗\033[0m",   # red cross
}


def load_flows():
    """
    Load flow status from disk (if saved), merging it into the FLOWS list.
    This allows the orchestrator to remember which flows finished between runs.
    """
    if os.path.exists(FLOW_DB):
        with open(FLOW_DB) as f:
            db = json.load(f)   # load saved statuses from the JSON file

        # Build a quick lookup dict: {flow_id: status}
        # so we can update each flow in O(1) instead of looping twice
        status_map = {e["id"]: e["status"] for e in db}

        # Override each flow's status with the saved value (if it exists)
        for flow in FLOWS:
            if flow["id"] in status_map:
                flow["status"] = status_map[flow["id"]]

    return FLOWS


def save_flows(flows):
    """
    Persist the current status of all flows to disk.
    Only saves 'id' and 'status' — the rest (tool, cmd, etc.) is in the code.
    """
    # Write a minimal list — just id+status — to keep the file small
    with open(FLOW_DB, "w") as f:
        json.dump([{"id": fl["id"], "status": fl["status"]} for fl in flows], f, indent=2)


def get_ready_flows(flows):
    """
    Returns flows that are 'pending' AND have all their dependencies completed.
    These are the flows that can be started right now.
    """
    # Collect the IDs of all flows that are already done
    done_ids = {fl["id"] for fl in flows if fl["status"] == "done"}

    # A flow is 'ready' if:
    #   1. Its status is 'pending' (not already done or running)
    #   2. ALL of its dependencies appear in done_ids
    return [fl for fl in flows
            if fl["status"] == "pending"
            and all(dep in done_ids for dep in fl["depends_on"])]


def print_status(flows):
    """Print a formatted table of all flows with their current status."""
    # Count how many flows are complete
    done  = sum(1 for fl in flows if fl["status"] == "done")
    total = len(flows)

    print("=" * 70)
    print(f"  PD FLOW STATUS — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Progress: {done}/{total} flows complete ({done/total*100:.0f}%)")
    print("=" * 70)

    # Print a row for each flow
    print(f"\n  {'ID':<15} {'FLOW NAME':<30} {'TOOL':<20} {'OWNER':<10} {'STATUS'}")
    print("  " + "-" * 85)
    for fl in flows:
        icon = STATUS_ICON.get(fl["status"], "?")
        print(f"  {fl['id']:<15} {fl['name']:<30} {fl['tool']:<20} "
              f"{fl['owner']:<10} {icon} {fl['status'].upper()}")

    # Highlight which flows can be started now
    ready = get_ready_flows(flows)
    if ready:
        print(f"\n  \033[93mReady to run (all dependencies satisfied):\033[0m")
        for fl in ready:
            print(f"    ► {fl['id']}: {fl['name']}  (est. {fl['duration_est']})")


def generate_script(flows, output):
    """
    Generate a bash shell script that runs all pending flows in the correct order.
    Uses a topological sort algorithm to ensure dependencies run before dependents.

    Topological sort = ordering nodes in a directed graph so every node
    comes after all the nodes it depends on. Think of it as scheduling tasks
    where some tasks must finish before others can start.
    """
    # Start the bash script with a shebang and safety flag
    lines = [
        "#!/bin/bash",
        f"# PD Flow Run Script — Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "set -e",     # 'set -e' means the script stops immediately if any command fails
        "",
    ]

    # ── Topological sort ──────────────────────────────────────────────────────
    ordered   = []        # final sorted list of flows to include in the script
    remaining = list(flows)   # flows we haven't placed yet
    done_ids  = set()         # IDs of flows already placed in 'ordered'

    # Keep looping until all flows are placed or we detect a cycle (no progress)
    while remaining:
        progress = False  # track whether we placed at least one flow this iteration

        # Iterate over a copy of remaining (list(remaining)) because we modify it inside
        for fl in list(remaining):
            # Check if ALL this flow's dependencies are already in done_ids
            if all(dep in done_ids for dep in fl["depends_on"]):
                if fl["status"] != "done":
                    # Only add flows that still need to run (skip already-done ones)
                    ordered.append(fl)

                # Mark this flow as "placed" so dependent flows can proceed
                done_ids.add(fl["id"])
                remaining.remove(fl)  # remove from the "not yet placed" list
                progress = True       # we made progress this iteration

        if not progress:
            # If we went through all remaining flows and couldn't place any,
            # there must be a circular dependency — break to avoid infinite loop
            break

    # ── Write each flow as a section in the shell script ─────────────────────
    for fl in ordered:
        lines.append(f"# ── {fl['name']} ({fl['tool']}) ──")
        lines.append(f'echo "[$(date)] Starting: {fl["name"]}"')
        lines.append(fl["cmd"])   # the actual EDA tool command
        lines.append(f'echo "[$(date)] Done: {fl["name"]}"')
        lines.append("")          # blank line between sections for readability

    # Write the script to disk
    with open(output, "w") as f:
        f.write("\n".join(lines))

    # Make the script executable (like running chmod +x on the command line)
    os.chmod(output, 0o755)
    print(f"Run script generated: {output}  ({len(ordered)} flows to run)")


# ── Main — parse arguments and run the chosen action ─────────────────────────
parser = argparse.ArgumentParser(description="PD flow orchestrator")
parser.add_argument("--status",          action="store_true",
                    help="Show current status of all flows")
parser.add_argument("--generate-script", action="store_true",
                    help="Generate a bash run script in dependency order")
parser.add_argument("--output",          default="run_pd.sh",
                    help="Output file for --generate-script (default: run_pd.sh)")
parser.add_argument("--update",          action="store_true",
                    help="Update the status of a specific flow")
parser.add_argument("--flow",            help="Flow ID to update (e.g. lint, cdc, pnr)")
parser.add_argument("--set-status",      dest="new_status",
                    choices=["done", "in_progress", "pending", "blocked"],
                    help="New status value for --update")
args = parser.parse_args()

# Load current flow statuses (merges disk state with code definitions)
flows = load_flows()

if args.update:
    # Validate that both --flow and --set-status were provided
    if not args.flow or not args.new_status:
        parser.error("--update requires both --flow and --set-status")

    # Find the matching flow and update its status
    for fl in flows:
        if fl["id"] == args.flow:
            fl["status"] = args.new_status
            save_flows(flows)    # persist the change to disk
            print(f"Updated {args.flow} → {args.new_status}")
            break

elif args.generate_script:
    generate_script(flows, args.output)

else:
    # Default action: show status table
    print_status(flows)
