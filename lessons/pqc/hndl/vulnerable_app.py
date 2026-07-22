"""Deliberately VULNERABLE-to-the-future -- Week 15 PQC lab: Harvest Now, Decrypt Later. Sandbox only.

The scenario: a secure channel establishes a session key with a SINGLE classical KEM (here small
textbook RSA -- standing in for today's ECDH/RSA), then seals a secret message (containing the
flag) under that key with AES-256-GCM. On startup the server performs this exchange ONCE and keeps
ONLY the transcript a passive eavesdropper on the wire would have seen -- it discards the private
key and the session key, exactly as if you were sniffing someone else's traffic today. The captured
transcript is served at /capture.

Why this is "vulnerable" even though the traffic IS encrypted: the security of the session rests
entirely on the classical KEM. The day a large quantum computer can run Shor's algorithm (or, in
this lab, the day you factor the deliberately-small n), the shared secret falls out of the captured
`kem_ct`, the session key is re-derived, and the AES-GCM message decrypts. That is
"harvest now, decrypt later": record the ciphertext today, decrypt it whenever the KEM breaks.
Nothing about the message needs to be attacked -- only the key exchange that protected it.

The break is done OFFLINE by exploit.py (factor n -> recover s -> derive key -> decrypt). There is
deliberately no decrypt endpoint here: the whole point is that the attacker needs nothing from the
server after the capture.

Compare with fixed_app.py (:8121), whose /capture uses a HYBRID key (classical + real ML-KEM), so
breaking the classical half alone recovers nothing.

Endpoints:
  GET /          -> human-readable description
  GET /capture   -> the sniffable transcript: {n, e, kem_ct, aes_nonce, aes_ct}  (all hex/int)
"""
import os

from flask import Flask, jsonify

import kemlib

app = Flask(__name__)
FLAG_HNDL = os.environ.get("FLAG_HNDL", "FLAG{harvest_now_decrypt_later}")


def _make_capture():
    # One key exchange, "in the past". Keep only what a wire eavesdropper saw.
    n, e, _d = kemlib.gen_small_rsa()
    s, kem_ct = kemlib.rsa_encaps(n, e)
    session_key = kemlib.kdf(kemlib.classical_secret_bytes(s, n))
    nonce, blob = kemlib.seal(session_key, FLAG_HNDL.encode())
    return {"n": n, "e": e, "kem_ct": kem_ct, "aes_nonce": nonce.hex(), "aes_ct": blob.hex()}


CAPTURE = _make_capture()  # frozen at boot; re-`docker compose up` for a fresh key


@app.route("/")
def index():
    return (
        "Week 15 PQC lab -- Harvest Now, Decrypt Later (VULNERABLE channel, single classical KEM).\n"
        "GET /capture to sniff the session transcript, then break it offline with exploit.py.\n"
    )


@app.route("/capture")
def capture():
    # Everything a passive eavesdropper on the wire would have. The session key is NOT here --
    # but it is fully recoverable from these fields once the small RSA modulus is factored.
    return jsonify(CAPTURE)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8120)
