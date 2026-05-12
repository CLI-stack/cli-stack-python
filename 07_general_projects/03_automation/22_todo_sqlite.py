"""
Project: Todo App with SQLite Database
What it does: A persistent todo list using a real SQLite database.
Unlike storing todos in a JSON file, SQLite gives you powerful queries,
proper data types, and better performance for larger datasets.

SQLite is a file-based database — no server needed. The entire database
is stored in a single .db file.

Run: python 22_todo_sqlite.py add "Buy groceries" --priority high
Run: python 22_todo_sqlite.py list
Run: python 22_todo_sqlite.py done 1
Run: python 22_todo_sqlite.py search "groceries"
Run: python 22_todo_sqlite.py stats
"""

import sqlite3    # built-in: SQLite database interface
import argparse
import os
from datetime import datetime

DB_FILE = "todos.db"


def get_connection():
    """
    Open a connection to the SQLite database file.
    If the file doesn't exist, SQLite creates it automatically.
    """
    conn = sqlite3.connect(DB_FILE)   # creates todos.db if it doesn't exist

    # Row factory: makes query results accessible by column name
    # Without this: row[0], row[1]... With this: row["title"], row["priority"]
    conn.row_factory = sqlite3.Row

    return conn


def create_tables(conn):
    """
    Create the database schema (table structure) if it doesn't already exist.
    SQL CREATE TABLE IF NOT EXISTS is idempotent — safe to run multiple times.
    """
    # cursor() creates an object to execute SQL commands
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            priority    TEXT    DEFAULT 'medium',
            done        INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now')),
            done_at     TEXT
        )
    """)
    # INTEGER PRIMARY KEY AUTOINCREMENT: auto-generates unique IDs (1, 2, 3...)
    # TEXT NOT NULL: title is required (cannot be empty)
    # done INTEGER: SQLite has no boolean type — use 0=false, 1=true

    conn.commit()  # save the schema change to disk


def add_todo(conn, title, priority="medium"):
    """Insert a new todo into the database using a parameterized query."""
    # Use ? placeholders instead of f-strings to prevent SQL injection attacks!
    # SQL injection: if title = "'; DROP TABLE todos; --" it would destroy data
    conn.execute(
        "INSERT INTO todos (title, priority) VALUES (?, ?)",
        (title, priority)
    )
    conn.commit()

    # Get the ID of the row we just inserted
    row = conn.execute("SELECT last_insert_rowid()").fetchone()
    new_id = row[0]
    print(f"Added [{new_id}]: {title} ({priority} priority)")


def list_todos(conn, show_done=False):
    """
    Query and display todos from the database.
    ORDER BY sorts: pending first (done=0), then by priority, then by date.
    """
    # SQL query with conditional WHERE clause
    if show_done:
        query = "SELECT * FROM todos ORDER BY done ASC, created_at DESC"
    else:
        query = "SELECT * FROM todos WHERE done = 0 ORDER BY created_at DESC"

    rows = conn.execute(query).fetchall()  # fetchall() returns all matching rows

    if not rows:
        print("No todos found!" + (" (all done?)" if not show_done else ""))
        return

    PRIORITY_ICON = {"high": "●", "medium": "◑", "low": "○"}

    print(f"\n  Todo List ({len(rows)} items):")
    print(f"  {'ID':>4}  {'ST':>2}  {'PRI':>3}  {'TITLE':<35} {'CREATED'}")
    print("  " + "-" * 65)

    for row in rows:
        status   = "✓" if row["done"] else PRIORITY_ICON.get(row["priority"], "○")
        created  = row["created_at"][:10]  # just the date part
        done_mark= " ← DONE" if row["done"] else ""
        print(f"  {row['id']:>4}  {status:>2}  {row['priority'][:3]:>3}  "
              f"{row['title']:<35} {created}{done_mark}")


def mark_done(conn, todo_id):
    """Mark a todo as complete and record when it was done."""
    done_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # UPDATE modifies existing rows that match the WHERE condition
    result = conn.execute(
        "UPDATE todos SET done = 1, done_at = ? WHERE id = ? AND done = 0",
        (done_time, todo_id)
    )
    conn.commit()

    # rowcount tells us how many rows were actually updated
    if result.rowcount > 0:
        print(f"Marked todo #{todo_id} as done!")
    else:
        print(f"Todo #{todo_id} not found or already done.")


def delete_todo(conn, todo_id):
    """Permanently delete a todo from the database."""
    result = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()

    if result.rowcount > 0:
        print(f"Deleted todo #{todo_id}")
    else:
        print(f"Todo #{todo_id} not found")


def search_todos(conn, keyword):
    """Search todos by keyword using SQL LIKE pattern matching."""
    # % is a wildcard in SQL: '%keyword%' matches any string containing keyword
    pattern = f"%{keyword}%"

    rows = conn.execute(
        "SELECT * FROM todos WHERE title LIKE ? ORDER BY created_at DESC",
        (pattern,)
    ).fetchall()

    print(f"\nSearch results for '{keyword}': {len(rows)} found")
    for row in rows:
        status = "✓" if row["done"] else "○"
        print(f"  [{row['id']}] {status} {row['title']} ({row['priority']})")


def show_stats(conn):
    """Display statistics about todos using SQL aggregate functions."""
    print("\n  Todo Statistics:")

    # COUNT(*) counts all rows
    total = conn.execute("SELECT COUNT(*) FROM todos").fetchone()[0]
    done  = conn.execute("SELECT COUNT(*) FROM todos WHERE done = 1").fetchone()[0]
    pending = total - done

    print(f"    Total todos  : {total}")
    print(f"    Completed    : {done}")
    print(f"    Pending      : {pending}")
    print(f"    Completion   : {done/total*100:.0f}%" if total else "    No data yet")

    # GROUP BY counts todos per priority level
    print("\n  By Priority:")
    rows = conn.execute(
        "SELECT priority, COUNT(*) as count FROM todos WHERE done=0 GROUP BY priority"
    ).fetchall()
    for row in rows:
        print(f"    {row['priority']:<8} : {row['count']}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Todo list with SQLite database")
subparsers = parser.add_subparsers(dest="command")

add_p = subparsers.add_parser("add", help="Add a todo")
add_p.add_argument("title", help="Todo text")
add_p.add_argument("--priority", choices=["low","medium","high"], default="medium")

list_p = subparsers.add_parser("list", help="List todos")
list_p.add_argument("--all", action="store_true", help="Include completed todos")

done_p = subparsers.add_parser("done", help="Mark as done")
done_p.add_argument("id", type=int)

del_p = subparsers.add_parser("delete", help="Delete a todo")
del_p.add_argument("id", type=int)

search_p = subparsers.add_parser("search", help="Search todos")
search_p.add_argument("keyword")

subparsers.add_parser("stats", help="Show statistics")
args = parser.parse_args()

# Connect and ensure tables exist
conn = get_connection()
create_tables(conn)

if args.command == "add":
    add_todo(conn, args.title, args.priority)
elif args.command == "list":
    list_todos(conn, show_done=vars(args).get("all", False))
elif args.command == "done":
    mark_done(conn, args.id)
elif args.command == "delete":
    delete_todo(conn, args.id)
elif args.command == "search":
    search_todos(conn, args.keyword)
elif args.command == "stats":
    show_stats(conn)
else:
    # Default: show pending todos
    list_todos(conn)

conn.close()  # always close the database connection when done
