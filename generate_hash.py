"""
generate_hash.py — Generate a SHA-256 hash for use as a page password.

Usage:
    python generate_hash.py
    python generate_hash.py mysecretpassword
"""

import hashlib
import sys


def sha256_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def main():
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = input("Enter password: ")

    hashed = sha256_hash(password)
    print(f"\nPassword : {password}")
    print(f"SHA-256  : {hashed}")
    print(f'\nPaste into HTML:\n  <script src="/js/auth.js" data-hash="{hashed}" defer></script>')


if __name__ == "__main__":
    main()
