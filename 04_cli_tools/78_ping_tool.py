"""
Script: Ping Tool
What it does: Checks if a host is reachable and measures response time.
Similar to the 'ping' command, but written in Python.

Run: python 78_ping_tool.py google.com
Run: python 78_ping_tool.py 8.8.8.8 --count 5
"""

import subprocess
import sys
import platform
import argparse
import time

def ping_host(host, count=4):
    """Ping a host and return statistics."""
    # Different ping command on Windows vs Linux/Mac
    if platform.system().lower() == "windows":
        cmd = ["ping", "-n", str(count), host]
    else:
        cmd = ["ping", "-c", str(count), host]

    results = []
    print(f"\nPinging {host} ({count} times)...")
    print("-" * 50)

    try:
        start = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=count * 5  # timeout based on count
        )
        elapsed = time.time() - start

        output = result.stdout
        is_reachable = result.returncode == 0

        print(output)

        return {
            "host": host,
            "reachable": is_reachable,
            "output": output,
            "return_code": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {"host": host, "reachable": False, "output": "Timeout", "return_code": -1}
    except FileNotFoundError:
        return {"host": host, "reachable": False, "output": "ping command not found", "return_code": -1}

def http_check(host):
    """Alternative: check host reachability via HTTP."""
    try:
        import urllib.request
        import urllib.error

        url = f"http://{host}" if not host.startswith("http") else host
        start = time.time()
        urllib.request.urlopen(url, timeout=5)
        elapsed = (time.time() - start) * 1000
        return True, elapsed
    except Exception:
        return False, None

# --- Parse args ---
parser = argparse.ArgumentParser(description="Ping a host to check connectivity")
parser.add_argument("host", help="Hostname or IP to ping")
parser.add_argument("--count", "-c", type=int, default=4, help="Number of pings")
args = parser.parse_args()

result = ping_host(args.host, args.count)

print("=" * 50)
if result["reachable"]:
    print(f"  RESULT: {args.host} is REACHABLE ✓")
else:
    print(f"  RESULT: {args.host} is UNREACHABLE ✗")

# Also try HTTP check as backup
reachable, ms = http_check(args.host)
if reachable:
    print(f"  HTTP:   Reachable via HTTP ({ms:.0f}ms)")
