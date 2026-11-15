"""FIXED -- Week 11 Signatures/ZKP lab. Same endpoints as vulnerable_app.py, but the bank
enforces LOW-S normalization (BIP-62 style) before it will process a withdrawal.

The vulnerability is ECDSA twin malleability: (r,s) and (r,n-s) verify for the same
message/key but hash to different transaction IDs. Low-S accepts one member of that
particular pair and rejects its high-S twin. It does NOT make signatures unique for a
message/key: fresh signing nonces can create other valid low-S signatures.

This deliberately narrow reference control preserves signature-hash deduplication so
students can discuss its limitations. A real payment protocol also needs authenticated,
application-level transaction identity/idempotency (for example a signed unique sequence
number); low-S alone is not a complete double-withdrawal defense. This toy bank is not a
reproduction of Bitcoin consensus or evidence of the cause of MtGox's losses.

RULE (repo policy): the keypair is generated fresh at container startup, in memory -- no private
key is shipped in the repo.
"""
import hashlib
import os
import threading

from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigdecode_string, sigencode_string
from flask import Flask, request, jsonify

app = Flask(__name__)

FLAG_SIG = os.environ.get("FLAG_SIG", "FLAG{ecdsa_malleable_double_spend}")

WITHDRAW_MSG = b"withdraw 100 to attacker"
AMOUNT = 100
AUTHORIZED_TOTAL = 100

SK = SigningKey.generate(curve=SECP256k1)
VK = SK.get_verifying_key()
N = SECP256k1.order
HALF_N = N // 2

_lock = threading.Lock()
_seen_txids = set()
_total_withdrawn = 0


def txid_of(r: int, s: int) -> str:
    return hashlib.sha256((str(r) + str(s)).encode()).hexdigest()


def is_low_s(s: int) -> bool:
    """BIP-62 canonical check: a signature is only accepted if s is in the LOWER half."""
    return 0 < s <= HALF_N


@app.route("/")
def index():
    return (
        "Week 11 -- Digital Signatures lab: ECDSA malleability / double-spend (FIXED -- low-S / BIP-62)\n"
        "Endpoints:\n"
        "  GET  /sign      -> {message, sig_r, sig_s} : a valid, LOW-S ECDSA (r,s) for the fixed message\n"
        "  GET  /pubkey    -> {pubkey_hex, curve}\n"
        "  POST /withdraw  {message, sig_r, sig_s}    : reject any s > n//2 (malleated high-S twin);\n"
        "                                               then verify + dedup + process\n"
        "Malleated (r, n-s) high-S signatures that double-spend on :8102 are REJECTED here.\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/sign")
def sign():
    """Return a valid LOW-S signature for the fixed message (normalize s down if the freshly
    generated s happened to land in the upper half)."""
    sig = SK.sign(WITHDRAW_MSG, hashfunc=hashlib.sha256)
    r, s = sigdecode_string(sig, N)
    if s > HALF_N:
        s = N - s
    return jsonify({"message": WITHDRAW_MSG.decode(), "sig_r": str(r), "sig_s": str(s)})


@app.route("/pubkey")
def pubkey():
    return jsonify({"pubkey_hex": VK.to_string().hex(), "curve": "SECP256k1"})


@app.route("/withdraw", methods=["POST"])
def withdraw():
    global _total_withdrawn
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "JSON object required"}), 400
    message = body.get("message", "")
    if not isinstance(message, str):
        return jsonify({"error": "message must be a string"}), 400
    try:
        r = int(body.get("sig_r"))
        s = int(body.get("sig_s"))
    except (TypeError, ValueError):
        return jsonify({"error": "sig_r/sig_s must be integers"}), 400
    if not (1 <= r < N and 1 <= s < N):
        return jsonify({"error": "sig_r/sig_s out of range"}), 400

    if message.encode() != WITHDRAW_MSG:
        return jsonify({"error": "unknown message; this bank only authorizes the fixed withdraw"}), 400

    # THE FIX: reject non-canonical (high-S) signatures BEFORE verifying. The malleated twin
    # (r, n-s) of a low-S signature is high-S, so it is rejected here and never reaches dedup.
    if not is_low_s(s):
        return jsonify({"error": "non-canonical signature: s must be <= n/2 (BIP-62 low-S)"}), 403

    sig = sigencode_string(r, s, N)
    try:
        VK.verify(sig, message.encode(), hashfunc=hashlib.sha256)
    except Exception:
        return jsonify({"error": "bad signature"}), 403

    txid = txid_of(r, s)
    with _lock:
        if txid in _seen_txids:
            return jsonify({"error": "replay: txid already processed", "txid": txid}), 409
        _seen_txids.add(txid)
        _total_withdrawn += AMOUNT
        total = _total_withdrawn

    # The high-S twin is rejected above. Other fresh valid low-S signatures can still
    # pass this deliberately retained signature-hash deduplication; this is not a
    # complete application-level idempotency fix (see the worksheet limitation task).
    if total > AUTHORIZED_TOTAL:
        return jsonify({
            "status": "processed", "txid": txid, "amount": AMOUNT,
            "total_withdrawn": total, "double_spend_detected": True, "flag": FLAG_SIG,
        })
    return jsonify({"status": "processed", "txid": txid, "amount": AMOUNT, "total_withdrawn": total})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8103, debug=False)
