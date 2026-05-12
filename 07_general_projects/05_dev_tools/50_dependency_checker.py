"""
Project: Python Dependency Checker
What it does: Analyzes a project's dependencies — checks if packages are
installed, identifies outdated packages, finds unused imports in code,
and generates a clean requirements.txt.

Run: python 50_dependency_checker.py  (check current environment)
Run: python 50_dependency_checker.py --requirements requirements.txt
Run: python 50_dependency_checker.py --scan-dir /path/to/project  (find used imports)
"""

import sys
import os
import re
import subprocess
import argparse
from collections import defaultdict


def get_installed_packages():
    """
    Get all installed packages and their versions using pip.
    Runs 'pip list --format=json' and parses the output.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True, text=True, timeout=30
        )
        import json
        packages = json.loads(result.stdout)
        # Return as dict: {package_name_lower: version}
        return {p["name"].lower(): p["version"] for p in packages}

    except Exception as e:
        print(f"Cannot get package list: {e}")
        return {}


def check_package_outdated():
    """
    Check which installed packages have newer versions available.
    'pip list --outdated' shows packages with available updates.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True, text=True, timeout=60
        )
        import json
        if result.returncode == 0 and result.stdout.strip():
            outdated = json.loads(result.stdout)
            # Return as dict: {package_name_lower: {"current": v, "latest": v}}
            return {
                p["name"].lower(): {
                    "current": p["version"],
                    "latest":  p["latest_version"]
                }
                for p in outdated
            }
    except Exception:
        pass
    return {}


def parse_requirements_file(filepath):
    """
    Parse a requirements.txt file and extract package names and versions.
    Handles common formats:
      package==1.0.0
      package>=1.0.0
      package~=1.0.0
      package  (no version)
      # comment (skipped)
    """
    requirements = []

    with open(filepath) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue  # skip empty lines and comments

            if line.startswith("-r "):
                continue  # skip -r includes (recursive requirements)

            # Split on version specifiers: ==, >=, <=, ~=, !=
            match = re.match(r"([a-zA-Z0-9_.-]+)([>=<!~]+.*)?", line)
            if match:
                name    = match.group(1).strip().lower()
                version = match.group(2).strip() if match.group(2) else "any"
                requirements.append({"name": name, "spec": version, "raw": line})

    return requirements


def scan_imports_in_code(directory):
    """
    Scan Python files to find all imported packages.
    Finds 'import X' and 'from X import Y' statements.
    This helps identify what packages your code actually uses.
    """
    imports = defaultdict(set)   # {package_name: set of files that import it}

    # Walk through all .py files in the directory
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "venv" and d != "__pycache__"]

        for filename in files:
            if not filename.endswith(".py"):
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, directory)

            try:
                with open(filepath, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Find 'import package' statements
                for match in re.finditer(r"^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)", content, re.MULTILINE):
                    pkg = match.group(1).split(".")[0]  # get the top-level package
                    imports[pkg.lower()].add(rel_path)

                # Find 'from package import something' statements
                for match in re.finditer(r"^from\s+([a-zA-Z_][a-zA-Z0-9_.]*).*import", content, re.MULTILINE):
                    pkg = match.group(1).split(".")[0]
                    if not pkg.startswith("."):  # skip relative imports
                        imports[pkg.lower()].add(rel_path)

            except Exception:
                pass

    return imports


def generate_requirements(imports, installed, output_path="requirements_generated.txt"):
    """
    Generate a requirements.txt from found imports and their installed versions.
    Only includes third-party packages (not built-in stdlib modules).
    """
    # Python stdlib modules to exclude (they don't need to be in requirements.txt)
    stdlib_modules = {
        "os", "sys", "re", "json", "csv", "io", "time", "datetime", "math",
        "random", "string", "hashlib", "collections", "itertools", "functools",
        "typing", "pathlib", "subprocess", "threading", "logging", "argparse",
        "unittest", "abc", "contextlib", "copy", "pprint", "struct", "socket",
        "ssl", "urllib", "http", "email", "base64", "zipfile", "gzip", "shutil",
        "tempfile", "glob", "fnmatch", "stat", "platform", "signal", "queue",
        "multiprocessing", "concurrent", "asyncio", "importlib", "inspect",
        "traceback", "warnings", "weakref", "gc", "ctypes", "enum", "dataclasses",
        "configparser", "difflib", "textwrap", "unicodedata", "codecs",
    }

    third_party = {}
    for pkg_name in imports:
        if pkg_name not in stdlib_modules and pkg_name in installed:
            third_party[pkg_name] = installed[pkg_name]

    with open(output_path, "w") as f:
        f.write(f"# Generated requirements.txt\n")
        f.write(f"# Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}\n\n")
        for name, version in sorted(third_party.items()):
            f.write(f"{name}>={version}\n")

    return third_party


def print_report(installed, requirements=None, outdated=None, imports=None, directory="."):
    """Display the complete dependency analysis report."""
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    CYN   = "\033[36m"
    RST   = "\033[0m"

    print("=" * 65)
    print("  DEPENDENCY CHECKER REPORT")
    print("=" * 65)

    # ── Requirements.txt check ─────────────────────────────────────────────────
    if requirements:
        print(f"\n  {CYN}Requirements.txt Analysis:{RST}\n")
        print(f"  {'PACKAGE':<25} {'REQUIRED':>12} {'INSTALLED':>12} {'STATUS'}")
        print("  " + "─" * 65)

        for req in requirements:
            name      = req["name"]
            spec      = req["spec"]
            installed_ver = installed.get(name, "NOT FOUND")

            if installed_ver == "NOT FOUND":
                status = f"{RED}MISSING — run: pip install {name}{RST}"
            else:
                status = f"{GREEN}OK{RST}"

            print(f"  {name:<25} {spec:>12} {installed_ver:>12}  {status}")

    # ── Outdated packages ──────────────────────────────────────────────────────
    if outdated:
        print(f"\n  {YEL}Outdated Packages ({len(outdated)} need update):{RST}\n")
        print(f"  {'PACKAGE':<25} {'INSTALLED':>12} {'LATEST':>12}")
        print("  " + "─" * 55)
        for name, versions in sorted(outdated.items()):
            print(f"  {name:<25} {versions['current']:>12} {versions['latest']:>12}")
        print(f"\n  Update all: pip install --upgrade {' '.join(outdated.keys())}")

    # ── Import scan results ────────────────────────────────────────────────────
    if imports:
        print(f"\n  {CYN}Packages Used in Code ({directory}):{RST}\n")
        stdlib = {"os", "sys", "re", "json", "csv", "io", "time", "datetime",
                  "math", "random", "string", "hashlib", "collections", "itertools",
                  "typing", "pathlib", "subprocess", "threading", "argparse",
                  "sqlite3", "shutil", "zipfile", "gzip", "platform", "struct",
                  "socket", "ssl", "urllib", "http", "base64", "difflib", "textwrap",
                  "unicodedata", "configparser", "importlib", "inspect", "copy"}

        third_party = {k: v for k, v in imports.items() if k not in stdlib}
        std_imports = {k: v for k, v in imports.items() if k in stdlib}

        print(f"  Third-party imports: {len(third_party)}")
        for pkg, files in sorted(third_party.items()):
            in_installed = pkg in installed
            status = f"{GREEN}installed{RST}" if in_installed else f"{RED}NOT installed!{RST}"
            print(f"    {pkg:<25} {status}  (used in {len(files)} file(s))")

        print(f"\n  Standard library imports: {len(std_imports)}")
        print(f"    {', '.join(sorted(std_imports.keys()))}")

    print(f"\n  Environment summary:")
    print(f"    Python version     : {sys.version.split()[0]}")
    print(f"    Total packages     : {len(installed)}")
    if outdated:
        print(f"    Outdated packages  : {YEL}{len(outdated)}{RST}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Check and analyze Python dependencies")
parser.add_argument("--requirements", help="Path to requirements.txt file")
parser.add_argument("--scan-dir",     help="Directory to scan for imports")
parser.add_argument("--check-outdated", action="store_true", help="Check for outdated packages")
parser.add_argument("--generate",     help="Generate requirements.txt to this path")
args = parser.parse_args()

print("=== Python Dependency Checker ===\n")
print("Getting installed packages...")

installed = get_installed_packages()
print(f"Found {len(installed)} installed packages.\n")

requirements = None
if args.requirements and os.path.exists(args.requirements):
    requirements = parse_requirements_file(args.requirements)
    print(f"Loaded {len(requirements)} requirements from {args.requirements}")

outdated = {}
if args.check_outdated:
    print("Checking for outdated packages (this may take a moment)...")
    outdated = check_package_outdated()

imports = None
scan_dir = args.scan_dir or "."
if os.path.isdir(scan_dir):
    print(f"Scanning imports in: {scan_dir}")
    imports = scan_imports_in_code(scan_dir)

if args.generate:
    if imports:
        third_party = generate_requirements(imports, installed, args.generate)
        print(f"\nGenerated requirements.txt: {args.generate}")
        print(f"Included {len(third_party)} third-party packages")

print_report(installed, requirements, outdated, imports, scan_dir)
