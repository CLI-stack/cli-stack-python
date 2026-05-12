"""
Project: System Resource Monitor
What it does: Displays real-time CPU, memory, disk, and network usage.
Updates every second like the 'top' or 'htop' command on Linux.
Useful for monitoring server health or understanding resource usage.

Install: pip install psutil  (for accurate system metrics)
Run: python 41_system_monitor.py
Run: python 41_system_monitor.py --interval 2 --duration 10
"""

import os
import time
import argparse
from datetime import datetime


def get_system_stats_builtin():
    """Get basic system stats using only built-in Python modules."""
    stats = {}

    # ── CPU: read /proc/stat on Linux ─────────────────────────────────────────
    try:
        with open("/proc/stat") as f:
            cpu_line = f.readline()  # first line = "cpu  ..."

        # Parse: user nice system idle iowait irq softirq steal guest guest_nice
        parts  = cpu_line.split()[1:]
        total  = sum(int(x) for x in parts)
        idle   = int(parts[3])                # idle time
        stats["cpu_total"]  = total
        stats["cpu_idle"]   = idle
    except Exception:
        stats["cpu_total"] = stats["cpu_idle"] = 0

    # ── Memory: read /proc/meminfo on Linux ────────────────────────────────────
    try:
        mem_info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                key, val = line.split(":")
                mem_info[key.strip()] = int(val.split()[0])  # value in kB

        total_kb     = mem_info.get("MemTotal", 0)
        available_kb = mem_info.get("MemAvailable", 0)
        used_kb      = total_kb - available_kb

        stats["mem_total_mb"] = total_kb / 1024
        stats["mem_used_mb"]  = used_kb  / 1024
        stats["mem_pct"]      = used_kb / total_kb * 100 if total_kb else 0
    except Exception:
        stats["mem_total_mb"] = stats["mem_used_mb"] = stats["mem_pct"] = 0

    # ── Disk: os.statvfs() gives disk usage ────────────────────────────────────
    try:
        disk = os.statvfs("/")
        total_bytes = disk.f_blocks * disk.f_frsize  # total blocks × block size
        free_bytes  = disk.f_bfree  * disk.f_frsize
        used_bytes  = total_bytes - free_bytes

        stats["disk_total_gb"] = total_bytes / 1e9
        stats["disk_used_gb"]  = used_bytes  / 1e9
        stats["disk_pct"]      = used_bytes / total_bytes * 100 if total_bytes else 0
    except Exception:
        stats["disk_total_gb"] = stats["disk_used_gb"] = stats["disk_pct"] = 0

    return stats


def calculate_cpu_percent(prev_total, prev_idle, curr_total, curr_idle):
    """
    Calculate CPU usage percentage from two consecutive /proc/stat readings.
    The difference between readings gives us the work done in that interval.

    CPU% = (total_time - idle_time) / total_time × 100
    """
    total_diff = curr_total - prev_total   # total CPU time elapsed
    idle_diff  = curr_idle  - prev_idle    # idle CPU time elapsed

    if total_diff == 0:
        return 0.0

    # Work = total - idle; as percentage of total
    cpu_pct = (total_diff - idle_diff) / total_diff * 100
    return max(0, min(100, cpu_pct))


def make_bar(pct, width=25, warn=70, crit=90):
    """Create a colored progress bar for a percentage value."""
    filled = int(width * pct / 100)
    bar    = "█" * filled + "░" * (width - filled)

    # Color the bar based on usage level
    if pct >= crit:    color = "\033[91m"  # red   = critical
    elif pct >= warn:  color = "\033[93m"  # yellow = warning
    else:              color = "\033[92m"  # green  = OK
    RST = "\033[0m"

    return f"{color}{bar}{RST}"


def display_stats(stats, cpu_pct):
    """Display a formatted system monitor screen."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\033[2J\033[H", end="")  # Clear screen and move cursor to top (ANSI escape)
    print("=" * 55)
    print(f"  SYSTEM MONITOR — {now}")
    print("=" * 55)

    # CPU
    cpu_bar = make_bar(cpu_pct)
    print(f"\n  CPU Usage")
    print(f"  [{cpu_bar}] {cpu_pct:>5.1f}%")

    # Memory
    mem_pct = stats["mem_pct"]
    mem_bar = make_bar(mem_pct)
    print(f"\n  Memory Usage")
    print(f"  [{mem_bar}] {mem_pct:>5.1f}%  "
          f"({stats['mem_used_mb']:.0f} MB / {stats['mem_total_mb']:.0f} MB)")

    # Disk
    disk_pct = stats["disk_pct"]
    disk_bar = make_bar(disk_pct, warn=80, crit=90)
    print(f"\n  Disk Usage (/)")
    print(f"  [{disk_bar}] {disk_pct:>5.1f}%  "
          f"({stats['disk_used_gb']:.1f} GB / {stats['disk_total_gb']:.1f} GB)")

    # Try psutil for additional stats
    try:
        import psutil

        # Per-CPU usage
        per_cpu = psutil.cpu_percent(percpu=True)
        if len(per_cpu) > 1:
            print(f"\n  Per-CPU ({len(per_cpu)} cores):")
            for i, pct in enumerate(per_cpu):
                bar = make_bar(pct, width=15)
                print(f"    Core {i}: [{bar}] {pct:.0f}%")

        # Network I/O
        net = psutil.net_io_counters()
        print(f"\n  Network:")
        print(f"    Sent    : {net.bytes_sent / 1e6:.1f} MB")
        print(f"    Received: {net.bytes_recv / 1e6:.1f} MB")

        # Top processes by CPU
        procs = [(p.info["pid"], p.info["name"], p.info["cpu_percent"])
                 for p in psutil.process_iter(["pid", "name", "cpu_percent"])]
        top5  = sorted(procs, key=lambda x: x[2], reverse=True)[:5]

        print(f"\n  Top Processes (by CPU):")
        for pid, name, cpu in top5:
            if cpu > 0:
                print(f"    PID {pid:>6}  {name:<25} {cpu:.1f}%")

    except ImportError:
        print("\n  (Install psutil for more details: pip install psutil)")

    print(f"\n  Press Ctrl+C to exit")


def monitor(interval, duration):
    """Run the monitor loop."""
    # Get initial reading (needed to compute CPU delta)
    first_stats = get_system_stats_builtin()
    prev_total  = first_stats["cpu_total"]
    prev_idle   = first_stats["cpu_idle"]

    elapsed  = 0
    try:
        while duration is None or elapsed < duration:
            time.sleep(interval)
            elapsed += interval

            curr_stats = get_system_stats_builtin()
            cpu_pct    = calculate_cpu_percent(
                prev_total, prev_idle,
                curr_stats["cpu_total"], curr_stats["cpu_idle"]
            )

            display_stats(curr_stats, cpu_pct)

            prev_total = curr_stats["cpu_total"]
            prev_idle  = curr_stats["cpu_idle"]

    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Real-time system resource monitor")
parser.add_argument("--interval", type=float, default=1.0,  help="Update interval (seconds)")
parser.add_argument("--duration", type=float, default=5,    help="Run for N seconds (default: 5)")
args = parser.parse_args()

print("=== System Monitor ===\n")
print(f"Monitoring for {args.duration}s, updating every {args.interval}s...")
monitor(args.interval, args.duration)
