"""
Script: Directory Lister
What it does: Lists all files and folders in a directory.
Similar to running "ls" on Linux or "dir" on Windows.
"""

import os  # os module for interacting with the operating system

# Get the current working directory (where this script is running from)
current_dir = os.getcwd()
print(f"Current directory: {current_dir}\n")

# List everything in the current directory
print("=== All items in current directory ===")
items = os.listdir(current_dir)  # returns a list of file/folder names
for item in items:
    print(" -", item)

# Separate files from folders
print("\n=== Files only ===")
for item in items:
    full_path = os.path.join(current_dir, item)  # build the full path
    if os.path.isfile(full_path):  # check if it's a file
        size = os.path.getsize(full_path)  # get file size in bytes
        print(f"  {item} ({size} bytes)")

print("\n=== Folders only ===")
for item in items:
    full_path = os.path.join(current_dir, item)
    if os.path.isdir(full_path):  # check if it's a folder
        print(f"  {item}/")

# Walk through all subdirectories too (recursive listing)
print("\n=== Full directory tree ===")
for root, dirs, files in os.walk(current_dir):
    # root = current folder path, dirs = subfolders, files = files
    level = root.replace(current_dir, "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    for file in files:
        print(f"{indent}  {file}")
    if level > 1:  # Stop going too deep to keep output short
        break
