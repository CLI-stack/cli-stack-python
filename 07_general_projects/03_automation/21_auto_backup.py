"""
Project: Auto Backup Tool
What it does: Automatically backs up files and folders to a destination.
Creates timestamped backups so you can restore any version.
Compresses the backup into a ZIP archive to save space.

Run: python 21_auto_backup.py  (creates a demo backup)
Run: python 21_auto_backup.py --source /path/to/project --dest /backups
"""

import os
import shutil
import zipfile
import argparse
from datetime import datetime
from pathlib import Path


def create_backup(source_path, dest_dir, max_backups=5):
    """
    Create a timestamped ZIP backup of a folder.

    source_path: the folder or file to back up
    dest_dir:    where to store the backup archives
    max_backups: keep only this many backups (delete older ones)
    """
    source   = Path(source_path)
    dest     = Path(dest_dir)

    # Create the backup destination directory if it doesn't exist
    dest.mkdir(parents=True, exist_ok=True)

    # Build a timestamped filename: "myproject_2024-01-15_143022.zip"
    timestamp   = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_name = f"{source.name}_{timestamp}.zip"
    backup_path = dest / backup_name

    print(f"Source : {source}")
    print(f"Dest   : {backup_path}")
    print(f"Creating backup...")

    # Count total files for progress
    total_files = sum(1 for _ in source.rglob("*") if _.is_file()) if source.is_dir() else 1
    zipped = 0

    # Create the ZIP archive
    # zipfile.ZIP_DEFLATED = use compression (smaller file size)
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
        if source.is_file():
            # Back up a single file
            zf.write(source, source.name)  # arcname = name inside the ZIP
            zipped = 1
        else:
            # Back up an entire directory recursively
            for file_path in source.rglob("*"):
                if file_path.is_file():
                    # arcname = relative path inside the ZIP
                    arcname = file_path.relative_to(source.parent)
                    zf.write(file_path, arcname)
                    zipped += 1
                    print(f"\r  Added {zipped}/{total_files} files", end="", flush=True)

    print(f"\r  Zipped {zipped} files" + " " * 20)

    # Show backup size
    backup_size = backup_path.stat().st_size
    print(f"  Backup size: {backup_size / 1024:.1f} KB")

    # ── Rotation: remove old backups to stay within max_backups ───────────────
    # Find all existing backups for this source
    pattern  = f"{source.name}_*.zip"
    existing = sorted(dest.glob(pattern))  # sorted alphabetically = oldest first

    if len(existing) > max_backups:
        to_delete = existing[:len(existing) - max_backups]  # oldest ones
        for old_backup in to_delete:
            old_backup.unlink()  # delete the file
            print(f"  Deleted old backup: {old_backup.name}")

    print(f"\nBackup complete: {backup_name}")
    return backup_path


def list_backups(backup_dir, source_name=None):
    """List all backups in the backup directory."""
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        print("No backups found.")
        return

    pattern = f"{source_name}_*.zip" if source_name else "*.zip"
    backups = sorted(backup_path.glob(pattern), reverse=True)  # newest first

    if not backups:
        print("No backup files found.")
        return

    print(f"\nBackups in {backup_dir}:")
    print(f"{'FILENAME':<50} {'SIZE':>10} {'MODIFIED'}")
    print("-" * 75)
    for backup in backups:
        size   = backup.stat().st_size / 1024
        mtime  = datetime.fromtimestamp(backup.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"{backup.name:<50} {size:>8.1f}KB {mtime}")


def demo_backup():
    """Create a demo folder structure and back it up."""
    # Create a sample project folder
    demo_src = Path("demo_project")
    (demo_src / "src").mkdir(parents=True, exist_ok=True)
    (demo_src / "docs").mkdir(exist_ok=True)

    # Write some demo files
    (demo_src / "src" / "main.py").write_text("# Main module\nprint('hello')\n")
    (demo_src / "src" / "utils.py").write_text("# Utility functions\n")
    (demo_src / "docs" / "README.md").write_text("# My Project\nDocumentation here.\n")
    (demo_src / "config.json").write_text('{"version": "1.0"}\n')

    print("Demo project created.\n")

    # Create two backups to demonstrate rotation
    for _ in range(2):
        create_backup("demo_project", "demo_backups", max_backups=3)
        print()

    list_backups("demo_backups")

    # Clean up
    shutil.rmtree("demo_project")
    shutil.rmtree("demo_backups")
    print("\n(Demo files cleaned up)")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Backup files/folders to a ZIP archive")
parser.add_argument("--source", help="Source folder to backup")
parser.add_argument("--dest",   help="Backup destination directory")
parser.add_argument("--keep",   type=int, default=5, help="Max backups to keep (default: 5)")
parser.add_argument("--list",   action="store_true", help="List existing backups")
args = parser.parse_args()

print("=== Auto Backup Tool ===\n")

if args.list and args.dest:
    list_backups(args.dest)
elif args.source and args.dest:
    create_backup(args.source, args.dest, max_backups=args.keep)
else:
    demo_backup()
