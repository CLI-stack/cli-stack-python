"""
Script: Log File Parser
What it does: Reads a log file and extracts useful information —
counts errors, warnings, and finds specific patterns.
Useful for monitoring applications and diagnosing problems.
"""

import os
import re  # regular expressions for pattern matching

# Create a sample log file
sample_log = """2024-01-15 08:00:01 INFO  Application started
2024-01-15 08:00:05 INFO  Connected to database
2024-01-15 08:01:12 WARNING Low memory: 85% used
2024-01-15 08:05:44 ERROR  Failed to load config file
2024-01-15 08:05:45 INFO  Using default config instead
2024-01-15 08:10:30 ERROR  Database connection lost
2024-01-15 08:10:31 INFO  Retrying connection...
2024-01-15 08:10:35 INFO  Reconnected successfully
2024-01-15 08:15:00 WARNING Disk space low: 90% used
2024-01-15 08:20:00 INFO  Backup completed
"""

with open("app.log", "w") as f:
    f.write(sample_log)

print("Sample log file created: app.log\n")

# --- Count each log level ---
counts = {"INFO": 0, "WARNING": 0, "ERROR": 0}

with open("app.log", "r") as f:
    lines = f.readlines()

for line in lines:
    for level in counts:
        if level in line:
            counts[level] += 1

print("=== Log Summary ===")
for level, count in counts.items():
    print(f"  {level}: {count}")

# --- Extract only ERROR lines ---
print("\n=== ERROR Lines ===")
for line in lines:
    if "ERROR" in line:
        print(" ", line.strip())

# --- Extract timestamps using regex ---
print("\n=== All Timestamps ===")
pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"  # matches date/time format
for line in lines:
    match = re.search(pattern, line)
    if match:
        print(" ", match.group())

os.remove("app.log")
