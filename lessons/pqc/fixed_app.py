"""FIXED -- Week 15 PQC lab. Same Lamport one-time signature scheme and same endpoints as
vulnerable_app.py, but this app ENFORCES THE ONE-TIME RULE: the keypair signs at most ONCE.

Lamport OTS is provably secure only if the key signs a single message. The vulnerability in
vulnerable_app.py was signing MANY messages with ONE key, letting an attacker collect both
preimages per bit position (from a message and its complement) and reconstruct the whole
private key. The fix here is not a different math -- it is an operational invariant: refuse the
second signature. A second POST /sign returns 403 "one-time key already used", so the attacker
can never obtain the complementary signature, never recovers the second preimage for any bit,
and cannot forge a signature on the admin message.

This is the real-world discipline behind stateful hash-based schemes (XMSS/LMS): never reuse a
one-time key. SPHINCS+ makes this STATELESS by using a huge tree of one-time keys chosen so that
reuse is cryptographically negligible -- but the underlying primitive is still one-time.

exploit.py runs the SAME two-signature key-recovery attack against this app on :8101 and must
observe the 2nd /sign REFUSED (403) and therefore NO flag.
"""
import hashlib
import os
import threading

from flask import Flask, request, jsonify

app = Flask(__name__)

N = 32
FLAG_PQC = os.environ.get("FLAG_PQC", "FLAG{lamport_one_time_only}")
ADMIN_MESSAGE = 0xA5A5C3C3


def H(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def int_to_bits(value: int, n: int = N):
    return [(value >> (n - 1 - i)) & 1 for i in range(n)]


_SEED = os.environ.get("LAMPORT_SEED")
if _SEED:
    def _preimage(i: int, b: int) -> bytes:
        return hashlib.sha256(f"{_SEED}:{i}:{b}".encode()).digest()
    SK = [(_preimage(i, 0), _preimage(i, 1)) for i in range(N)]
else:
    SK = [(os.urandom(32), os.urandom(32)) for _ in range(N)]

PK = [(H(SK[i][0]), H(SK[i][1])) for i in range(N)]

# --- One-time-use state -----------------------------------------------------------------
# The whole fix: this key may be used for exactly ONE signature. A lock makes the check
# atomic so two concurrent /sign requests cannot both slip through.
_used_lock = threading.Lock()
_signed_message = None  # the single message this key has signed (None until first use)


def sign(message: int):
    bits = int_to_bits(message)
    return [SK[i][bits[i]].hex() for i in range(N)]


def verify(message: int, sig) -> bool:
    if not isinstance(sig, list) or len(sig) != N:
        return False
    bits = int_to_bits(message)
    try:
        for i in range(N):
            revealed = bytes.fromhex(sig[i])
            if H(revealed) != PK[i][bits[i]]:
                return False
    except (ValueError, TypeError):
        return False
    return True


@app.route("/")
def index():
    return (
        "Week 15 -- Post-Quantum Cryptography lab: Lamport one-time signature (FIXED).\n"
        "This server enforces ONE-TIME use: the key signs at most once; a 2nd /sign -> 403.\n"
        "Endpoints:\n"
        "  POST /sign    {message_hex}        -> Lamport signature (ONCE only, then 403)\n"
        "  POST /verify  {message_hex, sig}   -> {valid: bool}\n"
        "  POST /admin   {sig}                -> flag if sig is valid on the fixed admin message\n"
        "The two-signature key-recovery attack that works on :8100 must FAIL here.\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/pubkey")
def pubkey():
    return jsonify({
        "N": N,
        "admin_message_hex": f"{ADMIN_MESSAGE:08x}",
        "pk": [[a.hex(), b.hex()] for (a, b) in PK],
    })


@app.route("/sign", methods=["POST"])
def sign_endpoint():
    global _signed_message
    body = request.get_json(silent=True) or {}
    message_hex = body.get("message_hex", "")
    try:
        message = int(message_hex, 16)
    except (ValueError, TypeError):
        return jsonify({"error": "message_hex must be a hex string"}), 400
    if message < 0 or message >= (1 << N):
        return jsonify({"error": f"message must fit in {N} bits"}), 400
    # Baseline (shared with vulnerable_app.py): never sign the reserved admin message directly.
    # The ONLY thing that differs between the two apps is the one-time enforcement below -- so a
    # student comparing them sees exactly the variable this week teaches.
    if message == ADMIN_MESSAGE:
        return jsonify({"error": "refusing to sign the reserved admin message"}), 403

    with _used_lock:
        # THE FIX: one-time enforcement. This key signs exactly ONCE. Any second /sign call --
        # even for the same message -- is refused: one-time means one signature, period. (A real
        # client that needs to retry a dropped response must re-request from a FRESH one-time key,
        # never re-use a spent one.)
        if _signed_message is not None:
            return jsonify({
                "error": "one-time key already used",
                "detail": f"this Lamport key already signed 0x{_signed_message:0{N // 4}x}; "
                          "a one-time key must never sign a second message.",
            }), 403
        _signed_message = message
        result = sign(message)

    return jsonify({"message_hex": f"{message:0{N // 4}x}", "sig": result})


@app.route("/verify", methods=["POST"])
def verify_endpoint():
    body = request.get_json(silent=True) or {}
    message_hex = body.get("message_hex", "")
    sig = body.get("sig")
    try:
        message = int(message_hex, 16)
    except (ValueError, TypeError):
        return jsonify({"error": "message_hex must be a hex string"}), 400
    return jsonify({"valid": verify(message, sig)})


@app.route("/admin", methods=["POST"])
def admin():
    body = request.get_json(silent=True) or {}
    sig = body.get("sig")
    if verify(ADMIN_MESSAGE, sig):
        return jsonify({"flag": FLAG_PQC})
    return jsonify({"error": "invalid signature on admin message"}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8101, debug=False)
