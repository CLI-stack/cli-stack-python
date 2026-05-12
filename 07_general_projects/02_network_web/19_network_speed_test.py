"""
Project: Network Speed Tester
What it does: Estimates your download speed by downloading a known-size
file and measuring how long it takes. Calculates speed in Mbps.

Formula: Speed (Mbps) = (File size in bits) / (Time in seconds) / 1,000,000

Install: pip install requests
Run: python 19_network_speed_test.py
"""

import time
import argparse

try:
    import requests

    # Public test files of known sizes for speed testing
    # These are files hosted by reliable CDNs specifically for testing
    TEST_FILES = {
        "small":  {
            "url":  "https://httpbin.org/bytes/1000000",   # 1 MB
            "size": 1_000_000,
            "label":"1 MB"
        },
        "medium": {
            "url":  "https://httpbin.org/bytes/5000000",   # 5 MB
            "size": 5_000_000,
            "label":"5 MB"
        },
    }

    def measure_download_speed(url, expected_bytes, label):
        """
        Download a file and measure the transfer speed.

        Returns:
          speed_mbps: speed in Megabits per second
          actual_bytes: how many bytes were actually downloaded
          time_seconds: how long the download took
        """
        print(f"  Downloading {label} test file...")

        headers = {"User-Agent": "NetworkSpeedTest/1.0"}

        try:
            start_time  = time.time()
            downloaded  = 0

            # stream=True means download in chunks (doesn't load all into memory at once)
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            chunk_size = 8192  # download 8 KB at a time

            for chunk in response.iter_content(chunk_size=chunk_size):
                downloaded += len(chunk)

                # Show a simple progress indicator
                if downloaded % (chunk_size * 10) == 0:
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        current_speed = (downloaded * 8) / elapsed / 1_000_000
                        bar_len = int(current_speed)  # rough bar length
                        print(f"\r    {downloaded/1000:.0f} KB | "
                              f"{current_speed:.1f} Mbps", end="", flush=True)

            elapsed_seconds = time.time() - start_time

            # Speed formula: bits / seconds / 1,000,000 = Megabits per second
            # downloaded * 8 converts bytes to bits (1 byte = 8 bits)
            speed_mbps = (downloaded * 8) / elapsed_seconds / 1_000_000

            print()  # new line after progress

            return speed_mbps, downloaded, elapsed_seconds

        except requests.exceptions.Timeout:
            print("\n    Timed out after 30 seconds.")
            return 0, 0, 30
        except Exception as e:
            print(f"\n    Error: {e}")
            return 0, 0, 0


    def measure_latency(url="https://httpbin.org/get", attempts=5):
        """
        Measure network latency (ping time) by sending small requests
        and measuring round-trip time.
        Latency = how long it takes to get the FIRST byte back.
        """
        times = []
        headers = {"User-Agent": "LatencyTest/1.0"}

        for i in range(attempts):
            try:
                start    = time.time()
                response = requests.head(url, headers=headers, timeout=5)
                elapsed  = (time.time() - start) * 1000  # convert to ms
                times.append(elapsed)
            except Exception:
                pass

        if not times:
            return 0, 0, 0

        avg  = sum(times) / len(times)
        min_ = min(times)
        max_ = max(times)
        return avg, min_, max_


    def print_speed_report(results, latency_avg, latency_min, latency_max):
        """Display the speed test results."""
        GREEN = "\033[92m"
        YEL   = "\033[33m"
        RED   = "\033[91m"
        RST   = "\033[0m"

        print(f"\n{'='*55}")
        print(f"  NETWORK SPEED TEST RESULTS")
        print(f"{'='*55}")

        # Display speed results for each test
        for label, speed, downloaded, elapsed in results:
            if speed == 0:
                print(f"\n  {label} test: Failed")
                continue

            # Color code the speed
            if speed >= 50:     color = GREEN
            elif speed >= 10:   color = YEL
            else:               color = RED

            print(f"\n  Test: {label}")
            print(f"    Download Speed : {color}{speed:.2f} Mbps{RST}")
            print(f"    Downloaded     : {downloaded/1000:.0f} KB in {elapsed:.2f}s")

        # Latency
        if latency_avg > 0:
            lat_color = GREEN if latency_avg < 50 else (YEL if latency_avg < 150 else RED)
            print(f"\n  Latency (ping):")
            print(f"    Average : {lat_color}{latency_avg:.1f} ms{RST}")
            print(f"    Min     : {latency_min:.1f} ms")
            print(f"    Max     : {latency_max:.1f} ms")

        # Summary
        speeds = [s for _, s, _, _ in results if s > 0]
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            print(f"\n  Average download speed: {avg_speed:.2f} Mbps")

            if avg_speed >= 100:     qual = "Excellent (streaming 4K, large files)"
            elif avg_speed >= 25:    qual = "Good (HD streaming, video calls)"
            elif avg_speed >= 5:     qual = "OK (SD video, web browsing)"
            elif avg_speed >= 1:     qual = "Slow (basic browsing)"
            else:                    qual = "Very slow"
            print(f"  Connection quality: {qual}")


    # ── Main ─────────────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(description="Test your network download speed")
    parser.add_argument("--size", choices=["small", "medium"], default="small",
                        help="Test file size (default: small)")
    args = parser.parse_args()

    print("=== Network Speed Test ===\n")

    # Measure latency first
    print("  Measuring latency...")
    lat_avg, lat_min, lat_max = measure_latency()

    # Run speed test
    results = []
    for key in (["small"] if args.size == "small" else ["small", "medium"]):
        cfg  = TEST_FILES[key]
        speed, downloaded, elapsed = measure_download_speed(cfg["url"], cfg["size"], cfg["label"])
        results.append((cfg["label"], speed, downloaded, elapsed))

    print_speed_report(results, lat_avg, lat_min, lat_max)

except ImportError:
    print("Install: pip install requests")
