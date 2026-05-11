"""
Script: Todo List CLI with File Persistence
What it does: A full-featured todo app that saves tasks to a JSON file.
Tasks persist between sessions — they're saved when you add/update/delete.

Run: python 70_todo_cli.py add "Buy groceries"
Run: python 70_todo_cli.py list
Run: python 70_todo_cli.py done 1
Run: python 70_todo_cli.py delete 1
"""

import argparse
import json
import os
from datetime import datetime

# File where todos are saved
TODO_FILE = os.path.expanduser("~/.todos.json")

def load_todos():
    """Load todos from the JSON file."""
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_todos(todos):
    """Save todos to the JSON file."""
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

def get_next_id(todos):
    """Get the next available ID."""
    return max([t["id"] for t in todos], default=0) + 1

# Parse arguments
parser = argparse.ArgumentParser(description="Todo list manager")
subparsers = parser.add_subparsers(dest="command")

subparsers.add_parser("list", help="Show all todos")

add_parser = subparsers.add_parser("add", help="Add a new todo")
add_parser.add_argument("title", help="Todo description")
add_parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium")

done_parser = subparsers.add_parser("done", help="Mark todo as done")
done_parser.add_argument("id", type=int)

delete_parser = subparsers.add_parser("delete", help="Delete a todo")
delete_parser.add_argument("id", type=int)

subparsers.add_parser("clear", help="Delete all todos")

args = parser.parse_args()
todos = load_todos()

PRIORITY_ICONS = {"low": "○", "medium": "◑", "high": "●"}
PRIORITY_COLORS = {"low": "", "medium": "", "high": ""}

if args.command == "add":
    new_todo = {
        "id": get_next_id(todos),
        "title": args.title,
        "done": False,
        "priority": args.priority,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    todos.append(new_todo)
    save_todos(todos)
    print(f"[{new_todo['id']}] Added: {args.title} ({args.priority} priority)")

elif args.command == "list" or args.command is None:
    if not todos:
        print("No todos! Add one with: python 70_todo_cli.py add 'Your task'")
    else:
        pending = [t for t in todos if not t["done"]]
        done = [t for t in todos if t["done"]]
        print(f"Todo List ({len(pending)} pending, {len(done)} done):")
        for t in sorted(todos, key=lambda x: (x["done"], x["id"])):
            status = "✓" if t["done"] else PRIORITY_ICONS.get(t.get("priority", "medium"), "○")
            print(f"  [{t['id']:>2}] {status} {t['title']}")

elif args.command == "done":
    for t in todos:
        if t["id"] == args.id:
            t["done"] = True
            save_todos(todos)
            print(f"Done: {t['title']}")
            break

elif args.command == "delete":
    before = len(todos)
    todos = [t for t in todos if t["id"] != args.id]
    if len(todos) < before:
        save_todos(todos)
        print(f"Deleted todo #{args.id}")
    else:
        print(f"Todo #{args.id} not found")

elif args.command == "clear":
    todos = []
    save_todos(todos)
    print("All todos cleared.")
