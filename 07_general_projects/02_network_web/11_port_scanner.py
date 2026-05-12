"""
Project: Port Scanner
What it does: Checks which network ports on a host are open (accepting connections).
Ports are like numbered doors on a computer. Open ports mean a service is listening:
  Port 80  = HTTP web server
  Port 443 = HTTPS web server
  Port 22  = SSH (remote login)
  Port 3306 = MySQL database

Security note: Only scan hosts you own or have permission to scan.

Run: python 11_port_scanner.py  (scans localhost)
Run: python 11_port_scanner.py --host localhost --ports 1-1024
"""

import socket    # built-in: low-level networking (creating TCP connections)
import argparse
import time
from datetime import datetime


# Dictionary of well-known port numbers and their services
COMMON_PORTS = {
    21:   "FTP",
    22:   "SSH",
    23:   "Telnet",
    25:   "SMTP (email)",
    53:   "DNS",
    80:   "HTTP",
    110:  "POP3 (email)",
    143:  "IMAP (email)",
    443:  "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP Alt",
    8443: "HTTPS Alt",
    27017:"MongoDB",
}


def scan_port(host, port, timeout=0.5):
    """
    Try to open a TCP connection to host:port.
    If the connection succeeds → port is OPEN (a service is listening).
    If the connection fails → port is CLOSED or FILTERED.

    timeout: how long to wait for a response (in seconds).
    A short timeout makes scans faster but may miss slow services.
    """
    # socket.socket() creates a new socket object
    # AF_INET = IPv4 addressing, SOCK_STREAM = TCP connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set how long to wait before giving up on a connection attempt
    sock.settimeout(timeout)

    try:
        # connect_ex() attempts to connect and returns:
        #   0 = connection succeeded (port is OPEN)
        #   non-zero error code = connection failed (port is CLOSED)
        result = sock.connect_ex((host, port))
        return result == 0  # True = open, False = closed

    except socket.error:
        return False  # any network error means the port is not reachable

    finally:
        # Always close the socket to free system resources
        # 'finally' runs even if an exception was raised
        sock.close()


def resolve_hostname(host):
    """
    Convert a hostname like 'google.com' to an IP address like '142.250.80.46'.
    socket.gethostbyname() performs a DNS lookup.
    """
    try:
        ip = socket.gethostbyname(host)  # DNS lookup
        return ip
    except socket.gaierror:
        # gaierror = 'getaddrinfo error' — hostname couldn't be resolved
        return None


def scan_range(host, start_port, end_port, timeout=0.5):
    """Scan all ports in a range and return a list of open ports."""
    open_ports = []
    total      = end_port - start_port + 1

    print(f"Scanning {host} ports {start_port}-{end_port}...")
    print(f"Timeout: {timeout}s per port | "
          f"Est. time: {total * timeout / 60:.1f} min (max)\n")

    for port in range(start_port, end_port + 1):
        # Show progress every 100 ports
        if port % 100 == 0 or port == start_port:
            pct = (port - start_port) / total * 100
            print(f"\r  Progress: {pct:.0f}% (port {port})", end="", flush=True)

        if scan_port(host, port, timeout):
            open_ports.append(port)

    print("\r  Progress: 100%              ")  # clear the progress line
    return open_ports


def print_results(host, ip, open_ports, elapsed):
    """Display the scan results."""
    print(f"\n{'='*55}")
    print(f"  PORT SCAN RESULTS")
    print(f"  Host: {host}  ({ip})")
    print(f"  Scanned at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Elapsed:    {elapsed:.2f} seconds")
    print(f"{'='*55}")

    if not open_ports:
        print("\n  No open ports found.")
    else:
        print(f"\n  Found {len(open_ports)} open port(s):\n")
        print(f"  {'PORT':>6}  {'SERVICE':<20}  STATUS")
        print("  " + "-" * 35)
        for port in open_ports:
            service = COMMON_PORTS.get(port, "Unknown")
            print(f"  {port:>6}  {service:<20}  OPEN")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Scan open TCP ports on a host")
parser.add_argument("--host",    default="localhost", help="Host to scan")
parser.add_argument("--ports",   default="20-100",    help="Port range e.g. 1-1024")
parser.add_argument("--timeout", type=float, default=0.3, help="Timeout per port (seconds)")
args = parser.parse_args()

print("=== Port Scanner ===\n")

# Parse the port range (e.g. "20-100" → start=20, end=100)
try:
    start, end = map(int, args.ports.split("-"))
except ValueError:
    start = end = int(args.ports)  # single port

# Resolve hostname to IP
ip = resolve_hostname(args.host)
if not ip:
    print(f"Cannot resolve hostname: {args.host}")
    exit(1)

print(f"Host: {args.host} ({ip})")

# Run the scan and time it
t0         = time.time()
open_ports = scan_range(ip, start, end, timeout=args.timeout)
elapsed    = time.time() - t0

print_results(args.host, ip, open_ports, elapsed)
