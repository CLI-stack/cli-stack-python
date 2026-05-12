"""
Project: Random Quote Generator
What it does: Displays a random inspirational/programming quote.
Supports categories, searching by keyword, and adding your own quotes.
Can be added to your shell profile to show a quote every time you open a terminal.

Run: python 27_quote_generator.py
Run: python 27_quote_generator.py --category programming
Run: python 27_quote_generator.py --search "code"
Run: python 27_quote_generator.py --all
"""

import random
import argparse
import json
import os
import textwrap  # built-in: for wrapping long text to fit terminal width


# Built-in quote database
QUOTES = [
    {"text": "First, solve the problem. Then, write the code.",
     "author": "John Johnson",              "category": "programming"},
    {"text": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.",
     "author": "Martin Fowler",             "category": "programming"},
    {"text": "The best way to predict the future is to invent it.",
     "author": "Alan Kay",                  "category": "innovation"},
    {"text": "Code is like humor. When you have to explain it, it's bad.",
     "author": "Cory House",               "category": "programming"},
    {"text": "Simplicity is the soul of efficiency.",
     "author": "Austin Freeman",            "category": "programming"},
    {"text": "Before software can be reusable it first has to be usable.",
     "author": "Ralph Johnson",             "category": "programming"},
    {"text": "The only way to do great work is to love what you do.",
     "author": "Steve Jobs",               "category": "motivation"},
    {"text": "In the middle of difficulty lies opportunity.",
     "author": "Albert Einstein",           "category": "motivation"},
    {"text": "It does not matter how slowly you go as long as you do not stop.",
     "author": "Confucius",                "category": "motivation"},
    {"text": "Programs must be written for people to read, and only incidentally for machines to execute.",
     "author": "Harold Abelson",            "category": "programming"},
    {"text": "The function of good software is to make the complex appear simple.",
     "author": "Grady Booch",              "category": "programming"},
    {"text": "Learning never exhausts the mind.",
     "author": "Leonardo da Vinci",         "category": "learning"},
    {"text": "Tell me and I forget. Teach me and I remember. Involve me and I learn.",
     "author": "Benjamin Franklin",         "category": "learning"},
    {"text": "The beautiful thing about learning is that no one can take it away from you.",
     "author": "B.B. King",               "category": "learning"},
    {"text": "Talk is cheap. Show me the code.",
     "author": "Linus Torvalds",           "category": "programming"},
    {"text": "Debugging is twice as hard as writing the code in the first place.",
     "author": "Brian Kernighan",          "category": "programming"},
    {"text": "The most disastrous thing that you can ever learn is your first programming language.",
     "author": "Alan Kay",                 "category": "learning"},
    {"text": "Everybody should learn to program a computer because it teaches you how to think.",
     "author": "Steve Jobs",              "category": "programming"},
    {"text": "Stay hungry, stay foolish.",
     "author": "Steve Jobs",              "category": "motivation"},
    {"text": "The secret of getting ahead is getting started.",
     "author": "Mark Twain",              "category": "motivation"},
]

# Custom quotes file (users can add their own)
CUSTOM_FILE = "my_quotes.json"


def load_custom_quotes():
    """Load user-added custom quotes from disk."""
    if os.path.exists(CUSTOM_FILE):
        with open(CUSTOM_FILE) as f:
            return json.load(f)
    return []


def display_quote(quote, width=60):
    """
    Display a single quote in a nicely formatted box.
    textwrap.fill() wraps long text to fit within 'width' characters.
    """
    GREEN = "\033[92m"
    CYAN  = "\033[36m"
    BOLD  = "\033[1m"
    RST   = "\033[0m"
    ITALIC= "\033[3m"

    # Wrap the quote text to fit within the box width
    wrapped = textwrap.fill(quote["text"], width=width - 4)
    lines   = wrapped.split("\n")

    # Top border
    print(f"\n  {'─'*width}")

    # Quote text (with left indent)
    for line in lines:
        print(f"  │  {BOLD}{ITALIC}{line}{RST}")

    # Attribution
    print(f"  │")
    print(f"  │      {CYAN}— {quote['author']}{RST}")

    # Category tag
    category = quote.get("category", "general")
    print(f"  │      {GREEN}#{category}{RST}")

    # Bottom border
    print(f"  {'─'*width}\n")


def get_random_quote(category=None, all_quotes=None):
    """
    Get a random quote from the database.
    If category is specified, only return quotes from that category.
    """
    if all_quotes is None:
        all_quotes = QUOTES + load_custom_quotes()

    if category:
        filtered = [q for q in all_quotes if q.get("category", "").lower() == category.lower()]
        if not filtered:
            print(f"No quotes found for category '{category}'")
            available = set(q.get("category","") for q in all_quotes)
            print(f"Available categories: {', '.join(sorted(available))}")
            return None
        return random.choice(filtered)  # random.choice() picks one randomly

    return random.choice(all_quotes)


def search_quotes(keyword, all_quotes):
    """Find all quotes containing a keyword (case-insensitive)."""
    keyword = keyword.lower()
    matches = [q for q in all_quotes
               if keyword in q["text"].lower() or keyword in q["author"].lower()]
    return matches


def add_custom_quote(text, author, category="general"):
    """Add a new quote to the custom quotes file."""
    custom  = load_custom_quotes()
    new_quote = {"text": text, "author": author, "category": category}
    custom.append(new_quote)

    with open(CUSTOM_FILE, "w") as f:
        json.dump(custom, f, indent=2)

    print(f"Added quote by {author} to your collection!")


def show_stats(all_quotes):
    """Show statistics about the quote database."""
    from collections import Counter
    categories = Counter(q.get("category","?") for q in all_quotes)

    print(f"\n  Quote Database Stats:")
    print(f"  Total quotes: {len(all_quotes)}")
    print(f"\n  By category:")
    for cat, count in categories.most_common():
        bar = "█" * count
        print(f"    {cat:<15} {count:>3}  {bar}")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Random quote generator")
parser.add_argument("--category", help="Filter by category (programming/motivation/learning)")
parser.add_argument("--search",   help="Search quotes by keyword")
parser.add_argument("--all",      action="store_true", help="Show all quotes")
parser.add_argument("--stats",    action="store_true", help="Show database statistics")
parser.add_argument("--add",      nargs=3, metavar=("TEXT", "AUTHOR", "CATEGORY"),
                    help='Add your own quote: --add "Quote text" "Author" "category"')
args = parser.parse_args()

all_quotes = QUOTES + load_custom_quotes()

print("=== Quote Generator ===")

if args.add:
    add_custom_quote(args.add[0], args.add[1], args.add[2])

elif args.stats:
    show_stats(all_quotes)

elif args.search:
    matches = search_quotes(args.search, all_quotes)
    print(f"\nFound {len(matches)} quote(s) for '{args.search}':")
    for q in matches:
        display_quote(q)

elif args.all:
    print(f"\nAll {len(all_quotes)} quotes:\n")
    for q in all_quotes:
        display_quote(q)

else:
    # Show a single random quote (the default)
    quote = get_random_quote(category=args.category, all_quotes=all_quotes)
    if quote:
        display_quote(quote)

# Clean up demo
if os.path.exists(CUSTOM_FILE):
    os.remove(CUSTOM_FILE)
