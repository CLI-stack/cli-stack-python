"""
Project: Design Change Tracker
Tool context: Cross-flow RTL change management
What it does: Tracks RTL changes between design milestones by diffing
module-level file hashes. Flags which modules changed and what flows
need to be re-run as a result (lint/CDC/DFT/UPF impact analysis).

Usage:
    python 49_design_change_tracker.py --snapshot (capture current state)
    python 49_design_change_tracker.py --diff     (compare to last snapshot)
    python 49_design_change_tracker.py --diff --rtl-dir /path/to/rtl
"""

import os
import hashlib
import json
import argparse
from datetime import datetime

SNAPSHOT_FILE = "rtl_snapshot.json"

# Simulated RTL directory structure
SIMULATED_FILES = {
    "rtl/cpu_core.v":    "abc123",   # different from last snapshot
    "rtl/alu_unit.v":    "def456",   # unchanged
    "rtl/l1_cache.v":    "ghi789",   # different
    "rtl/dma_ctrl.v":    "jkl012",   # unchanged
    "rtl/apb_bridge.v":  "mno345",   # different (new file)
    "rtl/uart_ctrl.v":   "pqr678",   # unchanged
    "rtl/pll_ctrl.v":    "stu901",   # unchanged
}

LAST_SNAPSHOT = {
    "timestamp": "2024-01-10 09:00:00",
    "files": {
        "rtl/cpu_core.v":   "old_abc",   # changed
        "rtl/alu_unit.v":   "def456",    # same
        "rtl/l1_cache.v":   "old_ghi",   # changed
        "rtl/dma_ctrl.v":   "jkl012",    # same
        # apb_bridge not in snapshot = new file
        "rtl/uart_ctrl.v":  "pqr678",    # same
        "rtl/pll_ctrl.v":   "stu901",    # same
        "rtl/spi_ctrl.v":   "vwx234",    # deleted
    }
}

# Which flows need re-run when a module changes
FLOW_DEPENDENCIES = {
    "cpu_core":  ["lint", "dft", "cdc", "timing"],
    "alu_unit":  ["lint", "dft", "timing"],
    "l1_cache":  ["lint", "dft", "cdc", "timing"],
    "dma_ctrl":  ["lint", "dft", "cdc", "upf"],
    "apb_bridge":["lint", "cdc", "upf"],
    "uart_ctrl": ["lint", "cdc", "dft"],
    "pll_ctrl":  ["lint", "cdc", "rdc", "upf"],
}


def hash_file(filepath):
    """Compute MD5 hash of a file."""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def scan_rtl_dir(rtl_dir):
    """Scan RTL directory and hash all .v and .sv files."""
    files = {}
    for root, _, filenames in os.walk(rtl_dir):
        for fname in filenames:
            if fname.endswith((".v", ".sv", ".vhd")):
                fpath = os.path.join(root, fname)
                rel   = os.path.relpath(fpath, rtl_dir)
                files[rel] = hash_file(fpath)
    return files


def compare_snapshots(old, new):
    old_files = old["files"]
    new_files = new

    added   = {f for f in new_files if f not in old_files}
    deleted = {f for f in old_files if f not in new_files}
    changed = {f for f in old_files if f in new_files and old_files[f] != new_files[f]}
    unchanged = {f for f in old_files if f in new_files and old_files[f] == new_files[f]}

    return added, deleted, changed, unchanged


def get_impacted_flows(changed_files):
    """Determine which EDA flows need re-run based on changed modules."""
    impacted = set()
    changed_modules = set()

    for fpath in changed_files:
        # Extract module name from filename
        module = os.path.splitext(os.path.basename(fpath))[0]
        changed_modules.add(module)
        flows = FLOW_DEPENDENCIES.get(module, ["lint"])
        impacted.update(flows)

    return changed_modules, impacted


def print_diff(old_snap, new_files):
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    added, deleted, changed, unchanged = compare_snapshots(old_snap, new_files)
    changed_modules, impacted_flows = get_impacted_flows(changed | added)

    print("=" * 65)
    print("  RTL DESIGN CHANGE TRACKER")
    print(f"  Comparing against snapshot: {old_snap.get('timestamp','?')}")
    print(f"  Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 65)

    print(f"\n  {GREEN}Added files   : {len(added)}{RST}")
    print(f"  {RED}Deleted files : {len(deleted)}{RST}")
    print(f"  {YEL}Changed files : {len(changed)}{RST}")
    print(f"  Unchanged     : {len(unchanged)}")

    if added:
        print(f"\n  {GREEN}New Files:{RST}")
        for f in sorted(added):
            print(f"    + {f}")

    if deleted:
        print(f"\n  {RED}Deleted Files:{RST}")
        for f in sorted(deleted):
            print(f"    - {f}")

    if changed:
        print(f"\n  {YEL}Changed Files:{RST}")
        for f in sorted(changed):
            print(f"    ~ {f}")

    if changed_modules:
        print(f"\n  Changed Modules: {', '.join(sorted(changed_modules))}")

    if impacted_flows:
        print(f"\n  Flows Requiring Re-Run:")
        for flow in sorted(impacted_flows):
            print(f"    {RED}• {flow.upper()}{RST}")

        if not changed:
            print(f"\n  {GREEN}No RTL changes detected — no re-runs needed.{RST}")
        else:
            print(f"\n  Action: Re-run the above flows to verify sign-off is still valid.")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Track RTL design changes between milestones")
parser.add_argument("--snapshot", action="store_true", help="Capture current RTL state")
parser.add_argument("--diff",     action="store_true", help="Compare to last snapshot")
parser.add_argument("--rtl-dir",  default="rtl",       help="RTL directory to scan")
args = parser.parse_args()

if args.snapshot and os.path.isdir(args.rtl_dir):
    new_files = scan_rtl_dir(args.rtl_dir)
    snap = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "files": new_files}
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snap, f, indent=2)
    print(f"Snapshot saved: {len(new_files)} files → {SNAPSHOT_FILE}")

elif args.diff:
    if os.path.isdir(args.rtl_dir) and os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE) as f:
            old_snap = json.load(f)
        new_files = scan_rtl_dir(args.rtl_dir)
    else:
        print("No real RTL dir or snapshot — using simulated data.\n")
        old_snap  = LAST_SNAPSHOT
        new_files = SIMULATED_FILES

    print_diff(old_snap, new_files)

else:
    print("Use --snapshot to capture RTL state, or --diff to compare.")
    print("Running diff with simulated data:\n")
    print_diff(LAST_SNAPSHOT, SIMULATED_FILES)
