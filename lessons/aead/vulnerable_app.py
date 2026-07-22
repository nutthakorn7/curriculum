"""Deliberately INSECURE -- Week 6 AEAD lab. Sandbox only; for authorized lab use.

The secret message (which CONTAINS the flag) is encrypted with AES-256-CBC and NO
authentication tag -- i.e. unauthenticated, malleable ciphertext (the Week 4 lesson) *plus* a
decrypt endpoint that leaks whether PKCS#7 padding was valid. That padding-error side channel is
a PADDING ORACLE: it lets an attacker decrypt any ciphertext byte-by-byte WITHOUT the key.

  GET  /secret            -> base64(IV || ct), the encrypted secret (fixed per process start)
  POST /decrypt {ciphertext: base64(IV||ct)}
        -> 200  if the CBC-decrypted plaintext has VALID PKCS#7 padding
        -> 403  "bad padding" if the padding is INVALID
      Those two DISTINGUISHABLE responses are the oracle. The endpoint never returns the
      plaintext -- the attacker recovers it purely from the 200-vs-403 signal.

This is what AEAD fixes: an authenticated cipher (AES-GCM, encrypt-then-MAC, ...) rejects any
tampered ciphertext with a SINGLE uniform error and checks the tag BEFORE touching the plaintext,
so there is no padding step to probe and no per-byte side channel. Compare with fixed_app.py
(AES-GCM) on :8099. See exploit.py for the full padding-oracle plaintext recovery.
"""
import base64
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import Flask, request, jsonify

app = Flask(__name__)

# Fixed AES-256 key for the whole process (32 bytes). Demo default; override via AES_KEY_HEX
# (64 hex chars). The attacker never learns this -- the whole point is decryption WITHOUT it.
KEY = bytes.fromhex(
    os.environ.get("AES_KEY_HEX", "00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff")
)
assert len(KEY) == 32, "AES_KEY_HEX must be 64 hex chars (32 bytes) for AES-256"

FLAG_AEAD = os.environ.get("FLAG_AEAD", "FLAG{padding_oracle_leaks_all}")

# Fixed IV so /secret is stable across requests within a process (still unauthenticated CBC).
IV = bytes.fromhex(os.environ.get("AES_IV_HEX", "0f1e2d3c4b5a69788796a5b4c3d2e1f0"))
assert len(IV) == 16, "AES_IV_HEX must be 32 hex chars (16 bytes)"

BLOCK = 16

# The secret plaintext that contains the flag. Kept short (fits in ~2 AES blocks after padding)
# so the padding-oracle run is fast to verify.
SECRET_PLAINTEXT = f"msg:{FLAG_AEAD}".encode()


def pkcs7_pad(data: bytes) -> bytes:
    n = BLOCK - (len(data) % BLOCK)
    return data + bytes([n]) * n


def pkcs7_valid(data: bytes) -> bool:
    """STRICT PKCS#7 check: last byte n must be 1..16 AND the last n bytes must all equal n."""
    if not data or len(data) % BLOCK != 0:
        return False
    n = data[-1]
    if n < 1 or n > BLOCK:
        return False
    return data[-n:] == bytes([n]) * n


def cbc_encrypt(iv: bytes, plaintext: bytes) -> bytes:
    enc = Cipher(algorithms.AES(KEY), modes.CBC(iv)).encryptor()
    return enc.update(pkcs7_pad(plaintext)) + enc.finalize()


def cbc_decrypt_raw(iv: bytes, ct: bytes) -> bytes:
    """Decrypt CBC and return the RAW plaintext (padding NOT stripped)."""
    dec = Cipher(algorithms.AES(KEY), modes.CBC(iv)).decryptor()
    return dec.update(ct) + dec.finalize()


# Encrypt the secret once at startup and serve the same IV||ct.
_CIPHERTEXT = base64.b64encode(IV + cbc_encrypt(IV, SECRET_PLAINTEXT)).decode()


@app.route("/")
def index():
    return (
        "Week 6 -- AEAD lab: CBC padding oracle (VULNERABLE; sandbox only)\n"
        "Endpoints:\n"
        "  GET  /secret    base64(IV||ct) of an AES-256-CBC-encrypted secret (contains the flag)\n"
        "  POST /decrypt {\"ciphertext\": base64(IV||ct)}\n"
        "       200 = valid PKCS#7 padding, 403 = bad padding  (this is the padding ORACLE)\n"
        "Unauthenticated CBC + a padding-error side channel = decryption without the key.\n"
        "The AEAD fix (AES-GCM) is on :8099.\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/secret")
def secret():
    # IV||ct, base64. This is exactly the format /decrypt parses back.
    return jsonify({"ciphertext": _CIPHERTEXT})


@app.route("/decrypt", methods=["POST"])
def decrypt():
    body = request.get_json(silent=True) or {}
    blob = body.get("ciphertext", "")

    # EVERY error path funnels to the SAME 403 as "bad padding" EXCEPT one: valid padding -> 200.
    # A distinct response for malformed input would itself be an extra side channel, so we avoid
    # it: base64 errors, wrong length, decrypt errors -> 403, identical to invalid padding.
    try:
        raw = base64.b64decode(blob, validate=True)
        if len(raw) < 2 * BLOCK or len(raw) % BLOCK != 0:
            return jsonify({"error": "bad padding"}), 403
        iv, ct = raw[:BLOCK], raw[BLOCK:]
        plaintext = cbc_decrypt_raw(iv, ct)
    except Exception:
        return jsonify({"error": "bad padding"}), 403

    # The ONLY distinguishing check: PKCS#7 padding validity. THIS is the oracle.
    if pkcs7_valid(plaintext):
        return jsonify({"status": "ok"}), 200
    return jsonify({"error": "bad padding"}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8098, threaded=True, debug=False)
