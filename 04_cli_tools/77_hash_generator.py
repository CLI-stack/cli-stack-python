"""
Script: Hash Generator
What it does: Generates cryptographic hashes of text or files.
Hashes are one-way functions — you can verify data integrity
but cannot reverse a hash to get the original data.
Used for: passwords, file checksums, digital signatures.

Run: python 77_hash_generator.py --text "hello"
Run: python 77_hash_generator.py --file myfile.txt
"""

import hashlib  # built-in module for cryptographic hashing
import argparse
import os

def hash_text(text, algorithm="sha256"):
    """Hash a string using the specified algorithm."""
    text_bytes = text.encode("utf-8")  # convert string to bytes
    hasher = hashlib.new(algorithm)    # create the hasher
    hasher.update(text_bytes)          # feed data to hasher
    return hasher.hexdigest()          # get hex string result

def hash_file(filepath, algorithm="sha256"):
    """Hash a file's contents (reads in chunks to handle large files)."""
    hasher = hashlib.new(algorithm)
    chunk_size = 65536  # read 64KB at a time

    with open(filepath, "rb") as f:  # "rb" = read binary
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()

# --- Demo ---
parser = argparse.ArgumentParser(description="Generate cryptographic hashes")
parser.add_argument("--text", help="Hash a text string")
parser.add_argument("--file", help="Hash a file")
parser.add_argument("--algo", default="sha256",
                    choices=["md5", "sha1", "sha256", "sha512"],
                    help="Hash algorithm (default: sha256)")
args = parser.parse_args()

if args.text:
    result = hash_text(args.text, args.algo)
    print(f"Text:      {args.text}")
    print(f"Algorithm: {args.algo}")
    print(f"Hash:      {result}")

elif args.file:
    if os.path.exists(args.file):
        result = hash_file(args.file, args.algo)
        size = os.path.getsize(args.file)
        print(f"File:      {args.file}")
        print(f"Size:      {size} bytes")
        print(f"Algorithm: {args.algo}")
        print(f"Hash:      {result}")
    else:
        print(f"File not found: {args.file}")

else:
    # Demo mode
    print("=== Hash Generator Demo ===\n")
    test_text = "Hello, World!"

    print(f"Text: '{test_text}'\n")
    for algo in ["md5", "sha1", "sha256", "sha512"]:
        h = hash_text(test_text, algo)
        print(f"{algo.upper():<8}: {h}")

    # Show that same input always gives same hash
    print(f"\nSame input = same hash: {hash_text(test_text) == hash_text(test_text)}")
    print(f"Diff input = diff hash: {hash_text('hello') != hash_text('Hello')}")

    # Password verification demo
    print("\n=== Password Storage Example ===")
    password = "my_secret_password"
    stored_hash = hash_text(password, "sha256")
    print(f"Stored hash: {stored_hash[:32]}...")
    print(f"Login check: {hash_text(password) == stored_hash} (correct password)")
    print(f"Wrong pass:  {hash_text('wrong') == stored_hash} (wrong password)")
