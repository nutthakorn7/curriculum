"""FIXED — Week 3 MACs lab. Same endpoints as vulnerable_app.py, but the cookie signature
is a proper HMAC (hmac.new(key, msg, sha256)) instead of a secret-prefix hash.

HMAC's nested construction -- H(key XOR opad || H(key XOR ipad || message)) -- means the
*outer* hash is computed over a fixed-size (already-hashed) block, not over attacker-extendable
data. An attacker who intercepts a valid (data, sig) pair still cannot compute a valid sig for
data + glue_padding + extra without knowing the key: they would need to resume the OUTER hash's
internal state, but that state depends on H(key XOR ipad || message), which they cannot compute
without the key. Length-extension is a property of bare Merkle-Damgard hashes (see source Q5);
HMAC's construction specifically defeats it. exploit.py runs the SAME forgery attempt against
this app on :8093 and must observe it correctly REJECTED (403, no flag).
"""
import hashlib
import hmac as hmac_module
import os

from flask import Flask, request, make_response, jsonify

app = Flask(__name__)

MAC_SECRET = os.environ.get("MAC_SECRET", "0123456789abcdef")
FLAG_MACS = os.environ.get("FLAG_MACS", "FLAG{macs_demo}")

assert len(MAC_SECRET) == 16, "MAC_SECRET must be exactly 16 ASCII bytes for this lab"


def make_cookie(data: bytes) -> dict:
    sig = hmac_module.new(MAC_SECRET.encode(), data, hashlib.sha256).hexdigest()
    return {"data": data.hex(), "sig": sig}


@app.route("/")
def index():
    return (
        "Week 3 -- MACs lab: hash-only cookie / length-extension (FIXED -- proper HMAC)\n"
        "Endpoints:\n"
        "  GET /login?user=<name>   issue a cookie: data='user=<name>&admin=false', sig=HMAC-SHA256(secret, data)\n"
        "  GET /admin               verify cookie; if sig valid AND data contains 'admin=true' -> flag\n"
        "Length-extension forgeries that work against :8092 must FAIL here.\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/login")
def login():
    user = request.args.get("user", "guest")
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

    expected = hmac_module.new(MAC_SECRET.encode(), data_bytes, hashlib.sha256).hexdigest()

    # Still a plain `!=` here on purpose (see vulnerable_app.py's note) -- switching to HMAC
    # fixes length-extension, but constant-time comparison is a SEPARATE fix (hmac.compare_digest).
    if sig != expected:
        return jsonify({"error": "bad signature"}), 403

    if b"admin=true" in data_bytes:
        return jsonify({"flag": FLAG_MACS})
    return jsonify({"error": "not admin"}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8093, debug=False)
