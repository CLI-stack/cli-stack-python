"""
Script: File Copier
What it does: Copies a file from one location to another.
Uses Python's built-in shutil module (shell utilities).
"""

import shutil  # shutil = shell utilities, handles file operations
import os

# Create a sample source file to copy
with open("original.txt", "w") as f:
    f.write("This is the original file.\nIt has two lines.")

print("Original file created: original.txt")

# --- Copy a single file ---
shutil.copy("original.txt", "copy_of_original.txt")
print("File copied to: copy_of_original.txt")

# shutil.copy2() also copies file metadata (creation date, etc.)
shutil.copy2("original.txt", "copy_with_metadata.txt")
print("File copied with metadata to: copy_with_metadata.txt")

# --- Copy a file to a different folder ---
os.makedirs("backup_folder", exist_ok=True)  # create folder if not exists
shutil.copy("original.txt", "backup_folder/original.txt")
print("File copied to backup_folder/")

# Verify the copy exists
print("\n=== Verifying copies ===")
for filename in ["copy_of_original.txt", "copy_with_metadata.txt", "backup_folder/original.txt"]:
    if os.path.exists(filename):
        print(f"  ✓ {filename} exists")

# Clean up
os.remove("original.txt")
os.remove("copy_of_original.txt")
os.remove("copy_with_metadata.txt")
shutil.rmtree("backup_folder")  # removes folder and all its contents
print("\nClean up done.")
