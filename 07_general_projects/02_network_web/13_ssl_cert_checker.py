"""
Project: SSL Certificate Checker
What it does: Checks the SSL/TLS certificate of websites to see:
  - When the certificate expires
  - How many days are left
  - Who issued it (Certificate Authority)
  - What domains it's valid for

SSL certificates prove a website's identity and encrypt your connection.
An expired certificate causes browser security warnings and breaks HTTPS.

Run: python 13_ssl_cert_checker.py
Run: python 13_ssl_cert_checker.py --hosts google.com python.org github.com
"""

import ssl           # built-in: SSL/TLS protocol handling
import socket        # built-in: network connections
import argparse
from datetime import datetime


def get_ssl_cert_info(hostname, port=443):
    """
    Connect to a host via HTTPS and retrieve its SSL certificate details.
    Returns a dict with expiry, issuer, subject, and days remaining.
    port=443 is the standard HTTPS port.
    """
    try:
        # Create an SSL context — this handles the encryption settings
        context = ssl.create_default_context()
        # create_default_context() uses safe, modern SSL settings by default

        # Connect and perform the SSL handshake
        with socket.create_connection((hostname, port), timeout=10) as sock:
            # Wrap the plain socket with SSL encryption
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Get the certificate as a Python dict
                cert = ssock.getpeercert()

        # Parse the expiry date from the certificate
        # The date format looks like: "Apr 15 12:00:00 2025 GMT"
        expire_str  = cert.get("notAfter", "")
        expire_date = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z")

        # Parse the valid-from date
        valid_str   = cert.get("notBefore", "")
        valid_from  = datetime.strptime(valid_str, "%b %d %H:%M:%S %Y %Z")

        # Calculate days remaining
        days_remaining = (expire_date - datetime.now()).days

        # Extract issuer information (the company that issued the certificate)
        # cert["issuer"] is a tuple of tuples like ((("O", "DigiCert"),), ...)
        issuer = {}
        for part in cert.get("issuer", []):
            for key, value in part:
                issuer[key] = value  # e.g. {"O": "DigiCert", "CN": "DigiCert..."}

        # Extract subject (who the certificate is FOR)
        subject = {}
        for part in cert.get("subject", []):
            for key, value in part:
                subject[key] = value

        # Get list of domains this certificate is valid for (SANs)
        san_list = []
        for san_type, san_value in cert.get("subjectAltName", []):
            if san_type == "DNS":
                san_list.append(san_value)

        return {
            "hostname":       hostname,
            "valid":          True,
            "expires":        expire_date.strftime("%Y-%m-%d"),
            "valid_from":     valid_from.strftime("%Y-%m-%d"),
            "days_remaining": days_remaining,
            "issuer_org":     issuer.get("O", "Unknown"),
            "issuer_cn":      issuer.get("CN", "Unknown"),
            "subject_cn":     subject.get("CN", hostname),
            "domains":        san_list[:5],  # first 5 valid domains
        }

    except ssl.SSLCertVerificationError as e:
        return {"hostname": hostname, "valid": False, "error": f"Certificate invalid: {e}"}
    except socket.timeout:
        return {"hostname": hostname, "valid": False, "error": "Connection timed out"}
    except ConnectionRefusedError:
        return {"hostname": hostname, "valid": False, "error": "Connection refused"}
    except Exception as e:
        return {"hostname": hostname, "valid": False, "error": str(e)[:80]}


def print_cert_report(results):
    """Display SSL certificate results with color-coded status."""
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print("=" * 65)
    print("  SSL CERTIFICATE REPORT")
    print(f"  Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    for r in results:
        print(f"\n  Host: {r['hostname']}")
        print("  " + "-" * 50)

        if not r.get("valid"):
            print(f"  {RED}ERROR: {r.get('error', 'Unknown error')}{RST}")
            continue

        days = r["days_remaining"]

        # Color-code based on days remaining
        if days <= 0:
            day_color = RED
            status    = "EXPIRED!"
        elif days <= 14:
            day_color = RED
            status    = "CRITICAL — expires very soon!"
        elif days <= 30:
            day_color = YEL
            status    = "WARNING — expires soon"
        else:
            day_color = GREEN
            status    = "OK"

        print(f"  Valid from    : {r['valid_from']}")
        print(f"  Expires       : {r['expires']}")
        print(f"  Days remaining: {day_color}{days}{RST}  ← {status}")
        print(f"  Issuer        : {r['issuer_org']}")
        print(f"  Subject       : {r['subject_cn']}")
        if r["domains"]:
            print(f"  Valid domains : {', '.join(r['domains'][:3])}"
                  + ("..." if len(r["domains"]) > 3 else ""))


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Check SSL certificate expiry for websites")
parser.add_argument("--hosts", nargs="+",
                    default=["google.com", "python.org", "github.com"],
                    help="Hostnames to check")
args = parser.parse_args()

print("=== SSL Certificate Checker ===\n")

results = []
for host in args.hosts:
    print(f"  Checking: {host}...", end="", flush=True)
    info = get_ssl_cert_info(host)
    results.append(info)
    status = "OK" if info.get("valid") else "ERROR"
    print(f" {status}")

print()
print_cert_report(results)
