"""
Project: File Organizer by Extension
What it does: Automatically sorts files in a messy folder into subfolders
based on their file type. Downloads folders often get cluttered — this
script organizes everything automatically.

Example: a folder with photos, documents, videos gets sorted into:
  Images/    ← .jpg, .png, .gif
  Documents/ ← .pdf, .docx, .txt
  Videos/    ← .mp4, .avi
  Others/    ← anything else

Run: python 03_file_organizer.py  (organizes current folder)
Run: python 03_file_organizer.py --folder /path/to/folder --dry-run
"""

import os
import shutil    # shell utilities: move, copy, delete files/folders
import argparse
from datetime import datetime


# Define which extensions belong to which category
# You can customize this dict to add your own file types
FILE_CATEGORIES = {
    "Images":     [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "Documents":  [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".odt"],
    "Videos":     [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "Audio":      [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Archives":   [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2"],
    "Code":       [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".sh"],
    "Data":       [".csv", ".json", ".xml", ".yaml", ".yml", ".sql"],
}


def get_category(filename):
    """
    Determine which category folder a file belongs in.
    Returns the category name, or 'Others' if the extension is unknown.
    """
    # os.path.splitext() splits "photo.jpg" into ("photo", ".jpg")
    _, extension = os.path.splitext(filename)
    extension = extension.lower()  # normalize: ".JPG" → ".jpg"

    # Check each category's extension list
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category  # found a match!

    return "Others"  # no match found — goes to the catch-all folder


def organize_folder(folder_path, dry_run=False):
    """
    Scan a folder and move each file into a category subfolder.

    dry_run=True: only SHOW what would happen without actually moving files.
    This is useful for previewing before committing to changes.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid folder.")
        return

    # Collect all files in the top-level folder (not subfolders)
    all_files = [f for f in os.listdir(folder_path)
                 if os.path.isfile(os.path.join(folder_path, f))]

    if not all_files:
        print("No files to organize.")
        return

    moved_count = 0
    skipped     = []
    moves       = {}  # track: filename → destination category

    for filename in sorted(all_files):  # sorted() processes alphabetically
        # Determine which category this file belongs to
        category = get_category(filename)
        moves[filename] = category

        # Build the full path to the destination folder
        dest_folder = os.path.join(folder_path, category)
        dest_file   = os.path.join(dest_folder, filename)
        src_file    = os.path.join(folder_path, filename)

        if dry_run:
            # Dry-run mode: just print what WOULD happen
            print(f"  Would move: {filename:<30} → {category}/")
        else:
            # Create the destination folder if it doesn't exist
            # exist_ok=True means no error if the folder already exists
            os.makedirs(dest_folder, exist_ok=True)

            # Check if a file with the same name already exists in the destination
            if os.path.exists(dest_file):
                # Add a timestamp to avoid overwriting: "photo.jpg" → "photo_20240115.jpg"
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name  = f"{name}_{timestamp}{ext}"
                dest_file = os.path.join(dest_folder, new_name)
                print(f"  Name conflict — renamed to: {new_name}")

            # Move the file from source to destination
            shutil.move(src_file, dest_file)
            moved_count += 1
            print(f"  Moved: {filename:<30} → {category}/")

    # Print summary
    print(f"\n{'=== DRY RUN COMPLETE ===' if dry_run else '=== DONE ==='}")
    if dry_run:
        from collections import Counter
        cat_counts = Counter(moves.values())
        for cat, count in sorted(cat_counts.items()):
            print(f"  {cat:<15} {count} files")
    else:
        print(f"  Moved {moved_count} files into category subfolders.")


def create_demo_folder():
    """Create a messy demo folder with mixed file types."""
    os.makedirs("messy_folder", exist_ok=True)

    # Create fake files of different types (empty files with the right extension)
    demo_files = [
        "vacation_photo.jpg", "report_2024.pdf", "music.mp3",
        "video_clip.mp4", "data_export.csv", "script.py",
        "presentation.pptx", "archive.zip", "notes.txt", "icon.png"
    ]

    for filename in demo_files:
        # Create an empty file just to have the right extension
        with open(os.path.join("messy_folder", filename), "w") as f:
            f.write(f"Content of {filename}")

    print("Demo folder created: messy_folder/")
    print(f"Files: {', '.join(demo_files)}\n")
    return "messy_folder"


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Organize files into folders by type")
parser.add_argument("--folder",  help="Folder to organize (default: creates demo)")
parser.add_argument("--dry-run", action="store_true",
                    help="Preview what would happen without moving files")
args = parser.parse_args()

print("=== File Organizer ===\n")

if args.folder:
    folder = args.folder
else:
    folder = create_demo_folder()

mode = "DRY RUN MODE — no files will be moved" if args.dry_run else "LIVE MODE — files will be moved"
print(f"Folder: {folder}")
print(f"Mode:   {mode}\n")

organize_folder(folder, dry_run=args.dry_run)

# Clean up demo
if not args.folder:
    import shutil
    shutil.rmtree("messy_folder")
    print("\n(Demo folder cleaned up)")
