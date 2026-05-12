"""
Project: Expense Tracker
What it does: Tracks your income and expenses, categorizes them, and
generates a monthly budget report. Stores data in a JSON file.

Categories: Food, Transport, Rent, Entertainment, Shopping, Health, Other

Run: python 23_expense_tracker.py add --amount 45.50 --category Food --note "Lunch"
Run: python 23_expense_tracker.py add --amount 2000 --category Rent --type income
Run: python 23_expense_tracker.py report
Run: python 23_expense_tracker.py list
"""

import json
import os
import argparse
from datetime import datetime
from collections import defaultdict

DATA_FILE = "expenses.json"

# Default budget limits per category per month (customize as needed)
BUDGET_LIMITS = {
    "Food":          600,
    "Transport":     200,
    "Rent":         1500,
    "Entertainment": 150,
    "Shopping":      300,
    "Health":        100,
    "Other":         200,
}


def load_data():
    """Load existing transactions from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Default structure with an empty transactions list
    return {"transactions": []}


def save_data(data):
    """Save all transactions to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_transaction(amount, category, trans_type, note=""):
    """
    Add a new income or expense transaction.
    trans_type: "expense" or "income"
    """
    data = load_data()

    # Build the transaction record
    transaction = {
        "id":       len(data["transactions"]) + 1,
        "date":     datetime.now().strftime("%Y-%m-%d"),
        "amount":   float(amount),
        "category": category,
        "type":     trans_type,       # "expense" or "income"
        "note":     note,
    }

    data["transactions"].append(transaction)
    save_data(data)

    sign = "-" if trans_type == "expense" else "+"
    print(f"Added: {sign}${amount:.2f}  [{category}]  {note}")


def get_monthly_report(year=None, month=None):
    """
    Generate a monthly budget report showing spending vs. budget by category.
    Defaults to the current month.
    """
    data = load_data()

    if year is None:
        year  = datetime.now().year
    if month is None:
        month = datetime.now().month

    # Filter transactions for the target month
    month_str  = f"{year}-{month:02d}"   # e.g. "2024-01"
    month_trans = [
        t for t in data["transactions"]
        if t["date"].startswith(month_str)   # date starts with "2024-01"
    ]

    if not month_trans:
        print(f"No transactions found for {month_str}")
        return

    # Separate income and expenses
    income_trans  = [t for t in month_trans if t["type"] == "income"]
    expense_trans = [t for t in month_trans if t["type"] == "expense"]

    total_income  = sum(t["amount"] for t in income_trans)
    total_expense = sum(t["amount"] for t in expense_trans)
    net_balance   = total_income - total_expense

    # Group expenses by category
    by_category = defaultdict(float)
    for t in expense_trans:
        by_category[t["category"]] += t["amount"]

    # ── Print report ─────────────────────────────────────────────────────────
    GREEN = "\033[92m"
    RED   = "\033[91m"
    YEL   = "\033[33m"
    RST   = "\033[0m"

    print(f"\n{'='*60}")
    print(f"  BUDGET REPORT — {year}-{month:02d}")
    print(f"{'='*60}")
    print(f"\n  Total Income  : {GREEN}+${total_income:>10,.2f}{RST}")
    print(f"  Total Expenses: {RED}-${total_expense:>10,.2f}{RST}")
    net_color = GREEN if net_balance >= 0 else RED
    print(f"  Net Balance   : {net_color}${net_balance:>+10,.2f}{RST}")

    print(f"\n  Expenses by Category:")
    print(f"  {'CATEGORY':<15} {'SPENT':>10} {'BUDGET':>10} {'REMAINING':>12}  {'BAR'}")
    print("  " + "-" * 65)

    for category, limit in BUDGET_LIMITS.items():
        spent     = by_category.get(category, 0.0)
        remaining = limit - spent
        pct       = spent / limit * 100 if limit > 0 else 0

        # Color: green if under budget, yellow if near limit, red if over
        if pct > 100:    color = RED
        elif pct > 80:   color = YEL
        else:            color = GREEN

        # Visual bar (max 20 chars)
        bar_filled = min(int(pct / 5), 20)   # 100% = 20 blocks
        bar = "█" * bar_filled + "░" * (20 - bar_filled)

        print(f"  {category:<15} {spent:>10,.2f} {limit:>10,.2f} "
              f"{color}{remaining:>+12,.2f}{RST}  {color}{bar}{RST} {pct:.0f}%")

    # "Other" categories not in BUDGET_LIMITS
    unlisted = set(by_category) - set(BUDGET_LIMITS)
    for cat in unlisted:
        spent = by_category[cat]
        print(f"  {cat:<15} {spent:>10,.2f} {'N/A':>10}  (no budget set)")


def list_transactions(limit=10):
    """Show recent transactions."""
    data = load_data()
    trans = data["transactions"]

    if not trans:
        print("No transactions yet.")
        return

    # Show most recent first
    recent = trans[-limit:][::-1]  # last N items, reversed

    print(f"\n  Recent Transactions (last {len(recent)}):")
    print(f"  {'ID':>4}  {'DATE':<12} {'TYPE':>8}  {'AMOUNT':>10}  {'CATEGORY':<15} NOTE")
    print("  " + "-" * 65)

    for t in recent:
        sign    = "-" if t["type"] == "expense" else "+"
        amount  = f"{sign}${t['amount']:,.2f}"
        print(f"  {t['id']:>4}  {t['date']:<12} {t['type']:>8}  {amount:>10}  "
              f"{t['category']:<15} {t.get('note','')[:20]}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Personal expense tracker")
subparsers = parser.add_subparsers(dest="command")

add_p = subparsers.add_parser("add", help="Add a transaction")
add_p.add_argument("--amount",   type=float, required=True)
add_p.add_argument("--category", default="Other",
                   choices=list(BUDGET_LIMITS.keys()) + ["Other"])
add_p.add_argument("--type",     dest="trans_type",
                   choices=["expense","income"], default="expense")
add_p.add_argument("--note",     default="")

subparsers.add_parser("report", help="Monthly budget report")
subparsers.add_parser("list",   help="List recent transactions")
args = parser.parse_args()

print("=== Expense Tracker ===")

# Add some demo data if the file doesn't exist yet
if not os.path.exists(DATA_FILE):
    print("Adding sample transactions for demo...\n")
    demo = [
        (2000, "Rent", "expense", "Monthly rent"),
        (3500, "Salary", "income", "Monthly salary"),
        (85, "Food", "expense", "Weekly groceries"),
        (45, "Transport", "expense", "Monthly bus pass"),
        (120, "Food", "expense", "Restaurant dinner"),
        (50, "Entertainment", "expense", "Netflix + Spotify"),
        (35, "Food", "expense", "Coffee shop"),
        (200, "Shopping", "expense", "New shoes"),
    ]
    for amount, cat, ttype, note in demo:
        add_transaction(amount, cat, ttype, note)

if args.command == "add":
    add_transaction(args.amount, args.category, args.trans_type, args.note)
elif args.command == "report":
    get_monthly_report()
elif args.command == "list":
    list_transactions()
else:
    get_monthly_report()
    list_transactions()

# Clean up demo data
if os.path.exists(DATA_FILE):
    os.remove(DATA_FILE)
