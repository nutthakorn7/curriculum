"""Deliberately INSECURE -- Week 15 Post-Quantum Cryptography (PQC) lab. Sandbox only.

Hash-based signatures (Lamport, and by extension SPHINCS+) are one of the four PQC families:
they rely ONLY on the (quantum-resistant) one-wayness of a hash, not on factoring/discrete-log,
so Shor's algorithm does not break them. But a Lamport keypair is a ONE-TIME signature (OTS):
it is provably secure if and only if the key signs exactly ONE message. This app violates that
rule -- it holds ONE fixed Lamport keypair and REUSES it on every /sign call (the bug).

Lamport OTS over an N-bit message (this lab signs the message DIRECTLY -- no hashing of the
message first -- so the key-reuse forgery is demonstrable on attacker-controllable bits):
  * Private key sk = 2 random preimages per bit position: sk[i][0], sk[i][1]  (i = 0..N-1)
  * Public key  pk = their hashes:  pk[i][b] = H(sk[i][b])
  * Signature of message m:  for each bit i, reveal the preimage selected by that bit:
        sig[i] = sk[i][ m_i ]
  * Verify:  for each bit i, check  H(sig[i]) == pk[i][ m_i ]

Why reuse is catastrophic (source Q6): signing message M reveals, per bit, the preimage for
that bit's VALUE. Signing the bitwise-complement ~M reveals the OTHER preimage per bit. Between
the two signatures the attacker learns BOTH preimages for every position -- i.e. the entire
private key -- and can forge a valid signature on ANY message, including the admin message.

Endpoints:
  POST /sign   {message_hex}          -> Lamport signature (REUSES the one key -- the bug)
  POST /verify {message_hex, sig}     -> {"valid": bool}
  POST /admin  {sig}                  -> if sig is a valid Lamport sig on the fixed admin
                                          message under pk, return {"flag": FLAG_PQC}; else 403

Compare with fixed_app.py (:8101), which enforces one-time use and refuses a 2nd /sign.
"""
import hashlib
import os

from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Lamport parameters -----------------------------------------------------------------
# N-bit message space. We sign the message DIRECTLY (no pre-hash) so that every message bit is
# attacker-controllable and the key-reuse forgery is clean and demonstrable. N=32 keeps the
# keypair small and the lab fast; the one-time-key lesson is identical for the N=256 used with
# a real hash-then-sign scheme.
N = 32
FLAG_PQC = os.environ.get("FLAG_PQC", "FLAG{lamport_one_time_only}")

# The admin message: a fixed N-bit value meaning "grant_admin". A valid Lamport signature on
# THIS exact message under the server's public key unlocks the flag. Chosen with a mix of 0s
# and 1s so a forger genuinely needs both preimages across many positions (a trivial all-zeros
# or all-ones admin message could be signed from a single non-complementary /sign call).
ADMIN_MESSAGE = 0xA5A5C3C3  # 32-bit: 1010_0101_1010_0101_1100_0011_1100_0011


def H(data: bytes) -> bytes:
    """The lab's one-way function: SHA-256. (Hash-based signatures inherit their security
    directly from this hash's preimage resistance -- which Grover only square-roots, not
    breaks; see the conventional-arm questions on Grover vs. Shor.)"""
    return hashlib.sha256(data).digest()


def int_to_bits(value: int, n: int = N):
    """Most-significant-bit-first list of the n low bits of value."""
    return [(value >> (n - 1 - i)) & 1 for i in range(n)]


# --- One fixed keypair, generated once at startup and REUSED forever (the vulnerability) ---
# sk[i] = (preimage_for_bit_0, preimage_for_bit_1); pk[i] = (H(that), H(that)).
_SEED = os.environ.get("LAMPORT_SEED")  # optional determinism for graders; random otherwise
if _SEED:
    # Derive preimages deterministically from a seed so a grader can reproduce a keypair.
    def _preimage(i: int, b: int) -> bytes:
        return hashlib.sha256(f"{_SEED}:{i}:{b}".encode()).digest()
    SK = [(_preimage(i, 0), _preimage(i, 1)) for i in range(N)]
else:
    SK = [(os.urandom(32), os.urandom(32)) for _ in range(N)]

PK = [(H(SK[i][0]), H(SK[i][1])) for i in range(N)]


def sign(message: int):
    """Return the Lamport signature of an N-bit message: one revealed preimage per bit.
    Serialized as a list of N hex strings (32 bytes each)."""
    bits = int_to_bits(message)
    return [SK[i][bits[i]].hex() for i in range(N)]


def verify(message: int, sig) -> bool:
    """Check that, for every bit i, H(sig[i]) == PK[i][ bit_i ]."""
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
        "Week 15 -- Post-Quantum Cryptography lab: Lamport one-time signature (VULNERABLE).\n"
        "This server REUSES a single Lamport keypair across every /sign call -- the bug.\n"
        "Endpoints:\n"
        "  POST /sign    {message_hex}        -> Lamport signature (N=%d-bit message, no pre-hash)\n"
        "  POST /verify  {message_hex, sig}   -> {valid: bool}\n"
        "  POST /admin   {sig}                -> flag if sig is valid on the fixed admin message\n"
        "Public key is published at GET /pubkey. Admin message = 0x%08X.\n"
        % (N, ADMIN_MESSAGE),
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/pubkey")
def pubkey():
    """Public key is public by definition -- publishing it changes nothing about security
    (that is the whole point of a signature scheme). The attack does NOT use this endpoint;
    it recovers the PRIVATE key from two reused signatures."""
    return jsonify({
        "N": N,
        "admin_message_hex": f"{ADMIN_MESSAGE:08x}",
        "pk": [[a.hex(), b.hex()] for (a, b) in PK],
    })


@app.route("/sign", methods=["POST"])
def sign_endpoint():
    body = request.get_json(silent=True) or {}
    message_hex = body.get("message_hex", "")
    try:
        message = int(message_hex, 16)
    except (ValueError, TypeError):
        return jsonify({"error": "message_hex must be a hex string"}), 400
    if message < 0 or message >= (1 << N):
        return jsonify({"error": f"message must fit in {N} bits"}), 400
    # Baseline (shared with fixed_app.py): never sign the reserved admin message directly --
    # otherwise the flag is a one-line curl and the Lamport lesson is moot. The attack does NOT
    # need this: it signs a message and its complement (neither is admin), recovers the private
    # key, and forges the admin signature OFFLINE.
    if message == ADMIN_MESSAGE:
        return jsonify({"error": "refusing to sign the reserved admin message"}), 403
    # THE BUG: no one-time enforcement -- the same key signs every OTHER message we are asked to
    # sign, so an attacker can collect a message and its complement and recover the whole key.
    return jsonify({"message_hex": f"{message:0{N // 4}x}", "sig": sign(message)})


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
    # A valid Lamport signature on the fixed admin message == proof the caller holds the key.
    if verify(ADMIN_MESSAGE, sig):
        return jsonify({"flag": FLAG_PQC})
    return jsonify({"error": "invalid signature on admin message"}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8100, debug=False)
