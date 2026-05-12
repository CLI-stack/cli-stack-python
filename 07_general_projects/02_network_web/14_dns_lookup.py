"""
Project: DNS Lookup Tool
What it does: Performs DNS (Domain Name System) lookups.
DNS is like a phone book for the internet — it converts domain names
like "google.com" into IP addresses like "142.250.80.46".

Types of DNS records:
  A     = IPv4 address of the domain
  AAAA  = IPv6 address of the domain
  MX    = Mail server for the domain
  NS    = Name servers (who manages the DNS for this domain)
  CNAME = Alias pointing to another domain

Run: python 14_dns_lookup.py  (looks up google.com)
Run: python 14_dns_lookup.py --domain python.org
"""

import socket    # built-in: DNS resolution via gethostbyname
import argparse
import struct    # built-in: for working with binary data (DNS packet parsing)


def lookup_a_record(domain):
    """
    Look up the IPv4 address(es) for a domain.
    socket.getaddrinfo() returns all address information for a domain.
    """
    try:
        # getaddrinfo returns a list of (family, type, proto, canonname, sockaddr)
        # Each sockaddr for AF_INET is (ip_address, port)
        results = socket.getaddrinfo(domain, None, socket.AF_INET)  # AF_INET = IPv4

        # Extract unique IP addresses from the results
        ips = list(set(r[4][0] for r in results))  # r[4][0] = the IP address
        return ips

    except socket.gaierror as e:
        return [f"Error: {e}"]


def lookup_ipv6(domain):
    """Look up IPv6 addresses for a domain (AAAA records)."""
    try:
        results = socket.getaddrinfo(domain, None, socket.AF_INET6)  # AF_INET6 = IPv6
        ips = list(set(r[4][0] for r in results))
        return ips
    except socket.gaierror:
        return []


def reverse_dns(ip_address):
    """
    Reverse DNS lookup: convert an IP address back to a hostname.
    e.g. "8.8.8.8" → "dns.google"
    gethostbyaddr() performs the reverse lookup.
    """
    try:
        # gethostbyaddr returns (hostname, alias_list, ip_list)
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except socket.herror:
        # herror = host error — no reverse DNS record exists
        return "No reverse DNS record"
    except socket.gaierror as e:
        return f"Error: {e}"


def get_whois_like_info(domain):
    """
    Get basic information about a domain using socket functions.
    (A simplified version — real WHOIS requires a separate library)
    """
    info = {}

    # Get the canonical hostname (resolves CNAME chains)
    try:
        canonical = socket.getfqdn(domain)  # FQDN = Fully Qualified Domain Name
        info["canonical_name"] = canonical
    except Exception:
        info["canonical_name"] = domain

    return info


def check_connectivity(host, port=80, timeout=3):
    """Check if we can actually connect to a host (not just resolve its name)."""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def print_dns_report(domain, ipv4, ipv6, reverse_results, extra_info):
    """Display the DNS lookup results."""
    print("=" * 55)
    print(f"  DNS LOOKUP: {domain}")
    print("=" * 55)

    # IPv4 addresses
    print(f"\n  IPv4 Addresses (A records):")
    for ip in ipv4:
        reachable = check_connectivity(ip)
        status    = "✓ reachable" if reachable else "○ no response on port 80"
        print(f"    {ip:<20}  {status}")

    # IPv6 addresses
    if ipv6:
        print(f"\n  IPv6 Addresses (AAAA records):")
        for ip in ipv6:
            print(f"    {ip}")
    else:
        print(f"\n  IPv6 Addresses: None found")

    # Reverse DNS
    if reverse_results:
        print(f"\n  Reverse DNS (IP → Hostname):")
        for ip, hostname in reverse_results.items():
            print(f"    {ip:<20} → {hostname}")

    # Extra info
    canonical = extra_info.get("canonical_name", domain)
    if canonical != domain:
        print(f"\n  Canonical Name: {canonical}")  # CNAME target

    print()


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="DNS lookup tool")
parser.add_argument("--domain",  default="google.com",  help="Domain to look up")
parser.add_argument("--reverse", help="IP address for reverse DNS lookup")
args = parser.parse_args()

print("=== DNS Lookup Tool ===\n")

if args.reverse:
    # Reverse DNS lookup mode
    print(f"Reverse DNS for: {args.reverse}")
    hostname = reverse_dns(args.reverse)
    print(f"Hostname: {hostname}")

else:
    domain = args.domain
    print(f"Looking up: {domain}\n")

    # Get IPv4 addresses
    ipv4 = lookup_a_record(domain)

    # Get IPv6 addresses
    ipv6 = lookup_ipv6(domain)

    # Reverse DNS for each IPv4 address
    reverse_results = {}
    for ip in ipv4:
        if not ip.startswith("Error"):
            reverse_results[ip] = reverse_dns(ip)

    # Extra domain info
    extra_info = get_whois_like_info(domain)

    print_dns_report(domain, ipv4, ipv6, reverse_results, extra_info)

    # Also demonstrate looking up multiple domains
    more_domains = ["cloudflare.com", "openai.com"]
    print("  Quick lookup of additional domains:")
    for d in more_domains:
        ips = lookup_a_record(d)
        print(f"    {d:<25} → {', '.join(ips[:2])}")
