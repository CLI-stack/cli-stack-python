"""
Script: Colored Terminal Output
What it does: Adds colors and formatting to terminal text.
Makes CLI tools much easier to read — errors in red, success in green, etc.

Install: pip install colorama (for Windows compatibility)
"""

# --- Method 1: ANSI escape codes (works on Linux/Mac) ---
# These are special codes that terminal apps recognize

COLORS = {
    "red":     "\033[31m",
    "green":   "\033[32m",
    "yellow":  "\033[33m",
    "blue":    "\033[34m",
    "magenta": "\033[35m",
    "cyan":    "\033[36m",
    "white":   "\033[37m",
    "reset":   "\033[0m",   # resets color back to default
}

STYLES = {
    "bold":      "\033[1m",
    "underline": "\033[4m",
    "blink":     "\033[5m",
}

def colorize(text, color, style=None):
    """Wrap text with color and optional style codes."""
    code = COLORS.get(color, "")
    style_code = STYLES.get(style, "") if style else ""
    return f"{style_code}{code}{text}{COLORS['reset']}"

# --- Display examples ---
print(colorize("=== Colored Terminal Output ===", "cyan", "bold"))
print()

# Log level messages (common use case)
print(colorize("[ERROR]   ", "red", "bold") + "Database connection failed")
print(colorize("[WARNING] ", "yellow", "bold") + "Disk usage is at 85%")
print(colorize("[INFO]    ", "cyan") + "Server started on port 5000")
print(colorize("[SUCCESS] ", "green", "bold") + "Backup completed successfully!")
print()

# Colored data display
print(colorize("System Status", "white", "underline"))
print(f"  CPU Usage:    " + colorize("78%", "yellow"))
print(f"  Memory:       " + colorize("45%", "green"))
print(f"  Disk:         " + colorize("92%", "red", "bold") + " ← WARNING")
print()

# --- Method 2: colorama (cross-platform, works on Windows too) ---
try:
    from colorama import Fore, Back, Style, init
    init()  # initialize colorama (required for Windows)

    print(colorize("=== Colorama Library ===", "magenta", "bold"))
    print(Fore.RED + "This is red text" + Style.RESET_ALL)
    print(Fore.GREEN + Style.BRIGHT + "This is bright green" + Style.RESET_ALL)
    print(Back.BLUE + Fore.WHITE + " Blue background " + Style.RESET_ALL)

except ImportError:
    print(colorize("\ncolorama not installed (optional).", "yellow"))
    print("Install with: pip install colorama")
