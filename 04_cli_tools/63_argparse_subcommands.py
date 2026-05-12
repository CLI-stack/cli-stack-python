"""
Script: CLI with Subcommands (like git or docker)
What it does: Creates a CLI tool that has multiple sub-commands.
Just like how 'git' has: git add, git commit, git push
or 'docker' has: docker run, docker build, docker pull.
Each subcommand has its own arguments.

Run: python 63_argparse_subcommands.py --help
Run: python 63_argparse_subcommands.py add "Buy milk" --priority high
Run: python 63_argparse_subcommands.py list
Run: python 63_argparse_subcommands.py done 1
Run: python 63_argparse_subcommands.py delete 1
"""

import argparse
import json
import os

# Where todos are stored between sessions (in /tmp so it auto-clears on reboot)
TODO_FILE = "/tmp/todos.json"


def load_todos():
    """Load the todo list from disk. Returns empty list if file doesn't exist yet."""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE) as f:
            return json.load(f)   # parse JSON file → Python list of dicts
    return []                     # first run — no todos yet


def save_todos(todos):
    """Save the current todo list to disk so it persists between runs."""
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)  # indent=2 makes the file human-readable


# ── Step 1: Create the main (top-level) parser ───────────────────────────────
parser = argparse.ArgumentParser(description="A simple todo list CLI")

# add_subparsers() creates a container for all the subcommands.
# dest="command" means: store which subcommand the user typed in args.command
subparsers = parser.add_subparsers(dest="command", help="Available commands")

# ── Step 2: Define each subcommand ───────────────────────────────────────────

# 'add' subcommand — has its own arguments
add_parser = subparsers.add_parser("add", help="Add a new todo item")
add_parser.add_argument("title", help="The todo item text")                    # required positional arg
add_parser.add_argument("--priority", choices=["low", "medium", "high"],       # optional flag
                        default="medium", help="Priority level (default: medium)")

# 'list' subcommand — shows all items
list_parser = subparsers.add_parser("list", help="List all todo items")
list_parser.add_argument("--done", action="store_true",                        # flag: True if present
                         help="Show only completed items")

# 'done' subcommand — marks an item complete by its ID
done_parser = subparsers.add_parser("done", help="Mark item as completed")
done_parser.add_argument("id", type=int, help="Item ID number to mark as done")

# 'delete' subcommand — removes an item permanently
delete_parser = subparsers.add_parser("delete", help="Delete an item")
delete_parser.add_argument("id", type=int, help="Item ID number to delete")

# ── Step 3: Parse what the user typed ────────────────────────────────────────
args = parser.parse_args()   # args.command will be "add", "list", "done", "delete", or None
todos = load_todos()         # load existing todos from disk

# ── Step 4: Dispatch to the right action based on the subcommand ─────────────

if args.command == "add":
    # Find the highest existing ID, then add 1 to get a unique new ID
    # default=0 handles the case where the todos list is empty
    new_id = max([t["id"] for t in todos], default=0) + 1

    # Build the new todo dict and add it to the list
    todos.append({
        "id":       new_id,
        "title":    args.title,       # text the user typed
        "priority": args.priority,    # low / medium / high
        "done":     False             # new items always start as not done
    })
    save_todos(todos)
    print(f"Added [{new_id}]: {args.title} (priority: {args.priority})")

elif args.command == "list":
    # If --done flag was given, show only completed items; otherwise show all
    items = [t for t in todos if t["done"] == args.done] if args.done else todos

    if not items:
        print("No items found.")
    for t in items:
        status = "✓" if t["done"] else "○"   # ✓ = done, ○ = pending
        print(f"  [{t['id']}] {status} {t['title']} ({t['priority']})")

elif args.command == "done":
    # Walk through todos to find the matching ID and mark it complete
    for t in todos:
        if t["id"] == args.id:
            t["done"] = True          # flip the done flag to True
            save_todos(todos)
            print(f"Marked [{args.id}] as done!")
            break                     # stop searching once we found and updated it

elif args.command == "delete":
    # Rebuild the list keeping every item EXCEPT the one with the matching ID
    # This is a list comprehension that filters OUT the deleted item
    todos = [t for t in todos if t["id"] != args.id]
    save_todos(todos)
    print(f"Deleted item {args.id}")

else:
    # No subcommand was given — show the help message
    parser.print_help()
