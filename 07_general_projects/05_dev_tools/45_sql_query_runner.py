"""
Project: Interactive SQLite Query Runner
What it does: Provides an interactive SQL shell for SQLite databases.
Type SQL queries and see results formatted as a table.
Includes query history, table explorer, and export to CSV.
Great for exploring data without needing a GUI tool.

Run: python 45_sql_query_runner.py  (opens an in-memory demo database)
Run: python 45_sql_query_runner.py --db mydb.sqlite
"""

import sqlite3   # built-in: SQLite database interface
import csv
import os
import argparse
import sys
from datetime import datetime


def create_demo_database(conn):
    """Create and populate a demo database with sample tables."""
    cursor = conn.cursor()

    # Create tables with SQL CREATE TABLE statements
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS employees (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            department TEXT,
            salary     REAL,
            hire_date  TEXT
        );

        CREATE TABLE IF NOT EXISTS departments (
            id   INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            budget REAL
        );

        CREATE TABLE IF NOT EXISTS projects (
            id      INTEGER PRIMARY KEY,
            name    TEXT,
            dept_id INTEGER,
            status  TEXT,
            FOREIGN KEY (dept_id) REFERENCES departments(id)
        );

        INSERT OR IGNORE INTO departments VALUES (1, 'Engineering', 500000);
        INSERT OR IGNORE INTO departments VALUES (2, 'Sales',       300000);
        INSERT OR IGNORE INTO departments VALUES (3, 'Marketing',   200000);

        INSERT OR IGNORE INTO employees VALUES (1, 'Alice',   'Engineering', 95000, '2021-01-15');
        INSERT OR IGNORE INTO employees VALUES (2, 'Bob',     'Sales',       75000, '2020-06-01');
        INSERT OR IGNORE INTO employees VALUES (3, 'Charlie', 'Engineering', 85000, '2022-03-20');
        INSERT OR IGNORE INTO employees VALUES (4, 'Diana',   'Marketing',   70000, '2019-09-10');
        INSERT OR IGNORE INTO employees VALUES (5, 'Eve',     'Engineering', 90000, '2021-11-05');

        INSERT OR IGNORE INTO projects VALUES (1, 'Project Alpha', 1, 'Active');
        INSERT OR IGNORE INTO projects VALUES (2, 'Project Beta',  2, 'Completed');
        INSERT OR IGNORE INTO projects VALUES (3, 'Project Gamma', 1, 'Active');
    """)
    conn.commit()
    print("Demo database created with tables: employees, departments, projects\n")


def execute_query(conn, query):
    """
    Execute a SQL query and return results.
    Returns (columns, rows, row_count, is_select)
    """
    cursor = conn.cursor()

    try:
        cursor.execute(query)

        # Determine if this is a SELECT query (returns rows) or a DML query (modifies data)
        query_upper = query.strip().upper()
        is_select   = any(query_upper.startswith(kw)
                          for kw in ("SELECT", "WITH", "EXPLAIN", "PRAGMA"))

        if is_select:
            rows    = cursor.fetchall()   # get all result rows
            columns = [d[0] for d in cursor.description]  # column names from cursor
            return columns, rows, len(rows), True

        else:
            conn.commit()   # save INSERT/UPDATE/DELETE changes
            return [], [], cursor.rowcount, False

    except sqlite3.Error as e:
        raise RuntimeError(f"SQL Error: {e}")


def format_table(columns, rows, max_width=20):
    """
    Format query results as an ASCII table.
    Automatically adjusts column widths to fit the data.
    """
    if not columns:
        return ""

    # Calculate column widths: max of column name length or max data length
    col_widths = [len(col) for col in columns]
    for row in rows:
        for i, value in enumerate(row):
            col_widths[i] = max(col_widths[i], min(len(str(value)), max_width))

    # Build separator line
    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    # Build header
    header = "|" + "|".join(f" {col:<{col_widths[i]}} " for i, col in enumerate(columns)) + "|"

    lines = [sep, header, sep]

    # Build data rows
    for row in rows:
        cells = []
        for i, value in enumerate(row):
            cell = str(value) if value is not None else "NULL"
            # Truncate long values
            if len(cell) > col_widths[i]:
                cell = cell[:col_widths[i]-3] + "..."
            cells.append(f" {cell:<{col_widths[i]}} ")
        lines.append("|" + "|".join(cells) + "|")

    lines.append(sep)
    return "\n".join(lines)


def list_tables(conn):
    """Show all tables in the database."""
    columns, rows, _, _ = execute_query(
        conn, "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"
    )
    print(f"\n  Tables in database:")
    for (name, type_) in rows:
        print(f"    {type_}: {name}")


def describe_table(conn, table_name):
    """Show the structure of a table (column names, types, constraints)."""
    columns, rows, _, _ = execute_query(conn, f"PRAGMA table_info({table_name})")
    print(f"\n  Table: {table_name}")
    print(format_table(["col", "name", "type", "not_null", "default", "pk"], rows))


def export_to_csv(columns, rows, filename):
    """Export query results to a CSV file."""
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print(f"\n  Exported {len(rows)} rows to: {filename}")


def run_interactive_shell(conn):
    """
    Interactive SQL REPL (Read-Eval-Print Loop).
    User types SQL queries and sees formatted results.
    """
    history = []  # query history for this session

    print("SQLite Interactive Shell")
    print("Commands: .tables  .describe <table>  .export <file>  .history  .quit")
    print("Type SQL queries followed by Enter.\n")

    # Show sample queries for beginners
    sample_queries = [
        "SELECT * FROM employees;",
        "SELECT name, salary FROM employees WHERE salary > 80000;",
        "SELECT dept.name, AVG(emp.salary) FROM employees emp JOIN departments dept ON emp.department = dept.name GROUP BY dept.name;",
    ]
    print("  Sample queries to try:")
    for q in sample_queries:
        print(f"    {q}")
    print()

    last_result = ([], [])   # store last query result for export

    while True:
        try:
            # Read input (handle multi-line queries ending with ;)
            query_lines = []
            while True:
                prompt = "sql> " if not query_lines else "  -> "
                try:
                    line = input(prompt)
                except EOFError:
                    return  # exit on EOF

                if not line.strip():
                    continue

                query_lines.append(line)

                # Check for special commands (start with .)
                full_input = " ".join(query_lines).strip()

                if full_input.lower() == ".quit" or full_input.lower() == ".exit":
                    print("Goodbye!")
                    return

                elif full_input.lower() == ".tables":
                    list_tables(conn)
                    query_lines = []
                    break

                elif full_input.lower().startswith(".describe "):
                    table = full_input.split()[1]
                    describe_table(conn, table)
                    query_lines = []
                    break

                elif full_input.lower().startswith(".export "):
                    filename = full_input.split()[1]
                    if last_result[0]:
                        export_to_csv(*last_result, filename)
                    else:
                        print("No results to export. Run a SELECT query first.")
                    query_lines = []
                    break

                elif full_input.lower() == ".history":
                    for i, q in enumerate(history[-10:], 1):
                        print(f"  {i}: {q}")
                    query_lines = []
                    break

                # SQL queries end with ;
                if full_input.rstrip().endswith(";"):
                    query = full_input.rstrip().rstrip(";")
                    history.append(query)

                    start_time = datetime.now()
                    columns, rows, count, is_select = execute_query(conn, query)
                    elapsed    = (datetime.now() - start_time).total_seconds() * 1000

                    if is_select:
                        last_result = (columns, rows)
                        table_str   = format_table(columns, rows)
                        print(f"\n{table_str}")
                        print(f"  {count} row(s) returned in {elapsed:.1f}ms")
                    else:
                        print(f"  OK — {count} row(s) affected in {elapsed:.1f}ms")

                    query_lines = []
                    break

        except RuntimeError as e:
            print(f"  Error: {e}")
            query_lines = []


def run_demo(conn):
    """Run a series of demo queries to show capabilities."""
    demo_queries = [
        ("All employees", "SELECT * FROM employees"),
        ("High earners", "SELECT name, salary FROM employees WHERE salary > 80000"),
        ("Avg salary by dept", "SELECT department, AVG(salary) as avg_salary, COUNT(*) as count FROM employees GROUP BY department"),
        ("Employees + dept budget", "SELECT e.name, e.salary, d.budget FROM employees e JOIN departments d ON e.department = d.name ORDER BY e.salary DESC"),
    ]

    print("Running demo queries:\n")
    for label, query in demo_queries:
        print(f"  >>> {label}")
        print(f"  SQL: {query}")
        columns, rows, count, _ = execute_query(conn, query)
        print(format_table(columns, rows))
        print(f"  ({count} rows)\n")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Interactive SQLite query runner")
parser.add_argument("--db",          help="SQLite database file (default: in-memory)")
parser.add_argument("--interactive", action="store_true", help="Start interactive shell")
args = parser.parse_args()

print("=== SQLite Query Runner ===\n")

# Open or create the database
if args.db:
    conn = sqlite3.connect(args.db)
    print(f"Connected to: {args.db}")
else:
    conn = sqlite3.connect(":memory:")  # in-memory database (lives only while running)
    print("Connected to: in-memory database")
    create_demo_database(conn)

if args.interactive:
    run_interactive_shell(conn)
else:
    run_demo(conn)

conn.close()
