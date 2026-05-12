"""
Project: Process Monitor
What it does: Lists and monitors running processes by name, PID, or CPU usage.
Lets you watch a specific process over time and alert if it's using too many resources.
Similar to Activity Monitor (Mac) or Task Manager (Windows) but in Python.

Install: pip install psutil
Run: python 48_process_monitor.py  (list top processes)
Run: python 48_process_monitor.py --name python  (find Python processes)
Run: python 48_process_monitor.py --top 10  (top 10 by CPU)
"""

import time
import argparse
import os
from datetime import datetime


def get_processes_builtin():
    """
    Get running process info using only built-in modules (Linux only).
    Reads from /proc filesystem which Linux exposes for each running process.
    """
    processes = []

    try:
        # /proc contains a numbered directory for each running process
        for pid_str in os.listdir("/proc"):
            if not pid_str.isdigit():
                continue  # skip non-process entries like /proc/sys

            pid = int(pid_str)
            proc_dir = f"/proc/{pid}"

            try:
                # Read process name from /proc/<pid>/comm
                with open(f"{proc_dir}/comm") as f:
                    name = f.read().strip()

                # Read process status for memory info
                mem_kb = 0
                with open(f"{proc_dir}/status") as f:
                    for line in f:
                        if line.startswith("VmRSS:"):  # RSS = Resident Set Size (physical memory)
                            mem_kb = int(line.split()[1])
                            break

                processes.append({
                    "pid":    pid,
                    "name":   name,
                    "mem_mb": mem_kb / 1024,
                    "cpu":    0.0,   # CPU% requires two readings, simplified to 0 here
                })

            except (PermissionError, FileNotFoundError, ValueError):
                continue  # some processes can't be read without root

    except Exception as e:
        return [], str(e)

    return processes, None


def get_processes_psutil(name_filter=None, top_n=None, sort_by="cpu"):
    """
    Get detailed process information using psutil.
    psutil provides cross-platform, accurate process stats.
    """
    try:
        import psutil

        processes = []

        for proc in psutil.process_iter(["pid", "name", "cpu_percent",
                                          "memory_info", "status", "create_time",
                                          "username"]):
            try:
                info = proc.info

                # Apply name filter if specified
                if name_filter and name_filter.lower() not in info["name"].lower():
                    continue

                # Get memory in MB
                mem_mb = info["memory_info"].rss / 1024 / 1024 if info["memory_info"] else 0

                # Get process start time
                create_dt = datetime.fromtimestamp(info["create_time"])
                running_since = create_dt.strftime("%H:%M:%S")

                processes.append({
                    "pid":    info["pid"],
                    "name":   info["name"][:25],
                    "cpu":    info["cpu_percent"],
                    "mem_mb": mem_mb,
                    "status": info["status"],
                    "user":   (info["username"] or "")[:12],
                    "started":running_since,
                })

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue  # process ended or we don't have permission

        # Sort by CPU or memory
        key_map = {"cpu": "cpu", "memory": "mem_mb", "pid": "pid", "name": "name"}
        sort_key = key_map.get(sort_by, "cpu")
        processes.sort(key=lambda p: p.get(sort_key, 0), reverse=(sort_by in ["cpu","memory"]))

        return (processes[:top_n] if top_n else processes), None

    except ImportError:
        return None, "psutil not installed"


def print_process_table(processes, sort_by="cpu"):
    """Display processes in a formatted table."""
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    CYN   = "\033[36m"
    RST   = "\033[0m"

    if not processes:
        print("  No processes found.")
        return

    print(f"\n  {'PID':>7} {'NAME':<26} {'CPU%':>6} {'MEM(MB)':>9} {'STATUS':<12} {'USER':<12}")
    print("  " + "─" * 80)

    for proc in processes:
        cpu    = proc.get("cpu", 0)
        mem    = proc.get("mem_mb", 0)
        status = proc.get("status", "?")
        user   = proc.get("user", "?")

        # Color-code high CPU usage
        if cpu >= 50:    cpu_color = RED
        elif cpu >= 20:  cpu_color = YEL
        else:            cpu_color = ""

        print(f"  {proc['pid']:>7} {proc['name']:<26} "
              f"{cpu_color}{cpu:>5.1f}%{RST} {mem:>9.1f} {status:<12} {user:<12}")


def watch_process(pid, interval=2):
    """
    Watch a single process and display its resource usage over time.
    Useful for monitoring a long-running process like a server or script.
    """
    try:
        import psutil

        print(f"\nWatching PID {pid}... (Ctrl+C to stop)\n")
        print(f"  {'TIME':<10} {'CPU%':>6} {'MEM(MB)':>9} {'THREADS':>8} {'STATUS'}")
        print("  " + "─" * 50)

        try:
            proc = psutil.Process(pid)

            while True:
                try:
                    cpu    = proc.cpu_percent(interval=interval)
                    mem    = proc.memory_info().rss / 1024 / 1024
                    threads= proc.num_threads()
                    status = proc.status()
                    time_  = datetime.now().strftime("%H:%M:%S")

                    print(f"  {time_:<10} {cpu:>6.1f} {mem:>9.1f} {threads:>8} {status}")

                except psutil.NoSuchProcess:
                    print(f"\n  Process {pid} has ended.")
                    break

        except KeyboardInterrupt:
            print(f"\n\nStopped watching PID {pid}")

    except ImportError:
        print("psutil not installed. Run: pip install psutil")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Monitor system processes")
parser.add_argument("--name",    help="Filter by process name")
parser.add_argument("--top",     type=int, default=15, help="Show top N processes")
parser.add_argument("--sort",    default="cpu", choices=["cpu","memory","pid","name"])
parser.add_argument("--watch",   type=int, help="Watch a specific PID over time")
parser.add_argument("--interval",type=float, default=2.0, help="Watch refresh interval (sec)")
args = parser.parse_args()

print("=== Process Monitor ===\n")
print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if args.watch:
    watch_process(args.watch, args.interval)
else:
    # Try psutil first (more accurate), fall back to /proc
    processes, error = get_processes_psutil(
        name_filter=args.name, top_n=args.top, sort_by=args.sort
    )

    if processes is None:
        # psutil not available — use built-in method (Linux only)
        print(f"  {error} — using built-in /proc reader\n")
        processes, error = get_processes_builtin()

        if error:
            print(f"  Error: {error}")
            processes = []

        # Apply name filter manually for built-in method
        if args.name:
            processes = [p for p in processes if args.name.lower() in p["name"].lower()]

        # Sort by memory (CPU not available in built-in mode)
        processes.sort(key=lambda p: p.get("mem_mb", 0), reverse=True)
        processes = processes[:args.top]

    label = f"by {args.sort}" if not args.name else f"named '{args.name}'"
    print(f"  Showing top {len(processes)} processes ({label}):")
    print_process_table(processes, args.sort)

    # Summary
    if processes:
        total_mem = sum(p.get("mem_mb", 0) for p in processes)
        print(f"\n  Total memory (shown): {total_mem:.1f} MB")
        print(f"  Install psutil for accurate CPU%: pip install psutil")
