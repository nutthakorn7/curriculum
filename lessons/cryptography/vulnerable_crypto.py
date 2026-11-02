"""
Week 3 — a small crypto helper with four mistakes. Find them (Tasks 1-2), then compare solution_skeleton.py.
"""
import hashlib, random
from Crypto.Cipher import AES  # pip install pycryptodome

# Store a user's password
def store_password(pw: str) -> str:
    return hashlib.md5(pw.encode()).hexdigest()

# Encrypt data before it is saved
HARDCODED_KEY = b"0123456789abcdef"
def encrypt_ecb(data: bytes) -> bytes:
    cipher = AES.new(HARDCODED_KEY, AES.MODE_ECB)
    pad = 16 - (len(data) % 16)
    return cipher.encrypt(data + bytes([pad]) * pad)

# Make a password-reset token
def reset_token() -> str:
    return "".join(random.choice("0123456789") for _ in range(6))

if __name__ == "__main__":
    print("md5:", store_password("password123"))
    # Encrypt two identical 16-byte blocks:
    print("ecb:", encrypt_ecb(b"A"*16 + b"A"*16).hex())
    print("token:", reset_token())
