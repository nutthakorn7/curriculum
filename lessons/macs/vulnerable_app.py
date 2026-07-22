"""Deliberately INSECURE — Week 3 MACs lab. Sandbox only; for authorized lab use.

Cookie authenticity is "protected" by a SECRET-PREFIX hash: sig = SHA256(MAC_SECRET + data).
This is the generalized form of source Q1's `username || SHA-3(username)` cookie (no key at
all) and source Q5's `SHA-256(key || message)` MAC (a key, but glued on the wrong side).
Because SHA-256 is a Merkle-Damgard hash, anyone who knows sig, len(data), and len(MAC_SECRET)
can compute SHA256(MAC_SECRET + data + glue_padding + anything) WITHOUT knowing MAC_SECRET.
See exploit.py for the forgery. Compare with fixed_app.py (proper HMAC) on :8093.
"""
import hashlib
import os

from flask import Flask, request, make_response, jsonify

app = Flask(__name__)

# Demo secret — 16 ASCII bytes (== 16 bytes, since ASCII chars are 1 byte each).
# exploit.py's SECRET_LEN constant MUST match this length; the attacker is assumed to know
# the LENGTH (a realistic assumption — it's often guessable/brute-forceable in small ranges)
# but never the VALUE.
MAC_SECRET = os.environ.get("MAC_SECRET", "0123456789abcdef")
FLAG_MACS = os.environ.get("FLAG_MACS", "FLAG{macs_demo}")

assert len(MAC_SECRET) == 16, "MAC_SECRET must be exactly 16 ASCII bytes for this lab"


def make_cookie(data: bytes) -> dict:
    sig = hashlib.sha256(MAC_SECRET.encode() + data).hexdigest()
    return {"data": data.hex(), "sig": sig}


@app.route("/")
def index():
    return (
        "Week 3 -- MACs lab: hash-only cookie / length-extension (VULNERABLE; sandbox only)\n"
        "Endpoints:\n"
        "  GET /login?user=<name>   issue a cookie: data='user=<name>&admin=false', sig=SHA256(secret||data)\n"
        "  GET /admin               verify cookie; if sig valid AND data contains 'admin=true' -> flag\n"
        "This app uses a SECRET-PREFIX hash (not HMAC) -- vulnerable to length-extension.\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/login")
def login():
    user = request.args.get("user", "guest")
    # data is transported hex-encoded because a forged extension contains raw padding bytes
    # (0x80, length bytes) that are not valid cookie-safe text.
    data = f"user={user}&admin=false".encode()
    cookie = make_cookie(data)
    resp = make_response(f"logged in as {user}\n")
    resp.set_cookie("data", cookie["data"])
    resp.set_cookie("sig", cookie["sig"])
    return resp


@app.route("/admin")
def admin():
    data_hex = request.cookies.get("data", "")
    sig = request.cookies.get("sig", "")
    try:
        data_bytes = bytes.fromhex(data_hex)
    except ValueError:
        return jsonify({"error": "malformed cookie"}), 403

    # Byte-native verification -- this is deliberate: the vulnerable construction is
    # SHA256(secret_bytes + data_bytes), and a forged data_bytes contains non-UTF-8 padding
    # bytes (0x80 etc.), so verification MUST happen on raw bytes, not on a decoded string.
    expected = hashlib.sha256(MAC_SECRET.encode() + data_bytes).hexdigest()

    # NOTE: plain `==`/`!=` on strings is a naive, non-constant-time comparison -- see
    # worksheet Part 2 Q4 (timing attack on tag verification). Not the focus of this lab's
    # exploit, but the vulnerability is real; the fixed app leaves the same comparison in
    # place on purpose so students notice it isn't automatically fixed by switching to HMAC.
    if sig != expected:
        return jsonify({"error": "bad signature"}), 403

    if b"admin=true" in data_bytes:
        return jsonify({"flag": FLAG_MACS})
    return jsonify({"error": "not admin"}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8092, debug=False)
