"""
Script: Batch File Renamer
What it does: Renames multiple files at once using a rule.
For example: add a prefix, add a number, or change extensions.
Very useful for organizing large collections of files.
"""

import os

# Create test files to rename
os.makedirs("photos", exist_ok=True)
filenames = ["photo.jpg", "image.jpg", "picture.jpg", "snapshot.jpg", "shot.jpg"]
for name in filenames:
    with open(f"photos/{name}", "w") as f:
        f.write("fake image content")

print("Test files created:", filenames)

# --- Strategy 1: Add a number prefix (001_, 002_, ...) ---
def add_number_prefix(folder):
    files = sorted(os.listdir(folder))  # sort alphabetically first
    for index, filename in enumerate(files, start=1):
        new_name = f"{index:03d}_{filename}"  # 001_, 002_, etc.
        os.rename(
            os.path.join(folder, filename),   # old path
            os.path.join(folder, new_name)    # new path
        )
        print(f"  {filename} → {new_name}")

print("\n=== Adding number prefix ===")
add_number_prefix("photos")

# --- Strategy 2: Replace extension ---
def change_extension(folder, old_ext, new_ext):
    for filename in os.listdir(folder):
        if filename.endswith(old_ext):
            new_name = filename.replace(old_ext, new_ext)
            os.rename(
                os.path.join(folder, filename),
                os.path.join(folder, new_name)
            )
            print(f"  {filename} → {new_name}")

print("\n=== Changing .jpg to .jpeg ===")
change_extension("photos", ".jpg", ".jpeg")

# Show final result
print("\n=== Final file list ===")
for f in sorted(os.listdir("photos")):
    print(" -", f)

# Clean up
import shutil
shutil.rmtree("photos")
