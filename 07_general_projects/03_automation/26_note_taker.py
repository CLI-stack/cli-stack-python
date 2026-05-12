"""
Project: Quick Note Taker CLI
What it does: A fast command-line note-taking app. Add, search, list,
and delete notes. Notes are stored in a JSON file with timestamps and tags.
Designed for quick capture — faster than opening a text editor.

Run: python 26_note_taker.py add "Remember to call Bob about the meeting"
Run: python 26_note_taker.py add "Python tip: use enumerate() instead of range(len())" --tag python
Run: python 26_note_taker.py list
Run: python 26_note_taker.py search "Python"
Run: python 26_note_taker.py show 1
"""

import json
import os
import argparse
from datetime import datetime


NOTES_FILE = "notes.json"


def load_notes():
    """Load notes from the JSON file. Returns empty dict on first run."""
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE) as f:
            return json.load(f)
    return {"notes": [], "next_id": 1}


def save_notes(data):
    """Persist notes to disk."""
    with open(NOTES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_note(content, tag="general"):
    """Add a new note with an auto-generated ID and timestamp."""
    data    = load_notes()
    note_id = data["next_id"]

    note = {
        "id":      note_id,
        "content": content,
        "tag":     tag.lower(),                                # normalize tag to lowercase
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"), # human-readable timestamp
        "pinned":  False,                                      # pinned notes show first
    }

    data["notes"].append(note)
    data["next_id"] += 1  # increment for the next note
    save_notes(data)

    print(f"Note #{note_id} added  [{tag}]")
    print(f"  '{content[:60]}{'...' if len(content) > 60 else ''}'")


def list_notes(tag_filter=None, limit=20):
    """List notes, optionally filtered by tag, newest first."""
    data  = load_notes()
    notes = data["notes"]

    if not notes:
        print("No notes yet! Try: python 26_note_taker.py add 'Your note here'")
        return

    # Apply tag filter if specified
    if tag_filter:
        notes = [n for n in notes if n["tag"] == tag_filter.lower()]
        if not notes:
            print(f"No notes with tag '{tag_filter}'")
            return

    # Sort: pinned notes first, then newest first
    notes = sorted(notes, key=lambda n: (not n.get("pinned", False), -n["id"]))

    print(f"\n  Your Notes ({len(notes)} total):\n")
    print(f"  {'ID':>4}  {'TAG':<12}  {'CREATED':<17}  NOTE")
    print("  " + "─" * 70)

    for note in notes[:limit]:
        pin     = "📌 " if note.get("pinned") else "   "
        preview = note["content"][:55] + ("..." if len(note["content"]) > 55 else "")
        print(f"  {note['id']:>4}  {note['tag']:<12}  {note['created']:<17}  {pin}{preview}")

    if len(notes) > limit:
        print(f"\n  ... {len(notes) - limit} more notes (use --limit to see more)")


def show_note(note_id):
    """Show the full content of a single note."""
    data  = load_notes()
    note  = next((n for n in data["notes"] if n["id"] == note_id), None)

    if not note:
        print(f"Note #{note_id} not found.")
        return

    print(f"\n  Note #{note['id']}")
    print(f"  {'─'*50}")
    print(f"  Tag     : {note['tag']}")
    print(f"  Created : {note['created']}")
    print(f"  Pinned  : {'Yes' if note.get('pinned') else 'No'}")
    print(f"\n  {note['content']}")


def search_notes(keyword):
    """Search notes by keyword (case-insensitive)."""
    data    = load_notes()
    keyword = keyword.lower()

    # Search in both content and tag
    matches = [n for n in data["notes"]
               if keyword in n["content"].lower() or keyword in n["tag"].lower()]

    if not matches:
        print(f"No notes found containing '{keyword}'")
        return

    print(f"\n  Found {len(matches)} note(s) containing '{keyword}':\n")
    for note in matches:
        # Highlight the matching keyword in the preview
        content   = note["content"]
        idx       = content.lower().find(keyword)
        if idx >= 0:
            # Show context around the match
            start   = max(0, idx - 20)
            end     = min(len(content), idx + len(keyword) + 30)
            preview = ("..." if start > 0 else "") + content[start:end] + ("..." if end < len(content) else "")
        else:
            preview = content[:60]

        print(f"  [{note['id']}] {note['tag']:<12} {preview}")


def delete_note(note_id):
    """Remove a note permanently."""
    data         = load_notes()
    before_count = len(data["notes"])

    # Keep all notes except the one with the matching ID
    data["notes"] = [n for n in data["notes"] if n["id"] != note_id]

    if len(data["notes"]) < before_count:
        save_notes(data)
        print(f"Deleted note #{note_id}")
    else:
        print(f"Note #{note_id} not found")


def show_tags(data=None):
    """Show all tags and how many notes each has."""
    if data is None:
        data = load_notes()

    from collections import Counter
    tag_counts = Counter(n["tag"] for n in data["notes"])

    print(f"\n  Tags ({len(tag_counts)} unique):")
    for tag, count in tag_counts.most_common():
        print(f"    #{tag:<20} {count} note(s)")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Quick command-line note taker")
subparsers = parser.add_subparsers(dest="command")

add_p = subparsers.add_parser("add", help="Add a new note")
add_p.add_argument("content", nargs="+", help="Note content (multi-word)")
add_p.add_argument("--tag", default="general", help="Tag to categorize the note")

list_p = subparsers.add_parser("list", help="List all notes")
list_p.add_argument("--tag",   help="Filter by tag")
list_p.add_argument("--limit", type=int, default=20)

show_p = subparsers.add_parser("show", help="Show a single note in full")
show_p.add_argument("id", type=int)

search_p = subparsers.add_parser("search", help="Search notes by keyword")
search_p.add_argument("keyword")

del_p = subparsers.add_parser("delete", help="Delete a note")
del_p.add_argument("id", type=int)

subparsers.add_parser("tags", help="Show all tags")
args = parser.parse_args()

# Add demo notes if file doesn't exist
if not os.path.exists(NOTES_FILE):
    add_note("Python tip: use f-strings for string formatting", tag="python")
    add_note("Meeting with team on Friday at 2pm", tag="work")
    add_note("Book recommendation: The Pragmatic Programmer", tag="reading")
    add_note("Always commit your work at end of day", tag="work")
    print()

if args.command == "add":
    add_note(" ".join(args.content), tag=args.tag)
elif args.command == "list":
    list_notes(tag_filter=args.tag, limit=args.limit)
elif args.command == "show":
    show_note(args.id)
elif args.command == "search":
    search_notes(args.keyword)
elif args.command == "delete":
    delete_note(args.id)
elif args.command == "tags":
    show_tags()
else:
    list_notes()

# Clean up demo
if os.path.exists(NOTES_FILE):
    os.remove(NOTES_FILE)
