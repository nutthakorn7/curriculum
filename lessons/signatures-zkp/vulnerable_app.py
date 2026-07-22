"""Deliberately INSECURE -- Week 11 Signatures/ZKP lab. Sandbox only; authorized lab use only.

A demo "bank" that authorizes a withdrawal with an ECDSA signature (SECP256k1) and
DEDUPLICATES transactions by a hash of the signature bytes:

    txid = sha256(str(r) + str(s))

ECDSA signatures are MALLEABLE: if (r, s) is a valid signature for a message under a key,
then (r, n - s) is ALSO a valid signature for the SAME message under the SAME key
(n = the curve order). The two share (message, pubkey) but hash to DIFFERENT txids. A system
that identifies/deduplicates by signature-hash therefore treats one authorized withdrawal as
two distinct transactions -> the SAME logical withdrawal is processed TWICE (a MtGox-style
"double spend"). See exploit.py. Compare with fixed_app.py (low-S / BIP-62 normalization) on
:8103.

RULE (repo policy): no private key is ever shipped in the repo. The keypair is generated fresh
at container startup, in memory. `/sign` is a lab convenience that signs the ONE fixed withdraw
message with that key so students can obtain a starting (r, s) without owning the key.
"""
import hashlib
import os
import threading

from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigdecode_string, sigencode_string
from flask import Flask, request, jsonify

app = Flask(__name__)

FLAG_SIG = os.environ.get("FLAG_SIG", "FLAG{ecdsa_malleable_double_spend}")

# The single, fixed withdrawal this demo authorizes. The bank only ever verifies THIS message.
WITHDRAW_MSG = b"withdraw 100 to attacker"
AMOUNT = 100                 # amount moved per processed withdrawal
AUTHORIZED_TOTAL = 100       # the account owner authorized exactly ONE withdrawal of 100

# Keypair generated in memory at startup -- never persisted, never committed (repo policy).
SK = SigningKey.generate(curve=SECP256k1)
VK = SK.get_verifying_key()
N = SECP256k1.order

# Bank state (single-process demo; a lock keeps the double-process check honest under load).
_lock = threading.Lock()
_seen_txids = set()          # dedup set: keyed by sha256(str(r)+str(s)) -- the VULNERABLE choice
_total_withdrawn = 0


def txid_of(r: int, s: int) -> str:
    """Transaction id = hash of the SIGNATURE. This is the vulnerable design decision:
    a malleated signature (r, n-s) for the same message yields a DIFFERENT txid."""
    return hashlib.sha256((str(r) + str(s)).encode()).hexdigest()


@app.route("/")
def index():
    return (
        "Week 11 -- Digital Signatures lab: ECDSA malleability / double-spend (VULNERABLE; sandbox only)\n"
        "Endpoints:\n"
        "  GET  /sign      -> {message, sig_r, sig_s} : a valid ECDSA (r,s) for the fixed withdraw message\n"
        "  GET  /pubkey    -> {pubkey_hex, curve}     : this bank's public key (for local verification)\n"
        "  POST /withdraw  {message, sig_r, sig_s}    : verify sig; dedup by sha256(str(r)+str(s));\n"
        "                                               process withdrawal; if total exceeds the single\n"
        "                                               authorized amount -> return the flag\n"
        "This bank deduplicates by SIGNATURE HASH -- vulnerable to (r, n-s) malleability.\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/sign")
def sign():
    """Lab helper: sign the ONE fixed withdraw message with the bank's key and hand back (r, s).
    (In the real MtGox story the attacker already possessed a validly signed transaction of
    their own; this endpoint just stands in for 'attacker holds one valid signature'.)"""
    sig = SK.sign(WITHDRAW_MSG, hashfunc=hashlib.sha256)
    r, s = sigdecode_string(sig, N)
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

    # Only the one fixed withdrawal is authorizable here.
    if message.encode() != WITHDRAW_MSG:
        return jsonify({"error": "unknown message; this bank only authorizes the fixed withdraw"}), 400

    # Verify the ECDSA signature. NOTE: python-ecdsa does NOT enforce low-S on verify, so BOTH
    # (r, s) and (r, n-s) verify True here. THAT is the malleability the dedup design fails to
    # account for -- not a bug in verification itself.
    sig = sigencode_string(r, s, N)
    try:
        VK.verify(sig, message.encode(), hashfunc=hashlib.sha256)
    except Exception:
        return jsonify({"error": "bad signature"}), 403

    txid = txid_of(r, s)
    with _lock:
        if txid in _seen_txids:
            # Correctly stops a byte-for-byte REPLAY of the exact same (r, s)...
            return jsonify({"error": "replay: txid already processed", "txid": txid}), 409
        _seen_txids.add(txid)
        # ...but a malleated (r, n-s) has a DIFFERENT txid, so we reach here a second time and
        # process the SAME logical withdrawal again.
        _total_withdrawn += AMOUNT
        total = _total_withdrawn

    if total > AUTHORIZED_TOTAL:
        # The owner authorized ONE withdrawal of 100, but we've now moved more than that from a
        # single authorization -> double-spend detected.
        return jsonify({
            "status": "processed",
            "txid": txid,
            "amount": AMOUNT,
            "total_withdrawn": total,
            "double_spend_detected": True,
            "flag": FLAG_SIG,
        })
    return jsonify({"status": "processed", "txid": txid, "amount": AMOUNT, "total_withdrawn": total})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8102, debug=False)
