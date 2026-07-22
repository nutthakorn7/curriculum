"""FIXED -- Week 4 AES / block-cipher-modes lab. Same endpoints as vulnerable_app.py, but the
token is AUTHENTICATED encryption: AES-256-GCM instead of raw AES-CBC.

    token = base64(nonce(12) || AES-256-GCM-ciphertext || tag(16))

GCM is an AEAD (Authenticated Encryption with Associated Data): every decryption re-checks a
128-bit authentication tag computed over the ciphertext. If ANY ciphertext (or nonce) byte is
altered -- exactly what CBC bit-flipping does -- the tag no longer matches and decryption RAISES,
so the token is rejected outright (403). Malleability is gone: you cannot silently flip a
plaintext byte, because you cannot also forge the tag without the key. This is why TLS/modern
systems use AES-GCM (authenticated encryption) instead of AES-CBC alone (source Q3/Q4/Q9).

exploit.py applies the SAME tampering idea (flip a ciphertext byte) to a token from THIS app on
:8097 and must observe it correctly REJECTED (403, no flag).

NOTE: GCM's token layout (nonce || ct || tag) is different from CBC's (IV || C0 || C1). There is
no "previous ciphertext block" to XOR into -- "same technique" here means "tamper with the
ciphertext"; the point is that ANY tamper fails the tag check.
"""
import base64
import os

from flask import Flask, request, make_response, jsonify

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

app = Flask(__name__)

_KEY_HEX = os.environ.get("AES_KEY", "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff")
KEY = bytes.fromhex(_KEY_HEX)
assert len(KEY) == 32, "AES_KEY must be 32 bytes (64 hex chars) for AES-256"

FLAG_AES = os.environ.get("FLAG_AES", "FLAG{aes_cbc_is_malleable}")

# Same 32-byte plaintext as the vulnerable app so the exploit targets the identical role bytes.
PLAINTEXT = b"comment=FILLER!!" + b"role=guest;xpad0"
assert len(PLAINTEXT) == 32, "plaintext must be exactly two 16-byte blocks"


def issue_token() -> str:
    nonce = os.urandom(12)                       # 96-bit GCM nonce -- fresh every token
    ct_and_tag = AESGCM(KEY).encrypt(nonce, PLAINTEXT, None)
    return base64.b64encode(nonce + ct_and_tag).decode()


def parse_role(token_b64: str) -> str:
    """Decrypt-and-verify the GCM token. Any tampering fails the tag check and RAISES here."""
    raw = base64.b64decode(token_b64)
    nonce, ct_and_tag = raw[:12], raw[12:]
    pt = AESGCM(KEY).decrypt(nonce, ct_and_tag, None)   # raises InvalidTag if tampered
    block1 = pt[16:32]
    if not block1.startswith(b"role=") or block1[10:11] != b";":
        return "?"
    return block1[5:10].decode("latin-1")


@app.route("/")
def index():
    return (
        "Week 4 -- AES / block-cipher modes lab: authenticated AES-256-GCM (FIXED)\n"
        "Endpoints:\n"
        "  GET /login    issue a session token = base64(nonce || AES-256-GCM-ct || tag); role=guest\n"
        "  GET /whoami   decrypt+verify the token cookie and report the parsed role\n"
        "  GET /admin    if parsed role == 'admin' -> flag; else 403\n"
        "CBC bit-flipping forgeries that work against :8096 must FAIL here (tag check rejects them).\n",
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
        # InvalidTag (tampered token) or malformed input both land here.
        return jsonify({"error": "invalid or tampered token"}), 403
    return jsonify({"role": role})


@app.route("/admin")
def admin():
    token = request.cookies.get("token", "")
    try:
        role = parse_role(token)
    except Exception:
        return jsonify({"error": "invalid or tampered token"}), 403
    if role == "admin":
        return jsonify({"flag": FLAG_AES})
    return jsonify({"error": "not admin", "role": role}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8097, debug=False)
