"""
Script: CLI with Subcommands (like git)
What it does: Creates a CLI with multiple subcommands, similar to how
  git has: git add, git commit, git push
  or how: docker run, docker build, docker pull

Run: python 63_argparse_subcommands.py --help
Run: python 63_argparse_subcommands.py add --file hello.txt
Run: python 63_argparse_subcommands.py list
Run: python 63_argparse_subcommands.py delete --id 1
"""

import argparse
import json
import os

TODO_FILE = "/tmp/todos.json"

def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE) as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

# --- Main parser ---
parser = argparse.ArgumentParser(description="A simple todo list CLI")
# Create a subparser group for the subcommands
subparsers = parser.add_subparsers(dest="command", help="Available commands")

# --- 'add' subcommand ---
add_parser = subparsers.add_parser("add", help="Add a new todo item")
add_parser.add_argument("title", help="The todo item text")
add_parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium")

# --- 'list' subcommand ---
list_parser = subparsers.add_parser("list", help="List all todo items")
list_parser.add_argument("--done", action="store_true", help="Show only completed items")

# --- 'done' subcommand ---
done_parser = subparsers.add_parser("done", help="Mark item as completed")
done_parser.add_argument("id", type=int, help="Item ID to mark as done")

# --- 'delete' subcommand ---
delete_parser = subparsers.add_parser("delete", help="Delete an item")
delete_parser.add_argument("id", type=int, help="Item ID to delete")

# --- Parse and dispatch ---
args = parser.parse_args()
todos = load_todos()

if args.command == "add":
    new_id = max([t["id"] for t in todos], default=0) + 1
    todos.append({"id": new_id, "title": args.title, "priority": args.priority, "done": False})
    save_todos(todos)
    print(f"Added [{new_id}]: {args.title} (priority: {args.priority})")

elif args.command == "list":
    items = [t for t in todos if t["done"] == args.done] if args.done else todos
    if not items:
        print("No items found.")
    for t in items:
        status = "✓" if t["done"] else "○"
        print(f"  [{t['id']}] {status} {t['title']} ({t['priority']})")

elif args.command == "done":
    for t in todos:
        if t["id"] == args.id:
            t["done"] = True
            save_todos(todos)
            print(f"Marked [{args.id}] as done!")
            break

elif args.command == "delete":
    todos = [t for t in todos if t["id"] != args.id]
    save_todos(todos)
    print(f"Deleted item {args.id}")

else:
    parser.print_help()
