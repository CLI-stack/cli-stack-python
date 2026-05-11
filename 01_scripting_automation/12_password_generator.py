"""
Script: Password Generator
What it does: Generates random, strong passwords.
Uses the secrets module which is safer than random for security purposes.
"""

import secrets   # cryptographically secure random number generator
import string    # provides character sets (letters, digits, symbols)

# Define character sets
letters = string.ascii_letters   # a-z and A-Z
digits = string.digits            # 0-9
symbols = string.punctuation      # !, @, #, $, etc.

# Combine all characters into one pool
all_characters = letters + digits + symbols
print(f"Character pool size: {len(all_characters)} characters")

# --- Generate a simple password ---
def generate_password(length=12):
    """Generate a random password of given length."""
    # secrets.choice() picks a random character from the pool
    password = "".join(secrets.choice(all_characters) for _ in range(length))
    return password

# --- Generate a stronger password (guaranteed to include each type) ---
def generate_strong_password(length=16):
    """Generate a password with at least one of each character type."""
    # Ensure at least one of each type
    mandatory = [
        secrets.choice(letters),   # at least one letter
        secrets.choice(digits),    # at least one digit
        secrets.choice(symbols),   # at least one symbol
    ]
    # Fill the rest randomly
    rest = [secrets.choice(all_characters) for _ in range(length - 3)]
    all_chars = mandatory + rest

    # Shuffle so the mandatory chars aren't always at the start
    secrets.SystemRandom().shuffle(all_chars)
    return "".join(all_chars)

# --- Generate a PIN (numbers only) ---
def generate_pin(length=6):
    """Generate a numeric PIN."""
    return "".join(secrets.choice(digits) for _ in range(length))

# Generate and display passwords
print("\n=== Generated Passwords ===")
for i in range(3):
    print(f"Password {i+1} (12 chars):  {generate_password(12)}")

print("\n=== Strong Passwords (16 chars) ===")
for i in range(3):
    print(f"Strong {i+1}: {generate_strong_password(16)}")

print("\n=== PINs (6 digits) ===")
for i in range(3):
    print(f"PIN {i+1}: {generate_pin(6)}")
