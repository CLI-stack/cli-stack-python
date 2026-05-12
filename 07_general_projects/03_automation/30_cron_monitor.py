"""
Project: Cron Job Monitor
What it does: Monitors scheduled jobs (cron jobs) to ensure they ran
as expected. Records job heartbeats and alerts when a job misses its schedule.

In production systems, cron jobs backup databases, generate reports, send emails, etc.
If they fail silently, data loss or missed operations can occur.

Run: python 30_cron_monitor.py  (interactive demo)
Run: python 30_cron_monitor.py --report
Run: python 30_cron_monitor.py --heartbeat daily_backup
"""

import json
import os
import argparse
from datetime import datetime, timedelta
from collections import defaultdict


MONITOR_FILE = "cron_monitor.json"


def load_monitor():
    """Load monitoring data from disk."""
    if os.path.exists(MONITOR_FILE):
        with open(MONITOR_FILE) as f:
            return json.load(f)
    # Default structure: job definitions and heartbeat history
    return {
        "jobs": [
            {
                "name":           "daily_backup",
                "description":    "Database backup to S3",
                "schedule":       "daily",
                "expected_hour":  2,     # expected to run at 2 AM
                "max_delay_hours":3,     # alert if not seen within 3 hours
                "last_seen":      None,
                "status":         "never_run",
            },
            {
                "name":           "weekly_report",
                "description":    "Send weekly analytics email",
                "schedule":       "weekly",
                "expected_day":   1,     # Monday (0=Sunday, 1=Monday, etc.)
                "max_delay_hours":24,
                "last_seen":      None,
                "status":         "never_run",
            },
            {
                "name":           "hourly_cleanup",
                "description":    "Clean temp files",
                "schedule":       "hourly",
                "max_delay_hours":2,
                "last_seen":      None,
                "status":         "never_run",
            },
        ],
        "heartbeat_history": defaultdict(list)
    }


def save_monitor(data):
    """Convert defaultdict to dict before saving (JSON doesn't support defaultdict)."""
    data["heartbeat_history"] = dict(data["heartbeat_history"])
    with open(MONITOR_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def record_heartbeat(job_name):
    """
    Record that a job ran successfully right now.
    Jobs should call this when they complete to let the monitor know they ran.
    """
    data = load_monitor()

    # Find the job definition
    job = next((j for j in data["jobs"] if j["name"] == job_name), None)

    if not job:
        # Auto-register unknown jobs
        print(f"New job registered: {job_name}")
        data["jobs"].append({
            "name":           job_name,
            "description":    "Auto-registered job",
            "schedule":       "unknown",
            "max_delay_hours":24,
            "last_seen":      None,
            "status":         "ok",
        })
        job = data["jobs"][-1]

    now   = datetime.now().isoformat()  # ISO format: "2024-01-15T14:30:00"
    job["last_seen"] = now
    job["status"]    = "ok"

    # Keep last 10 heartbeats in history
    if job_name not in data["heartbeat_history"]:
        data["heartbeat_history"][job_name] = []

    data["heartbeat_history"][job_name].append(now)
    data["heartbeat_history"][job_name] = data["heartbeat_history"][job_name][-10:]

    save_monitor(data)
    print(f"Heartbeat recorded: {job_name} at {datetime.now().strftime('%H:%M:%S')}")


def check_job_status(job):
    """
    Determine if a job is healthy, late, or missing.
    Returns: "ok", "late", "missing", or "never_run"
    """
    if not job["last_seen"]:
        return "never_run"

    last_seen    = datetime.fromisoformat(job["last_seen"])
    now          = datetime.now()
    hours_since  = (now - last_seen).total_seconds() / 3600  # convert to hours

    max_delay = job.get("max_delay_hours", 24)

    if hours_since <= max_delay:
        return "ok"
    elif hours_since <= max_delay * 2:
        return "late"      # seen recently but overdue
    else:
        return "missing"   # hasn't been seen for too long


def print_report(data):
    """Display the monitoring dashboard."""
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    GREY  = "\033[90m"
    RST   = "\033[0m"

    STATUS_COLOR = {
        "ok":       GREEN,
        "late":     YEL,
        "missing":  RED,
        "never_run":GREY,
    }

    STATUS_ICON = {
        "ok":       "✓",
        "late":     "⚠",
        "missing":  "✗",
        "never_run":"?",
    }

    print(f"\n{'='*65}")
    print(f"  CRON JOB MONITOR — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*65}\n")

    all_ok  = True
    for job in data["jobs"]:
        status    = check_job_status(job)
        color     = STATUS_COLOR.get(status, "")
        icon      = STATUS_ICON.get(status, "?")

        if status in ("missing", "late"):
            all_ok = False

        last_seen_str = "Never" if not job["last_seen"] else \
            datetime.fromisoformat(job["last_seen"]).strftime("%Y-%m-%d %H:%M")

        print(f"  {color}{icon} {job['name']:<20}{RST}")
        print(f"    Description: {job['description']}")
        print(f"    Schedule   : {job['schedule']}")
        print(f"    Last seen  : {last_seen_str}")
        print(f"    Status     : {color}{status.upper()}{RST}")

        # Show recent history
        history = data.get("heartbeat_history", {}).get(job["name"], [])
        if history:
            recent = [datetime.fromisoformat(h).strftime("%m/%d %H:%M") for h in history[-3:]]
            print(f"    History    : {', '.join(recent)}")
        print()

    print(f"  Overall: {'ALL JOBS OK ✓' if all_ok else 'ATTENTION REQUIRED ⚠'}")


def simulate_demo():
    """Create demo data showing various job states."""
    data = load_monitor()
    now  = datetime.now()

    # Simulate: hourly_cleanup ran recently (healthy)
    data["jobs"][2]["last_seen"] = now.isoformat()
    data["jobs"][2]["status"]    = "ok"

    # Simulate: daily_backup ran 4 hours ago (slightly late)
    four_hours_ago = (now - timedelta(hours=4)).isoformat()
    data["jobs"][0]["last_seen"] = four_hours_ago
    data["jobs"][0]["status"]    = "late"

    # weekly_report: never run (left as never_run)
    save_monitor(data)

    return data


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Monitor cron job health")
parser.add_argument("--report",     action="store_true", help="Show monitoring report")
parser.add_argument("--heartbeat",  help="Record a job heartbeat by name")
args = parser.parse_args()

print("=== Cron Job Monitor ===\n")

if args.heartbeat:
    record_heartbeat(args.heartbeat)
elif args.report:
    data = load_monitor()
    print_report(data)
else:
    # Demo mode
    print("Running in demo mode (simulating job statuses)...\n")
    data = simulate_demo()
    print_report(data)

# Clean up demo
if os.path.exists(MONITOR_FILE):
    os.remove(MONITOR_FILE)
