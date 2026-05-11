"""
Script: System Information
What it does: Collects and displays information about your computer —
CPU, memory, disk space, OS version, and more.

Install: pip install psutil
"""

import platform  # built-in: OS and hardware info
import os        # built-in: OS interface

# --- Basic OS Information (no extra install needed) ---
print("=== Operating System ===")
print(f"System:    {platform.system()}")       # Linux, Windows, Darwin (macOS)
print(f"Node:      {platform.node()}")         # computer hostname
print(f"Release:   {platform.release()}")      # OS version
print(f"Machine:   {platform.machine()}")      # hardware type (x86_64, etc.)
print(f"Processor: {platform.processor()}")    # CPU name

print("\n=== Python Info ===")
print(f"Python version: {platform.python_version()}")

# --- CPU count ---
cpu_count = os.cpu_count()
print(f"\nCPU cores: {cpu_count}")

# --- Try to get memory info using psutil ---
try:
    import psutil  # external library for system resource info

    print("\n=== Memory ===")
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024 ** 3)       # convert bytes to GB
    available_gb = mem.available / (1024 ** 3)
    used_percent = mem.percent
    print(f"Total RAM:     {total_gb:.2f} GB")
    print(f"Available RAM: {available_gb:.2f} GB")
    print(f"Used:          {used_percent}%")

    print("\n=== Disk Space ===")
    disk = psutil.disk_usage("/")
    print(f"Total:     {disk.total / (1024**3):.2f} GB")
    print(f"Used:      {disk.used / (1024**3):.2f} GB")
    print(f"Free:      {disk.free / (1024**3):.2f} GB")
    print(f"Used:      {disk.percent}%")

except ImportError:
    print("\npsutil not installed. Run: pip install psutil")
    print("(Showing basic info only)")
