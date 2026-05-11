"""
Script: Command Runner
What it does: Runs shell commands from inside Python.
Useful for automating system tasks, running scripts, or getting system info.
"""

import subprocess  # module to run external commands

# --- Run a simple command and get output ---
print("=== Run 'echo' command ===")
result = subprocess.run(
    ["echo", "Hello from shell!"],  # command as a list
    capture_output=True,            # capture stdout and stderr
    text=True                       # return output as string (not bytes)
)
print("Output:", result.stdout)     # stdout = standard output

# --- Get current date from the system ---
print("=== Get current date ===")
result = subprocess.run(["date"], capture_output=True, text=True)
print("Date:", result.stdout.strip())

# --- List files (like running 'ls') ---
print("=== List files in current directory ===")
result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
print(result.stdout[:300])  # show first 300 characters

# --- Check return code (0 = success, non-zero = error) ---
print("=== Check if command succeeded ===")
result = subprocess.run(["ls", "/nonexistent_folder"], capture_output=True, text=True)
print(f"Return code: {result.returncode}")  # 0 = success
if result.returncode != 0:
    print(f"Error: {result.stderr.strip()}")

# --- Run a command and get just the output as a string ---
hostname = subprocess.check_output(["hostname"], text=True).strip()
print(f"\nHostname: {hostname}")

# --- Use shell=True to run a full shell command string ---
result = subprocess.run("echo Python + Shell = Powerful", shell=True, capture_output=True, text=True)
print("\nShell command output:", result.stdout.strip())
