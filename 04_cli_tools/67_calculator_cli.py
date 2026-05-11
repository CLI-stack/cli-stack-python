"""
Script: Calculator CLI
What it does: A command-line calculator that evaluates math expressions.
Supports both interactive mode and single expressions via arguments.

Run interactively: python 67_calculator_cli.py
Run single expression: python 67_calculator_cli.py "2 + 3 * 4"
"""

import argparse
import math
import operator

# Map of supported operators
OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,  # integer division
    "%": operator.mod,        # remainder
    "**": operator.pow,       # power
}

# Available math functions
MATH_FUNCTIONS = {
    "sqrt":  math.sqrt,    # square root
    "abs":   abs,          # absolute value
    "ceil":  math.ceil,    # round up
    "floor": math.floor,   # round down
    "log":   math.log,     # natural logarithm
    "log10": math.log10,   # base-10 logarithm
    "sin":   math.sin,     # sine
    "cos":   math.cos,     # cosine
    "pi":    math.pi,      # π constant
    "e":     math.e,       # Euler's number
}

def safe_eval(expression):
    """Safely evaluate a math expression using only allowed functions."""
    try:
        # Allow only safe builtins + math functions
        allowed = {**MATH_FUNCTIONS, "__builtins__": {}}
        result = eval(expression, {"__builtins__": {}}, {**MATH_FUNCTIONS})
        return result
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {e}"

# --- Check for command-line argument ---
parser = argparse.ArgumentParser(description="Command-line calculator")
parser.add_argument("expression", nargs="?", help="Math expression to evaluate")
args = parser.parse_args()

if args.expression:
    # Single expression mode
    result = safe_eval(args.expression)
    print(f"{args.expression} = {result}")
else:
    # Interactive mode
    print("=== Python Calculator ===")
    print("Supported: +, -, *, /, //, %, **")
    print("Functions: sqrt(), abs(), sin(), cos(), log(), ceil(), floor()")
    print("Constants: pi, e")
    print("Type 'exit' to quit\n")

    while True:
        try:
            expression = input("Enter expression: ").strip()
            if expression.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            if expression:
                result = safe_eval(expression)
                print(f"= {result}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
