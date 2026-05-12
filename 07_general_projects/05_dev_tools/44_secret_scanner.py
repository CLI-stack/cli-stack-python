"""
Project: Secret Scanner (Hardcoded Credential Detector)
What it does: Scans source code files for accidentally hardcoded secrets —
API keys, passwords, tokens, and connection strings.
Developers sometimes accidentally commit secrets to git, creating security risks.
This tool catches them before commit or in CI/CD pipelines.

Run: python 44_secret_scanner.py  (scans current directory)
Run: python 44_secret_scanner.py --dir /path/to/project --severity high
"""

import os
import re
import argparse
from pathlib import Path


# ── Secret patterns ────────────────────────────────────────────────────────────
# Each pattern: (name, regex, severity, example)
SECRET_PATTERNS = [
    {
        "name":     "AWS Access Key",
        "pattern":  r"AKIA[0-9A-Z]{16}",
        "severity": "HIGH",
        "example":  "AKIAIOSFODNN7EXAMPLE",
    },
    {
        "name":     "AWS Secret Key",
        "pattern":  r"(?i)aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]",
        "severity": "HIGH",
        "example":  "aws_secret = 'wJalrXUtnFEMI...'",
    },
    {
        "name":     "Generic API Key (long hex)",
        "pattern":  r"(?i)(api[_-]?key|apikey).{0,20}['\"][0-9a-f]{32,}['\"]",
        "severity": "HIGH",
        "example":  "api_key = 'abc123def456...'",
    },
    {
        "name":     "Hardcoded Password",
        "pattern":  r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{8,}['\"]",
        "severity": "HIGH",
        "example":  "password = 'my_secret_pass'",
    },
    {
        "name":     "Generic Token",
        "pattern":  r"(?i)(token|auth_token|access_token)\s*=\s*['\"][^'\"]{20,}['\"]",
        "severity": "MEDIUM",
        "example":  "token = 'eyJhbGciOiJI...'",
    },
    {
        "name":     "Database Connection String",
        "pattern":  r"(?i)(mysql|postgres|mongodb|sqlite)://[^\s'\"]+:[^\s'\"@]+@",
        "severity": "HIGH",
        "example":  "postgres://user:password@localhost/db",
    },
    {
        "name":     "Private Key Header",
        "pattern":  r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----",
        "severity": "CRITICAL",
        "example":  "-----BEGIN RSA PRIVATE KEY-----",
    },
    {
        "name":     "GitHub Token",
        "pattern":  r"ghp_[0-9a-zA-Z]{36}",
        "severity": "HIGH",
        "example":  "ghp_abc123...",
    },
    {
        "name":     "Slack Token",
        "pattern":  r"xox[baprs]-[0-9a-zA-Z-]{10,}",
        "severity": "HIGH",
        "example":  "xoxb-12345-abcde...",
    },
    {
        "name":     "Email + Password Pattern",
        "pattern":  r"(?i)(email|username)\s*=\s*['\"][^'\"]+['\"].*\n.*password\s*=\s*['\"][^'\"]+['\"]",
        "severity": "MEDIUM",
        "example":  "email = 'user@x.com'\npassword = 'pass'",
    },
    {
        "name":     "Base64 Secret",
        "pattern":  r"(?i)(secret|key)\s*=\s*['\"][A-Za-z0-9+/]{40,}={0,2}['\"]",
        "severity": "MEDIUM",
        "example":  "secret = 'SGVsbG8gV29ybGQ...'",
    },
]

# Files and directories to skip
SKIP_DIRS  = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
SKIP_FILES = {".env.example", ".env.sample", "README.md"}

# Binary file extensions to skip
SKIP_EXTS  = {".png", ".jpg", ".gif", ".pdf", ".zip", ".gz", ".exe", ".bin", ".lock"}

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def should_skip(path):
    """Return True if this file/directory should be excluded from scanning."""
    name = os.path.basename(path)
    ext  = os.path.splitext(name)[1].lower()

    return (name in SKIP_DIRS
            or name in SKIP_FILES
            or name.startswith(".")
            or ext in SKIP_EXTS)


def scan_file(filepath, patterns, severity_filter=None):
    """
    Scan a single file for secret patterns.
    Returns a list of findings: (line_number, pattern_name, severity, matched_text)
    """
    findings = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, start=1):
                for pat in patterns:
                    # Apply severity filter if specified
                    if severity_filter and pat["severity"] != severity_filter:
                        continue

                    # Search for the pattern in this line
                    match = re.search(pat["pattern"], line)
                    if match:
                        # Redact the actual secret in the output
                        matched = match.group()
                        if len(matched) > 20:
                            # Show first 10 and last 4 chars, mask the middle
                            redacted = matched[:10] + "..." + matched[-4:]
                        else:
                            redacted = matched[:6] + "****"

                        findings.append({
                            "line":     line_num,
                            "pattern":  pat["name"],
                            "severity": pat["severity"],
                            "matched":  redacted,
                            "line_text":line.strip()[:100],
                        })
    except (PermissionError, OSError):
        pass

    return findings


def scan_directory(directory, severity_filter=None):
    """Recursively scan all files in a directory."""
    all_findings = []
    scanned      = 0
    skipped      = 0

    for root, dirs, files in os.walk(directory):
        # Skip unwanted directories (in-place modification stops os.walk from entering them)
        dirs[:] = [d for d in dirs if not should_skip(os.path.join(root, d))]

        for filename in files:
            filepath = os.path.join(root, filename)

            if should_skip(filepath):
                skipped += 1
                continue

            findings = scan_file(filepath, SECRET_PATTERNS, severity_filter)
            scanned += 1

            for finding in findings:
                finding["file"] = os.path.relpath(filepath, directory)
                all_findings.append(finding)

    return all_findings, scanned, skipped


def print_scan_report(findings, scanned, skipped, directory):
    """Display scan results."""
    CRIT  = "\033[91m\033[1m"  # bright red bold
    RED   = "\033[91m"
    YEL   = "\033[33m"
    GREEN = "\033[92m"
    RST   = "\033[0m"

    SEV_COLOR = {"CRITICAL": CRIT, "HIGH": RED, "MEDIUM": YEL, "LOW": ""}

    print("=" * 65)
    print(f"  SECRET SCANNER REPORT")
    print(f"  Directory: {os.path.abspath(directory)}")
    print("=" * 65)
    print(f"\n  Files scanned : {scanned}")
    print(f"  Files skipped : {skipped}")
    print(f"  Findings      : {len(findings)}")

    if not findings:
        print(f"\n  {GREEN}✓ No secrets detected! Clean scan.{RST}")
        return

    # Sort by severity
    sorted_findings = sorted(findings, key=lambda x: SEVERITY_ORDER.get(x["severity"], 9))

    print(f"\n  {'SEVERITY':<10} {'FILE':<35} {'LINE':>5} {'PATTERN'}")
    print("  " + "─" * 70)

    for f in sorted_findings:
        color = SEV_COLOR.get(f["severity"], "")
        print(f"  {color}{f['severity']:<10}{RST} {f['file']:<35} "
              f"{f['line']:>5}  {f['pattern']}")
        print(f"           Matched: {f['matched']}")

    # Summary by severity
    from collections import Counter
    sev_counts = Counter(f["severity"] for f in findings)

    print(f"\n  By Severity:")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = sev_counts.get(sev, 0)
        if count:
            color = SEV_COLOR.get(sev, "")
            print(f"    {color}{sev:<10}{RST} {count}")

    print(f"\n  {RED}Action: Remove all secrets from code! Use environment variables instead.{RST}")
    print(f"  Example: Replace 'password = \"secret\"' with 'password = os.environ[\"DB_PASSWORD\"]'")


def create_demo_file():
    """Create a file with fake secrets for demonstration."""
    demo_content = """
# This is a demo file with fake secrets
# DO NOT commit real secrets like these!

# Fake AWS key (for demo only)
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

# Fake database connection
db_url = "postgres://admin:supersecret123@localhost:5432/mydb"

# Fake API key
api_key = 'a1b2c3d4e5f6789012345678901234ab'

# Safe: using environment variable (correct way)
real_api_key = os.environ.get("API_KEY")

# Fake GitHub token
GITHUB_TOKEN = "ghp_abc123xyz456def789ghi012jkl345mno"
"""
    with open("demo_secrets.py", "w") as f:
        f.write(demo_content)
    return "demo_secrets.py"


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Scan source code for hardcoded secrets")
parser.add_argument("--dir",      default=".",  help="Directory to scan")
parser.add_argument("--severity", choices=["CRITICAL","HIGH","MEDIUM","LOW"],
                    help="Filter by minimum severity")
args = parser.parse_args()

print("=== Secret Scanner ===\n")

# Create demo file for demonstration
demo_file = create_demo_file()
print("Demo file created with fake secrets for demonstration.\n")

findings, scanned, skipped = scan_directory(".", severity_filter=args.severity)
print_scan_report(findings, scanned, skipped, ".")

# Clean up demo file
os.remove(demo_file)
print("\n(Demo file cleaned up)")
