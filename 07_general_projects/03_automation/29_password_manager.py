"""
Project: Simple Password Manager (Educational)
What it does: Stores passwords encrypted with a master password.
Demonstrates symmetric encryption concepts using a key derived from
the master password. For real use, consider KeePass or Bitwarden.

How it works:
  1. Master password → key (via PBKDF2 key derivation)
  2. Key → encrypt/decrypt stored passwords (XOR cipher for simplicity)
  3. Everything stored in an encrypted JSON file

Note: This uses a simple XOR cipher for educational purposes.
Real password managers use AES-256 encryption.

Run: python 29_password_manager.py  (demo mode)
"""

import json
import os
import hashlib
import base64    # for encoding binary data as text
import argparse
import getpass   # for reading passwords without showing them on screen
from datetime import datetime


VAULT_FILE = "password_vault.json"


def derive_key(master_password, salt):
    """
    Derive a cryptographic key from the master password.
    Uses PBKDF2 (Password-Based Key Derivation Function 2).

    Why not just use the password directly?
    - PBKDF2 adds 'stretching' — runs thousands of iterations to slow down attacks
    - salt prevents two same passwords from having the same key (rainbow table defense)
    - The output is always a fixed-length bytes object

    iterations=100000 means the hash is computed 100,000 times — very slow to brute-force
    """
    key = hashlib.pbkdf2_hmac(
        "sha256",                             # hash algorithm
        master_password.encode("utf-8"),      # password as bytes
        salt.encode("utf-8"),                 # salt as bytes
        iterations=100_000,                   # number of iterations
        dklen=32                              # output key length in bytes
    )
    return key


def xor_encrypt_decrypt(data_bytes, key_bytes):
    """
    XOR cipher: encrypt or decrypt bytes using a key.
    XOR is its own inverse: encrypt(encrypt(data)) = data.
    So the same function works for both encryption and decryption.

    XOR (^) operation:
        0 ^ 0 = 0
        0 ^ 1 = 1
        1 ^ 0 = 1
        1 ^ 1 = 0
    """
    # Extend key to match data length by repeating it (key cycling)
    key_extended = (key_bytes * (len(data_bytes) // len(key_bytes) + 1))[:len(data_bytes)]

    # XOR each byte of data with the corresponding key byte
    result = bytes(d ^ k for d, k in zip(data_bytes, key_extended))
    return result


def encrypt_password(password, key):
    """Encrypt a password string and return a base64-encoded string."""
    password_bytes   = password.encode("utf-8")
    encrypted_bytes  = xor_encrypt_decrypt(password_bytes, key)
    # base64 encoding converts binary bytes to safe ASCII text for storage
    return base64.b64encode(encrypted_bytes).decode("utf-8")


def decrypt_password(encrypted_b64, key):
    """Decrypt a base64-encoded encrypted password back to plain text."""
    encrypted_bytes  = base64.b64decode(encrypted_b64.encode("utf-8"))
    decrypted_bytes  = xor_encrypt_decrypt(encrypted_bytes, key)
    return decrypted_bytes.decode("utf-8")


def load_vault():
    """Load the password vault from disk."""
    if os.path.exists(VAULT_FILE):
        with open(VAULT_FILE) as f:
            return json.load(f)
    # Initialize a new vault with a random salt
    import secrets
    return {
        "salt":     secrets.token_hex(16),  # 16 random bytes as hex string
        "entries":  []
    }


def save_vault(vault):
    with open(VAULT_FILE, "w") as f:
        json.dump(vault, f, indent=2)


def add_entry(vault, key, site, username, password, notes=""):
    """Add a new password entry to the vault."""
    # Encrypt the password before storing
    encrypted = encrypt_password(password, key)

    entry = {
        "id":        len(vault["entries"]) + 1,
        "site":      site,
        "username":  username,
        "encrypted": encrypted,   # stored encrypted — never plain text!
        "notes":     notes,
        "added":     datetime.now().strftime("%Y-%m-%d"),
    }

    vault["entries"].append(entry)
    save_vault(vault)
    print(f"✓ Stored credentials for: {site}")


def list_entries(vault, key=None, reveal=False):
    """List all stored entries (optionally with decrypted passwords)."""
    entries = vault["entries"]

    if not entries:
        print("Vault is empty.")
        return

    print(f"\n  Stored Credentials ({len(entries)} entries):")
    print(f"  {'ID':>4}  {'SITE':<25}  {'USERNAME':<20}  {'PASSWORD':<20}  ADDED")
    print("  " + "─" * 80)

    for entry in entries:
        if reveal and key:
            password = decrypt_password(entry["encrypted"], key)
        else:
            password = "••••••••"  # mask the password

        print(f"  {entry['id']:>4}  {entry['site']:<25}  {entry['username']:<20}  "
              f"{password:<20}  {entry['added']}")


def get_password(vault, key, entry_id):
    """Retrieve and decrypt a specific password."""
    entry = next((e for e in vault["entries"] if e["id"] == entry_id), None)

    if not entry:
        print(f"Entry #{entry_id} not found.")
        return

    password = decrypt_password(entry["encrypted"], key)
    print(f"\n  Site     : {entry['site']}")
    print(f"  Username : {entry['username']}")
    print(f"  Password : {password}")  # Now decrypted
    if entry.get("notes"):
        print(f"  Notes    : {entry['notes']}")


def generate_password(length=16):
    """Generate a strong random password."""
    import secrets
    import string

    # Character pool: letters + digits + symbols
    chars = string.ascii_letters + string.digits + "!@#$%^&*"

    # secrets.choice() is cryptographically secure (better than random.choice)
    return "".join(secrets.choice(chars) for _ in range(length))


# ── Demo ─────────────────────────────────────────────────────────────────────
print("=== Password Manager (Educational Demo) ===\n")
print("NOTE: This uses XOR cipher for demonstration. Use KeePass for real passwords.\n")

# Use a fixed demo master password
demo_master = "demo_master_password_123"
vault = load_vault()
key   = derive_key(demo_master, vault["salt"])

print(f"Demo master password: '{demo_master}'")
print(f"Derived key (first 16 bytes): {key[:8].hex()}...\n")

# Add some demo entries
add_entry(vault, key, "github.com",    "alice@example.com",  "my_github_pass!", "Work account")
add_entry(vault, key, "gmail.com",     "alice@gmail.com",    generate_password(), "Personal email")
add_entry(vault, key, "amazon.com",    "alice@example.com",  generate_password(), "Shopping")

print()
print("--- Listing entries (passwords hidden) ---")
list_entries(vault, key, reveal=False)

print("\n--- Listing with revealed passwords ---")
list_entries(vault, key, reveal=True)

print("\n--- Getting specific entry ---")
get_password(vault, key, 1)

print(f"\n--- Generated strong password example ---")
print(f"  {generate_password(20)}")

# Clean up
if os.path.exists(VAULT_FILE):
    os.remove(VAULT_FILE)
print("\n(Demo vault cleaned up)")
