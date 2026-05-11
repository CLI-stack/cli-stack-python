"""
Script: Base64 Encoder/Decoder CLI
What it does: Encodes and decodes text and files using Base64.
Base64 converts binary data to text — used in email attachments,
data URLs, and API authentication.

Run: python 76_base64_tool.py encode "Hello World"
Run: python 76_base64_tool.py decode "SGVsbG8gV29ybGQ="
"""

import base64
import argparse
import sys

def encode_text(text):
    """Encode a string to Base64."""
    # Encode string to bytes first, then to Base64
    text_bytes = text.encode("utf-8")      # str → bytes
    encoded_bytes = base64.b64encode(text_bytes)  # bytes → base64 bytes
    return encoded_bytes.decode("utf-8")   # base64 bytes → str

def decode_text(encoded):
    """Decode a Base64 string back to text."""
    try:
        encoded_bytes = encoded.encode("utf-8")   # str → bytes
        decoded_bytes = base64.b64decode(encoded_bytes)  # base64 → bytes
        return decoded_bytes.decode("utf-8")       # bytes → str
    except Exception as e:
        return f"Error decoding: {e}"

def encode_file(filepath):
    """Encode a file's contents to Base64."""
    with open(filepath, "rb") as f:  # "rb" = read binary
        content = f.read()
    return base64.b64encode(content).decode("utf-8")

# --- Parse arguments ---
parser = argparse.ArgumentParser(description="Base64 encode/decode tool")
subparsers = parser.add_subparsers(dest="action")

encode_p = subparsers.add_parser("encode", help="Encode text to Base64")
encode_p.add_argument("text", help="Text to encode")

decode_p = subparsers.add_parser("decode", help="Decode Base64 to text")
decode_p.add_argument("encoded", help="Base64 string to decode")

args = parser.parse_args()

# --- Demo mode if no arguments ---
if not args.action:
    print("=== Base64 Encoder/Decoder Demo ===\n")

    examples = ["Hello, World!", "Python is awesome!", "secret_password_123"]

    for text in examples:
        encoded = encode_text(text)
        decoded = decode_text(encoded)
        print(f"Original: {text}")
        print(f"Encoded:  {encoded}")
        print(f"Decoded:  {decoded}")
        print(f"Match:    {'✓' if text == decoded else '✗'}\n")

    # Show URL-safe variant
    print("=== URL-Safe Base64 ===")
    data = "Hello+World/Test=="
    url_safe = base64.urlsafe_b64encode(data.encode()).decode()
    print(f"URL-safe encoded: {url_safe}")
    print("(Uses - and _ instead of + and /)")

elif args.action == "encode":
    print(encode_text(args.text))

elif args.action == "decode":
    print(decode_text(args.encoded))
