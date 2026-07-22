"""FIXED -- Week 11 Signatures/ZKP lab. Same endpoints as vulnerable_app.py, but the bank
enforces LOW-S normalization (BIP-62 style) before it will process a withdrawal.

The vulnerability was ECDSA malleability: for a valid (r, s) the twin (r, n - s) is also a
valid signature for the same message+key but hashes to a different txid, so a bank that
deduplicates by signature-hash double-processes one authorization. The canonical MtGox-era fix
(Bitcoin BIP-62 / BIP-146) is to reject any signature whose s is in the UPPER half of the
range: a signature is only valid if s <= n // 2. Because n is odd, exactly ONE of {s, n - s}
is <= n // 2 -- so a message+key has exactly ONE canonical (low-S) signature. The malleated
high-S twin is now rejected at verification time; there is no second txid to double-process.

Defense-in-depth note (see the answer key): the complementary PROTOCOL-level fix is to
deduplicate by (message, pubkey) instead of by signature bytes, which recognizes the malleated
submission as the same logical transaction regardless of s. This app uses low-S as the primary,
signature-level fix because it names the vulnerability directly and matches the real BIP-62 fix.

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
    body = request.get_json(silent=True) or {}
    message = body.get("message", "")
    try:
        r = int(body.get("sig_r"))
        s = int(body.get("sig_s"))
    except (TypeError, ValueError):
        return jsonify({"error": "sig_r/sig_s must be integers"}), 400

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

    # With low-S enforced, a message+key has exactly ONE acceptable signature, so total can never
    # exceed the authorized amount via malleability -> the flag branch is unreachable here.
    if total > AUTHORIZED_TOTAL:
        return jsonify({
            "status": "processed", "txid": txid, "amount": AMOUNT,
            "total_withdrawn": total, "double_spend_detected": True, "flag": FLAG_SIG,
        })
    return jsonify({"status": "processed", "txid": txid, "amount": AMOUNT, "total_withdrawn": total})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8103, debug=False)
