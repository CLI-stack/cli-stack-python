"""
Project: Development Environment Checker
What it does: Verifies that your development environment is correctly set up.
Checks Python version, required packages, system tools, and config files.
Useful for onboarding new team members or debugging environment issues.

Run: python 47_env_checker.py
Run: python 47_env_checker.py --requirements requirements.txt
"""

import sys       # built-in: Python version info
import os
import subprocess
import argparse
import platform
from datetime import datetime


def check_python_version(min_major=3, min_minor=8):
    """
    Check if the current Python version meets the minimum requirement.
    sys.version_info holds: (major, minor, micro, releaselevel, serial)
    e.g. Python 3.9.7 → sys.version_info = (3, 9, 7, 'final', 0)
    """
    version = sys.version_info
    meets   = (version.major > min_major or
               (version.major == min_major and version.minor >= min_minor))
    return {
        "name":    f"Python {min_major}.{min_minor}+",
        "status":  "PASS" if meets else "FAIL",
        "detail":  f"Python {version.major}.{version.minor}.{version.micro} installed",
    }


def check_package(package_name, min_version=None):
    """
    Check if a Python package is installed and optionally check its version.
    importlib.metadata.version() gets the installed version of a package.
    """
    try:
        import importlib.metadata
        installed_version = importlib.metadata.version(package_name)

        if min_version:
            # Simple version comparison (works for most semantic versioning)
            inst_parts = [int(x) for x in installed_version.split(".")[:3] if x.isdigit()]
            min_parts  = [int(x) for x in min_version.split(".")[:3]       if x.isdigit()]

            # Pad shorter list
            while len(inst_parts) < len(min_parts):
                inst_parts.append(0)
            while len(min_parts) < len(inst_parts):
                min_parts.append(0)

            meets_version = inst_parts >= min_parts
        else:
            meets_version = True

        return {
            "name":   f"Package: {package_name}",
            "status": "PASS" if meets_version else "WARN",
            "detail": f"v{installed_version} installed" + (f" (need {min_version}+)" if not meets_version else ""),
        }

    except Exception:
        return {
            "name":   f"Package: {package_name}",
            "status": "FAIL",
            "detail": f"Not installed — run: pip install {package_name}",
        }


def check_command(command, args=["--version"]):
    """
    Check if an external command-line tool is available.
    subprocess.run() runs a shell command — we check its exit code.
    """
    try:
        result = subprocess.run(
            [command] + args,
            capture_output=True, text=True, timeout=5
        )
        version = (result.stdout + result.stderr).split("\n")[0].strip()[:60]
        return {
            "name":   f"Tool: {command}",
            "status": "PASS",
            "detail": version,
        }
    except FileNotFoundError:
        return {
            "name":   f"Tool: {command}",
            "status": "WARN",
            "detail": f"Not found in PATH",
        }
    except Exception as e:
        return {
            "name":   f"Tool: {command}",
            "status": "WARN",
            "detail": str(e)[:60],
        }


def check_env_var(var_name, required=False):
    """Check if an environment variable is set."""
    value = os.environ.get(var_name)
    if value:
        # Mask sensitive values (show only first 4 chars)
        masked = value[:4] + "****" if len(value) > 4 else "****"
        return {
            "name":   f"Env: {var_name}",
            "status": "PASS",
            "detail": f"Set ({masked})",
        }
    else:
        return {
            "name":   f"Env: {var_name}",
            "status": "FAIL" if required else "WARN",
            "detail": "Not set",
        }


def check_file_exists(filepath, description=""):
    """Check if a required file or directory exists."""
    exists = os.path.exists(filepath)
    return {
        "name":   f"File: {filepath}",
        "status": "PASS" if exists else "WARN",
        "detail": ("Found" if exists else "Not found") + (f" — {description}" if description else ""),
    }


def check_disk_space(min_gb=1.0):
    """Check if there's enough free disk space."""
    try:
        stat  = os.statvfs(".")
        free  = stat.f_bavail * stat.f_frsize / 1e9  # free space in GB
        meets = free >= min_gb
        return {
            "name":   f"Disk space (≥ {min_gb}GB free)",
            "status": "PASS" if meets else "WARN",
            "detail": f"{free:.1f} GB free",
        }
    except Exception:
        return {"name": "Disk space", "status": "SKIP", "detail": "Cannot check"}


def print_check_report(results):
    """Display all check results in a formatted report."""
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    GREY  = "\033[90m"
    BOLD  = "\033[1m"
    RST   = "\033[0m"

    STATUS_COLOR = {
        "PASS": GREEN,
        "FAIL": RED,
        "WARN": YEL,
        "SKIP": GREY,
    }

    STATUS_ICON = {
        "PASS": "✓",
        "FAIL": "✗",
        "WARN": "⚠",
        "SKIP": "─",
    }

    print("=" * 65)
    print(f"  {BOLD}DEVELOPMENT ENVIRONMENT CHECKER{RST}")
    print(f"  System: {platform.system()} {platform.release()}")
    print(f"  Date:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    pass_count = fail_count = warn_count = 0

    for r in results:
        status = r["status"]
        color  = STATUS_COLOR.get(status, "")
        icon   = STATUS_ICON.get(status, "?")

        print(f"\n  {color}{icon} {r['name']}{RST}")
        print(f"    {r['detail']}")

        if status == "PASS":   pass_count += 1
        elif status == "FAIL": fail_count += 1
        elif status == "WARN": warn_count += 1

    total = len(results)
    print(f"\n{'='*65}")
    print(f"  Results: {GREEN}{pass_count} PASS{RST}  {RED}{fail_count} FAIL{RST}  {YEL}{warn_count} WARN{RST}")

    if fail_count == 0 and warn_count == 0:
        print(f"  {GREEN}{BOLD}Environment is fully configured! ✓{RST}")
    elif fail_count == 0:
        print(f"  {YEL}Environment is mostly configured (review warnings){RST}")
    else:
        print(f"  {RED}Environment has issues — fix FAIL items before continuing{RST}")
    print("=" * 65)


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Check development environment setup")
parser.add_argument("--requirements", help="requirements.txt file to check")
args = parser.parse_args()

print("=== Environment Checker ===\n")

checks = []

# ── Python version ─────────────────────────────────────────────────────────────
checks.append(check_python_version(3, 7))

# ── Common packages ────────────────────────────────────────────────────────────
common_packages = [
    ("pip", "21.0"),
    ("numpy", "1.20"),
    ("pandas", "1.3"),
    ("requests", "2.25"),
]
for pkg, ver in common_packages:
    checks.append(check_package(pkg, ver))

# ── Requirements.txt packages ──────────────────────────────────────────────────
if args.requirements and os.path.exists(args.requirements):
    print(f"Checking packages from: {args.requirements}\n")
    with open(args.requirements) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Parse "package>=version" format
                parts   = line.replace("==",">=").split(">=")
                pkg     = parts[0].strip()
                min_ver = parts[1].strip() if len(parts) > 1 else None
                checks.append(check_package(pkg, min_ver))

# ── System tools ───────────────────────────────────────────────────────────────
for tool in ["git", "python3", "pip3"]:
    checks.append(check_command(tool))

# ── Disk space ─────────────────────────────────────────────────────────────────
checks.append(check_disk_space(min_gb=1.0))

# ── Common files ───────────────────────────────────────────────────────────────
checks.append(check_file_exists(".gitignore", "prevents accidental commits"))
checks.append(check_file_exists("requirements.txt", "dependency list"))

print_check_report(checks)
