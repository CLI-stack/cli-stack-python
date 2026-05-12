"""
Project: IP Geolocation Lookup
What it does: Finds the geographic location of an IP address — country, city,
timezone, and ISP. Uses a free public API (no key required).

Useful for: analytics, security monitoring, personalizing content by location.

Install: pip install requests
Run: python 15_ip_geolocation.py  (uses your current public IP)
Run: python 15_ip_geolocation.py --ip 8.8.8.8  (Google's DNS server)
Run: python 15_ip_geolocation.py --ip 1.1.1.1  (Cloudflare's DNS)
"""

import argparse

try:
    import requests
    import json

    def get_my_ip():
        """
        Find your own public IP address using a free API.
        Your public IP is the address the internet sees — not your local network IP.
        """
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            return response.json()["ip"]
        except Exception:
            return None


    def geolocate_ip(ip_address):
        """
        Look up geographic information for an IP address.
        Uses ip-api.com — free, no API key needed, limited to 45 requests/minute.
        """
        # The 'fields' parameter specifies which data fields to return
        fields = "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"

        try:
            url      = f"http://ip-api.com/json/{ip_address}?fields={fields}"
            response = requests.get(url, timeout=10)
            data     = response.json()

            if data.get("status") == "fail":
                return {"error": data.get("message", "Unknown error")}

            return data

        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to API — check your internet connection"}
        except Exception as e:
            return {"error": str(e)}


    def format_coordinates(lat, lon):
        """Format latitude/longitude as a Google Maps link."""
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        return (f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}",
                f"https://maps.google.com/?q={lat},{lon}")


    def print_location_report(ip, data):
        """Display the geolocation results nicely."""
        print(f"\n{'='*55}")
        print(f"  IP GEOLOCATION REPORT")
        print(f"{'='*55}")
        print(f"\n  IP Address  : {ip}")

        if "error" in data:
            print(f"  Error       : {data['error']}")
            return

        # Location info
        print(f"\n  Location:")
        print(f"    Country   : {data.get('country', 'N/A')} "
              f"({data.get('countryCode', '??')})")
        print(f"    Region    : {data.get('regionName', 'N/A')} "
              f"({data.get('region', '')})")
        print(f"    City      : {data.get('city', 'N/A')}")
        print(f"    ZIP Code  : {data.get('zip', 'N/A')}")
        print(f"    Timezone  : {data.get('timezone', 'N/A')}")

        # Coordinates
        lat = data.get("lat")
        lon = data.get("lon")
        if lat and lon:
            coords, maps_link = format_coordinates(lat, lon)
            print(f"    Coordinates: {coords}")
            print(f"    Maps       : {maps_link}")

        # Network info
        print(f"\n  Network:")
        print(f"    ISP       : {data.get('isp', 'N/A')}")
        print(f"    Org       : {data.get('org', 'N/A')}")
        print(f"    AS Number : {data.get('as', 'N/A')}")

        # ASCII map (simple visualization of latitude position)
        if lat:
            equator_pos = int(20 - lat * 20 / 90)  # map -90 to 90 onto 0-40 scale
            equator_pos = max(0, min(40, equator_pos))
            print(f"\n  Approximate Position on Globe:")
            print(f"  North Pole ─┐")
            for i in range(21):
                if i == equator_pos:
                    print(f"              │{'─' * 30}  ← location (lat: {lat:.1f})")
                elif i == 10:
                    print(f"  Equator ────┤")
            print(f"  South Pole ─┘")


    # ── Main ─────────────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description="Geolocate an IP address")
    parser.add_argument("--ip", help="IP address to look up (default: your public IP)")
    args = parser.parse_args()

    print("=== IP Geolocation Lookup ===\n")

    if args.ip:
        target_ip = args.ip
    else:
        print("Getting your public IP address...")
        target_ip = get_my_ip()
        if not target_ip:
            print("Could not determine public IP. Using 8.8.8.8 (Google DNS) as demo.")
            target_ip = "8.8.8.8"
        else:
            print(f"Your public IP: {target_ip}")

    print(f"Looking up: {target_ip}...")
    geo_data = geolocate_ip(target_ip)
    print_location_report(target_ip, geo_data)

    # Demo: look up a few well-known IPs
    print("\n\n  Quick lookup of well-known IPs:")
    known_ips = {"8.8.8.8": "Google DNS", "1.1.1.1": "Cloudflare DNS"}
    for ip, name in known_ips.items():
        data = geolocate_ip(ip)
        city = data.get("city", "?")
        country = data.get("country", "?")
        print(f"    {ip:<15} ({name:<18}) → {city}, {country}")

except ImportError:
    print("Install: pip install requests")
