"""
Script: ZIP File Handler
What it does: Creates, reads, and extracts ZIP archive files.
Useful for compressing files or unpacking downloaded archives.
"""

import zipfile  # built-in module for ZIP files
import os

# --- Create a few test files to zip ---
os.makedirs("files_to_zip", exist_ok=True)
for i in range(3):
    with open(f"files_to_zip/file{i+1}.txt", "w") as f:
        f.write(f"This is file number {i+1}.\nSome sample content here.")

print("Test files created in 'files_to_zip/'")

# --- Create a ZIP archive ---
with zipfile.ZipFile("archive.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
    # ZIP_DEFLATED = compress the files (smaller file size)
    for filename in os.listdir("files_to_zip"):
        filepath = os.path.join("files_to_zip", filename)
        zipf.write(filepath, arcname=filename)  # arcname = name inside the ZIP
        print(f"  Added: {filename}")

print("\nCreated: archive.zip")

# --- List contents of a ZIP file without extracting ---
print("\n=== Contents of archive.zip ===")
with zipfile.ZipFile("archive.zip", "r") as zipf:
    for info in zipf.infolist():
        print(f"  {info.filename} ({info.file_size} bytes)")

# --- Extract the ZIP file ---
os.makedirs("extracted_files", exist_ok=True)
with zipfile.ZipFile("archive.zip", "r") as zipf:
    zipf.extractall("extracted_files")  # extract everything to a folder
    print(f"\nExtracted to: extracted_files/")
    print("Files:", os.listdir("extracted_files"))

# Clean up
import shutil
shutil.rmtree("files_to_zip")
shutil.rmtree("extracted_files")
os.remove("archive.zip")
print("\nClean up done.")
