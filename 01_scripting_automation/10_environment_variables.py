"""
Script: Environment Variables
What it does: Reads environment variables from the operating system.
Environment variables store system-wide settings like API keys, paths, and config.
They keep sensitive data (like passwords) out of your code.
"""

import os  # os module provides access to environment variables

# --- Read an environment variable ---
# os.environ is like a dictionary of all env variables
home_dir = os.environ.get("HOME")  # .get() is safe — returns None if not found
print(f"Home directory: {home_dir}")

# Read PATH variable (where system looks for executables)
path = os.environ.get("PATH")
print(f"\nPATH (first 100 chars): {path[:100]}...")

# --- Set a temporary environment variable ---
os.environ["MY_APP_NAME"] = "PythonLearner"
os.environ["MY_APP_VERSION"] = "1.0"

# Now read it back
app_name = os.environ.get("MY_APP_NAME")
app_version = os.environ.get("MY_APP_VERSION")
print(f"\nApp Name: {app_name}")
print(f"App Version: {app_version}")

# --- Safe way to read with a default value ---
# If "API_KEY" doesn't exist, use "not_set" as default
api_key = os.environ.get("API_KEY", "not_set")
print(f"\nAPI Key: {api_key}")

# --- List all environment variables ---
print("\n=== First 5 environment variables ===")
for i, (key, value) in enumerate(os.environ.items()):
    if i >= 5:
        break
    print(f"  {key} = {value[:50]}")  # show first 50 chars of value

# Check if a specific variable exists
if "HOME" in os.environ:
    print("\n✓ HOME variable is set")
else:
    print("\n✗ HOME variable is not set")
