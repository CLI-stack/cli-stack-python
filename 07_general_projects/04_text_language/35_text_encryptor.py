"""
Project: Text Encryptor (Caesar Cipher + Vigenère Cipher)
What it does: Encrypts and decrypts messages using classical ciphers.
Great for learning the fundamentals of cryptography.

Caesar Cipher: shift each letter by N positions in the alphabet
  "HELLO" with shift=3 → "KHOOR"
  (H→K, E→H, L→O, L→O, O→R)

Vigenère Cipher: uses a keyword to create varying shifts
  Keyword "KEY" → shifts: K=10, E=4, Y=24, K=10, E=4...
  Much harder to crack than Caesar cipher.

Run: python 35_text_encryptor.py
"""

import argparse


def caesar_encrypt(text, shift):
    """
    Encrypt text using the Caesar cipher.
    Each letter is shifted 'shift' positions forward in the alphabet.
    Non-letter characters (spaces, punctuation) are left unchanged.
    """
    result = []
    shift  = shift % 26  # modulo ensures shift stays within 0-25 range

    for char in text:
        if char.isalpha():
            # Determine the base ASCII value (65 for uppercase, 97 for lowercase)
            # ord() converts a character to its ASCII number: ord('A') = 65
            base = ord('A') if char.isupper() else ord('a')

            # Shift the character:
            # 1. Move to 0-based index:  ord(char) - base
            # 2. Add the shift
            # 3. Wrap around using modulo 26
            # 4. Convert back to character: chr(number)
            shifted = (ord(char) - base + shift) % 26 + base
            result.append(chr(shifted))
        else:
            result.append(char)  # keep non-letters as-is

    return "".join(result)


def caesar_decrypt(text, shift):
    """Decrypt Caesar cipher by shifting backwards (subtract instead of add)."""
    return caesar_encrypt(text, -shift)  # negative shift = reverse direction


def vigenere_encrypt(text, keyword):
    """
    Encrypt using the Vigenère cipher.
    The keyword repeats to match the length of the text.
    Each letter uses a different shift based on the current keyword letter.
    """
    keyword = keyword.upper()  # normalize keyword to uppercase
    result  = []
    key_idx = 0               # tracks our position in the keyword

    for char in text:
        if char.isalpha():
            # Get the shift value from the current keyword character
            # 'A' = 0, 'B' = 1, ..., 'Z' = 25
            key_char = keyword[key_idx % len(keyword)]  # cycle through keyword
            shift    = ord(key_char) - ord('A')

            base    = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - base + shift) % 26 + base
            result.append(chr(shifted))

            key_idx += 1   # advance the keyword position for the next letter
        else:
            result.append(char)  # leave non-letters unchanged

    return "".join(result)


def vigenere_decrypt(text, keyword):
    """Decrypt Vigenère by subtracting the keyword shifts instead of adding."""
    keyword = keyword.upper()
    result  = []
    key_idx = 0

    for char in text:
        if char.isalpha():
            key_char = keyword[key_idx % len(keyword)]
            shift    = ord(key_char) - ord('A')

            base    = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - base - shift) % 26 + base  # subtract shift
            result.append(chr(shifted))
            key_idx += 1
        else:
            result.append(char)

    return "".join(result)


def frequency_analysis(text):
    """
    Analyze letter frequencies to help crack a Caesar cipher.
    In English, 'E' is the most common letter (~12.7%).
    If 'H' is most common in the ciphertext, the shift is likely 3 (E+3=H).
    """
    from collections import Counter

    letters = [c.upper() for c in text if c.isalpha()]
    if not letters:
        return {}

    counts = Counter(letters)
    total  = len(letters)

    # Return frequencies as percentages
    return {char: count/total*100 for char, count in counts.most_common(5)}


def demo():
    """Run a demonstration of both ciphers."""
    message = "The quick brown fox jumps over the lazy dog"
    print(f"Original: {message}\n")

    # ── Caesar cipher demo ────────────────────────────────────────────────────
    print("=== Caesar Cipher ===")
    for shift in [3, 13, 25]:  # ROT13 is shift=13 (used widely online)
        encrypted = caesar_encrypt(message, shift)
        decrypted = caesar_decrypt(encrypted, shift)
        print(f"\n  Shift {shift}:")
        print(f"  Encrypted : {encrypted}")
        print(f"  Decrypted : {decrypted}")
        assert decrypted == message, "Decryption failed!"
        print(f"  Verified  : ✓ encrypt → decrypt gives original")

    # ── Vigenère cipher demo ──────────────────────────────────────────────────
    print(f"\n=== Vigenère Cipher ===")
    for keyword in ["KEY", "PYTHON", "SECRET"]:
        encrypted = vigenere_encrypt(message, keyword)
        decrypted = vigenere_decrypt(encrypted, keyword)
        print(f"\n  Keyword '{keyword}':")
        print(f"  Encrypted : {encrypted}")
        print(f"  Decrypted : {decrypted}")
        assert decrypted == message, "Decryption failed!"
        print(f"  Verified  : ✓")

    # ── Frequency analysis ────────────────────────────────────────────────────
    print(f"\n=== Frequency Analysis (crack Caesar) ===")
    shift       = 7
    cipher_text = caesar_encrypt(message, shift)
    print(f"  Ciphertext: {cipher_text}")
    freqs = frequency_analysis(cipher_text)
    print(f"  Top letter frequencies in ciphertext:")
    for letter, pct in freqs.items():
        print(f"    '{letter}': {pct:.1f}%  "
              f"→ if this is 'E', shift = {(ord(letter) - ord('E')) % 26}")
    print(f"  (Actual shift used: {shift})")


# ── Main ─────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Text encryption with Caesar/Vigenère")
parser.add_argument("--encrypt",  help="Text to encrypt")
parser.add_argument("--decrypt",  help="Text to decrypt")
parser.add_argument("--shift",    type=int, default=13, help="Caesar shift (default: 13 = ROT13)")
parser.add_argument("--keyword",  default="PYTHON", help="Vigenère keyword")
parser.add_argument("--cipher",   choices=["caesar","vigenere"], default="caesar")
args = parser.parse_args()

print("=== Text Encryptor ===\n")

if args.encrypt:
    if args.cipher == "caesar":
        result = caesar_encrypt(args.encrypt, args.shift)
        print(f"Caesar encrypted (shift={args.shift}): {result}")
    else:
        result = vigenere_encrypt(args.encrypt, args.keyword)
        print(f"Vigenère encrypted (key='{args.keyword}'): {result}")
elif args.decrypt:
    if args.cipher == "caesar":
        result = caesar_decrypt(args.decrypt, args.shift)
        print(f"Caesar decrypted (shift={args.shift}): {result}")
    else:
        result = vigenere_decrypt(args.decrypt, args.keyword)
        print(f"Vigenère decrypted (key='{args.keyword}'): {result}")
else:
    demo()
