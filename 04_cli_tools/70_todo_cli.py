"""
Script: Todo List CLI with File Persistence
What it does: A full-featured todo app that saves tasks to a JSON file
in your home directory (~/.todos.json). Tasks survive between sessions —
they are saved when you add, complete, or delete items.

Run: python 70_todo_cli.py add "Buy groceries"
Run: python 70_todo_cli.py add "Fix bug" --priority high
Run: python 70_todo_cli.py list
Run: python 70_todo_cli.py done 1
Run: python 70_todo_cli.py delete 1
Run: python 70_todo_cli.py clear
"""

import argparse
import json
import os
from datetime import datetime

# os.path.expanduser("~") converts "~" to the actual home directory path
# e.g. "/home/alice/.todos.json" — a hidden file in the user's home folder
TODO_FILE = os.path.expanduser("~/.todos.json")


def load_todos():
    """Load todos from the JSON file. Returns an empty list on first run."""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)   # JSON file → Python list of dicts
    return []                     # file doesn't exist yet → start fresh


def save_todos(todos):
    """Write the current todo list to disk as a JSON file."""
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)  # indent=2 makes the file readable by humans


def get_next_id(todos):
    """Return the next unique ID (max existing ID + 1, or 1 if list is empty)."""
    # max() with default=0 safely handles the case where todos is an empty list
    return max([t["id"] for t in todos], default=0) + 1


# ── Argument parser setup ─────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Todo list manager")
subparsers = parser.add_subparsers(dest="command")   # stores which subcommand was used

# 'list' — no extra arguments needed
subparsers.add_parser("list", help="Show all todos")

# 'add' — requires the task text, optionally a priority level
add_parser = subparsers.add_parser("add", help="Add a new todo")
add_parser.add_argument("title", help="Todo description text")
add_parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium",
                        help="Task priority (default: medium)")

# 'done' — requires the numeric ID of the task to mark complete
done_parser = subparsers.add_parser("done", help="Mark todo as done")
done_parser.add_argument("id", type=int, help="ID number of the todo to complete")

# 'delete' — requires the numeric ID of the task to remove
delete_parser = subparsers.add_parser("delete", help="Delete a todo")
delete_parser.add_argument("id", type=int, help="ID number of the todo to delete")

# 'clear' — no arguments needed, removes everything
subparsers.add_parser("clear", help="Delete all todos")

# ── Parse arguments and load data ────────────────────────────────────────────
args  = parser.parse_args()  # reads what the user typed on the command line
todos = load_todos()         # load existing todos from ~/.todos.json

# Visual icons for each priority level — shown when listing todos
PRIORITY_ICONS = {
    "low":    "○",   # empty circle = low urgency
    "medium": "◑",   # half circle = medium urgency
    "high":   "●",   # filled circle = high urgency
}

# ── Command dispatch ──────────────────────────────────────────────────────────

if args.command == "add":
    # Build a dict representing the new todo item
    new_todo = {
        "id":       get_next_id(todos),                          # unique auto-increment ID
        "title":    args.title,                                  # the task description
        "done":     False,                                       # not completed yet
        "priority": args.priority,                               # low / medium / high
        "created":  datetime.now().strftime("%Y-%m-%d %H:%M")   # timestamp for reference
    }
    todos.append(new_todo)   # add to the list in memory
    save_todos(todos)        # write the updated list to disk
    print(f"[{new_todo['id']}] Added: {args.title} ({args.priority} priority)")

elif args.command == "list" or args.command is None:
    # 'list' OR no command at all → show the full list
    if not todos:
        print("No todos! Add one with: python 70_todo_cli.py add 'Your task'")
    else:
        # Separate done and pending for the summary count
        pending = [t for t in todos if not t["done"]]
        done    = [t for t in todos if     t["done"]]
        print(f"Todo List ({len(pending)} pending, {len(done)} done):")

        # Sort: pending items first (done=False < done=True), then by ID within each group
        for t in sorted(todos, key=lambda x: (x["done"], x["id"])):
            # Done items get a checkmark; pending items get a priority icon
            status = "✓" if t["done"] else PRIORITY_ICONS.get(t.get("priority", "medium"), "○")
            # :>2 right-aligns the ID number in a field of width 2
            print(f"  [{t['id']:>2}] {status} {t['title']}")

elif args.command == "done":
    # Find the todo with the matching ID and mark it complete
    for t in todos:
        if t["id"] == args.id:
            t["done"] = True     # flip the done flag to True
            save_todos(todos)    # persist the change to disk
            print(f"Done: {t['title']}")
            break                # stop looping once we found and updated it

elif args.command == "delete":
    before = len(todos)  # remember how many items we had before

    # Rebuild the list keeping every item EXCEPT the one with the given ID
    todos = [t for t in todos if t["id"] != args.id]

    if len(todos) < before:    # if the list got shorter, deletion was successful
        save_todos(todos)
        print(f"Deleted todo #{args.id}")
    else:
        print(f"Todo #{args.id} not found")   # ID didn't exist

elif args.command == "clear":
    todos = []            # replace the list with an empty one
    save_todos(todos)     # save the empty list to disk (overwrites existing file)
    print("All todos cleared.")
