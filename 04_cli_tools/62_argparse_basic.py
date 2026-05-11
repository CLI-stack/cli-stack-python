"""
Script: CLI with argparse (Command-Line Arguments)
What it does: Creates a professional CLI tool that accepts arguments.
Instead of asking questions interactively, the user passes arguments when running:
  python 62_argparse_basic.py --name Alice --age 30 --greet

Run: python 62_argparse_basic.py --help
Run: python 62_argparse_basic.py --name Bob --age 25
"""

import argparse  # built-in module for parsing command-line arguments

# Create the argument parser with a description
parser = argparse.ArgumentParser(
    description="A greeting tool that demonstrates argparse",
    formatter_class=argparse.RawDescriptionHelpFormatter
)

# --- Add arguments ---
# Positional argument (required, no -- prefix)
parser.add_argument("username", help="Your username")

# Optional argument with -- prefix
parser.add_argument("--name", help="Your full name", default="Friend")
parser.add_argument("--age", type=int, help="Your age (must be a number)")

# Flag argument (True if present, False if not)
parser.add_argument("--greet", action="store_true", help="Show a greeting")
parser.add_argument("--shout", action="store_true", help="UPPERCASE output")

# Choice argument (only allows specific values)
parser.add_argument(
    "--language",
    choices=["python", "javascript", "rust"],
    default="python",
    help="Your favorite language"
)

# --- Parse the arguments ---
args = parser.parse_args()

# --- Use the arguments ---
message = f"User: {args.username}"
if args.name:
    message += f" | Name: {args.name}"
if args.age:
    message += f" | Age: {args.age}"
message += f" | Language: {args.language}"

if args.shout:
    message = message.upper()

if args.greet:
    print(f"Hello, {args.name}! Welcome!")

print(message)

if args.age and args.age < 18:
    print("Note: You are under 18.")
elif args.age and args.age >= 65:
    print("Note: Senior discount available!")
