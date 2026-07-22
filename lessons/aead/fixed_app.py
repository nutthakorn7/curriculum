"""FIXED -- Week 6 AEAD lab. Same endpoints as vulnerable_app.py, but the secret is protected
with AES-256-GCM, an AEAD (Authenticated Encryption with Associated Data) cipher.

Two things kill the padding oracle:
  1. GCM is a STREAM mode (CTR under the hood) -- there is no block padding at all, so there is
     no "valid vs invalid padding" distinction to leak.
  2. GCM authenticates: decryption verifies a 128-bit tag BEFORE releasing any plaintext. Any
     tampered/forged ciphertext fails the tag check.
And critically, /decrypt returns a UNIFORM 403 for EVERY failure -- bad base64, wrong length,
bad nonce, tag mismatch -- all indistinguishable. There is no per-byte signal for an attacker to
turn into a decryption. The same padding-oracle attack that fully recovers the plaintext on
:8098 gets ZERO usable signal here.

  GET  /secret            -> base64(nonce || ct || tag), AES-256-GCM
  POST /decrypt {ciphertext: base64(nonce||ct||tag)}
        -> 200 only if the tag verifies (authentic ciphertext); 403 (uniform) otherwise
"""
import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import Flask, request, jsonify

app = Flask(__name__)

KEY = bytes.fromhex(
    os.environ.get("AES_KEY_HEX", "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff")
)
assert len(KEY) == 32, "AES_KEY_HEX must be 64 hex chars (32 bytes) for AES-256"

FLAG_AEAD = os.environ.get("FLAG_AEAD", "FLAG{padding_oracle_leaks_all}")

# 96-bit nonce (GCM standard). Fixed so /secret is stable within a process. (In real systems a
# GCM nonce must be UNIQUE per message under a key -- see Week 10's nonce-reuse audit; a fixed
# nonce is acceptable here only because we encrypt exactly one message per process.)
NONCE = bytes.fromhex(os.environ.get("AES_NONCE_HEX", "0f1e2d3c4b5a69788796a5b4"))
assert len(NONCE) == 12, "AES_NONCE_HEX must be 24 hex chars (12 bytes)"

NONCE_LEN = 12
TAG_LEN = 16

SECRET_PLAINTEXT = f"msg:{FLAG_AEAD}".encode()

_aesgcm = AESGCM(KEY)
# nonce || ct||tag  (cryptography returns ct||tag concatenated). Base64 the whole blob.
_ct_and_tag = _aesgcm.encrypt(NONCE, SECRET_PLAINTEXT, None)
_CIPHERTEXT = base64.b64encode(NONCE + _ct_and_tag).decode()


@app.route("/")
def index():
    return (
        "Week 6 -- AEAD lab: AES-256-GCM (FIXED -- authenticated encryption)\n"
        "Endpoints:\n"
        "  GET  /secret    base64(nonce||ct||tag) of an AES-256-GCM-encrypted secret\n"
        "  POST /decrypt {\"ciphertext\": base64(nonce||ct||tag)}\n"
        "       200 only if the tag verifies; 403 (UNIFORM) for ANY failure -- no side channel\n"
        "Stream mode = no padding; tag checked before plaintext = no oracle. AEAD.\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/secret")
def secret():
    return jsonify({"ciphertext": _CIPHERTEXT})


@app.route("/decrypt", methods=["POST"])
def decrypt():
    body = request.get_json(silent=True) or {}
    blob = body.get("ciphertext", "")

    # UNIFORM failure. EVERY error -- bad base64, wrong length, bad nonce, tag mismatch -- returns
    # the identical 403. A 400-vs-403 split, or a 500 stack trace, would reintroduce exactly the
    # side channel AEAD is meant to remove. The uniformity IS the teaching point.
    try:
        raw = base64.b64decode(blob, validate=True)
        if len(raw) < NONCE_LEN + TAG_LEN:
            return jsonify({"error": "decryption failed"}), 403
        nonce, ct_and_tag = raw[:NONCE_LEN], raw[NONCE_LEN:]
        # Raises InvalidTag on any tampering; we catch it and return the same uniform 403.
        _aesgcm.decrypt(nonce, ct_and_tag, None)
    except Exception:
        return jsonify({"error": "decryption failed"}), 403

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8099, threaded=True, debug=False)
