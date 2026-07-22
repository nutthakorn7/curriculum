"""Deliberately INSECURE -- Week 4 AES / block-cipher-modes lab. Sandbox only.

The session token is UNAUTHENTICATED AES-256-CBC: token = base64(IV || AES-CBC(key, plaintext)).
There is NO MAC and NO auth tag, so the ciphertext is *malleable*: an attacker who never learns
the key can predictably alter the decrypted plaintext by XOR-ing bytes into the PREVIOUS
ciphertext block (a "CBC bit-flipping" attack). This is source Q3 ("encrypts but does not verify
integrity") made concrete. Compare with fixed_app.py (AES-256-GCM, authenticated) on :8097.

================================ BLOCK LAYOUT (read this) ================================
The server-side plaintext is a FIXED 32-byte constant (two AES blocks). /login ignores any
client input for layout purposes -- the role always sits at the same byte offset, so the
bit-flip target is deterministic.

    Block 0  (plaintext bytes  0..15):  b"comment=FILLER!!"   <- expendable filler
    Block 1  (plaintext bytes 16..31):  b"role=guest;xpad0"   <- role value at offset 5..9

Token bytes:  IV (16) || C0 (16) || C1 (16)     (48 bytes, then base64)
    IV = token[0:16]      C0 = token[16:32]      C1 = token[32:48]

CBC decryption of block 1:   P1 = AES_decrypt(C1) XOR C0
So flipping ANY byte of C0 (== token[16 + k]) flips the SAME byte position k of P1, while
turning block 0's plaintext (the "comment" filler) into unpredictable garbage. The app never
reads the comment field, so garbling block 0 is harmless.

Target: turn P1 = "role=guest;xpad0" into "role=admin;xpad0".
  "guest" occupies P1[5..9]; "admin" is also 5 bytes (equal length -> a clean, length-preserving
  XOR flip). For each i in 0..4:  C0[5+i] ^= (ord("guest"[i]) ^ ord("admin"[i])).
  i.e. edit token[16 + 5 + i] = token[21 + i].
==========================================================================================
"""
import base64
import os

from flask import Flask, request, make_response, jsonify

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

app = Flask(__name__)

# AES-256 => 32-byte key. Fixed demo key (the attacker never needs it -- malleability, not
# key recovery, is the point). Override via AES_KEY (must be 64 hex chars = 32 bytes).
_KEY_HEX = os.environ.get("AES_KEY", "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff")
KEY = bytes.fromhex(_KEY_HEX)
assert len(KEY) == 32, "AES_KEY must be 32 bytes (64 hex chars) for AES-256"

FLAG_AES = os.environ.get("FLAG_AES", "FLAG{aes_cbc_is_malleable}")

# Fixed 32-byte (2-block) plaintext. Role value is block-aligned inside block 1.
PLAINTEXT = b"comment=FILLER!!" + b"role=guest;xpad0"
assert len(PLAINTEXT) == 32, "plaintext must be exactly two 16-byte blocks"


def _aes_cbc_encrypt(iv: bytes, pt: bytes) -> bytes:
    enc = Cipher(algorithms.AES(KEY), modes.CBC(iv)).encryptor()
    return enc.update(pt) + enc.finalize()


def _aes_cbc_decrypt(iv: bytes, ct: bytes) -> bytes:
    dec = Cipher(algorithms.AES(KEY), modes.CBC(iv)).decryptor()
    return dec.update(ct) + dec.finalize()


def issue_token() -> str:
    iv = os.urandom(16)
    ct = _aes_cbc_encrypt(iv, PLAINTEXT)  # PLAINTEXT is a whole number of blocks -> no padding
    return base64.b64encode(iv + ct).decode()


def parse_role(token_b64: str) -> str:
    """Decrypt the token and read the role field out of block 1 at its fixed offset.

    Block 0 (the comment filler) may be garbage after a bit-flip -- we deliberately do NOT read
    it. Block 1 has the form b"role=<5 bytes>;xpad0"; we anchor on the fixed layout and return
    the 5-byte role value, so a garbled block 0 can never accidentally inject a role.
    """
    raw = base64.b64decode(token_b64)
    iv, ct = raw[:16], raw[16:]
    pt = _aes_cbc_decrypt(iv, ct)
    block1 = pt[16:32]                       # b"role=<5>;xpad0"
    if not block1.startswith(b"role=") or block1[10:11] != b";":
        return "?"
    return block1[5:10].decode("latin-1")    # the 5-byte role value


@app.route("/")
def index():
    return (
        "Week 4 -- AES / block-cipher modes lab: unauthenticated AES-CBC (VULNERABLE; sandbox only)\n"
        "Endpoints:\n"
        "  GET /login    issue a session token = base64(IV || AES-256-CBC(plaintext)); role=guest\n"
        "  GET /whoami   decrypt the token cookie and report the parsed role\n"
        "  GET /admin    if parsed role == 'admin' -> flag; else 403\n"
        "This token has NO MAC / auth tag -- AES-CBC alone is malleable (CBC bit-flipping).\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/login")
def login():
    token = issue_token()
    resp = make_response("logged in as guest (role=guest)\n")
    resp.set_cookie("token", token)
    return resp


@app.route("/whoami")
def whoami():
    token = request.cookies.get("token", "")
    try:
        role = parse_role(token)
    except Exception:
        return jsonify({"error": "malformed token"}), 400
    return jsonify({"role": role})


@app.route("/admin")
def admin():
    token = request.cookies.get("token", "")
    try:
        role = parse_role(token)
    except Exception:
        # A missing/malformed token is not admin -> 403 (never leak the flag on any error path).
        return jsonify({"error": "malformed token"}), 403
    if role == "admin":
        return jsonify({"flag": FLAG_AES})
    return jsonify({"error": "not admin", "role": role}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8096, debug=False)
