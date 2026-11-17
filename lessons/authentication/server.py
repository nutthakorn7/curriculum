"""
Week 14 lab -- the authentication server (Flask).

One binary, two behaviours, selected by the PAKE environment variable:

VULNERABLE (PAKE unset/empty) -- plain password login:
    POST /login  {username, password}
    The server receives the ACTUAL password in the request body. It LOGS it:
        SERVER SAW PASSWORD: <submitted password>
    then checks it against the stored verifier and returns {"status": "ok"}.
    This models a malicious / compromised / over-logging server harvesting the
    plaintext password. Note: TLS would encrypt this on the wire, but the
    server is the endpoint that TERMINATES the TLS -- so it still sees the
    plaintext. TLS does not protect you from the server itself.

FIXED (PAKE=1) -- challenge-response, password never transmitted:
    GET  /challenge  {username}          -> {"nonce": <hex>, "salt": <hex>}
    POST /login      {username, nonce, proof}
    The client fetches a fresh random nonce, derives verifier = KDF(salt,
    password) LOCALLY, and returns proof = HMAC(verifier, nonce). The server
    recomputes the proof from the verifier it STORED (it never stored the
    password) and compares. The server LOGS only the nonce and proof:
        SERVER SAW: nonce=<hex> proof=<hex>
    -- never the password, because the password never arrives.

HONEST SCOPE: the fixed path proves only "password never transmitted". It is
NOT a full PAKE (no offline-dictionary resistance on the stored verifier, no
mutual authentication). See common.py and README.md.
"""
import os
import secrets

from flask import Flask, jsonify, request

from common import derive_verifier, verify_proof

PAKE = os.environ.get("PAKE", "").strip() == "1"
LISTEN_HOST = os.environ.get("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "8080"))

# The one demo account. This verifier was precomputed for the lab password
# during an imaginary registration step. The fixed server image contains only
# the public salt and password-derived verifier, not the plaintext password.
# This is not a real registration protocol or a production-safe verifier.
DEMO_USERNAME = "alice"
DEMO_SALT = b"week14-demo-salt"
DEMO_VERIFIER = bytes.fromhex(
    "d40d66b95547a1a3526a4d424c693a0ea39e8203234335ce0ba48bc212778524"
)

# Issued challenges: username -> nonce (single-use, popped on /login).
_outstanding_nonces: dict[str, bytes] = {}

app = Flask(__name__)


@app.get("/challenge")
def challenge():
    """FIXED path only: hand out a fresh random nonce + the account's salt.

    The salt is public (the client needs it to derive the same verifier the
    server stored). The nonce is single-use and random per attempt, which is
    what stops an eavesdropper from replaying a captured proof.
    """
    if not PAKE:
        return jsonify({"error": "challenge-response is disabled (PAKE unset)"}), 400

    username = request.args.get("username", "")
    if username != DEMO_USERNAME:
        return jsonify({"error": "unknown user"}), 404

    nonce = secrets.token_bytes(16)
    _outstanding_nonces[username] = nonce
    return jsonify({"nonce": nonce.hex(), "salt": DEMO_SALT.hex()})


@app.post("/login")
def login():
    body = request.get_json(force=True, silent=True)
    if not isinstance(body, dict):
        return jsonify({"status": "denied", "reason": "expected a JSON object"}), 400
    username = body.get("username", "")
    if not isinstance(username, str):
        return jsonify({"status": "denied", "reason": "invalid username"}), 400

    if not PAKE:
        # -------------------------------------------------------------------
        # VULNERABLE: the client sent the actual password. The server sees it
        # in plaintext and -- modelling a compromised / over-logging server --
        # writes it straight to the log before doing anything else.
        # -------------------------------------------------------------------
        password = body.get("password", "")
        if not isinstance(password, str):
            return jsonify({"status": "denied", "reason": "invalid password field"}), 400
        print(f"SERVER SAW PASSWORD: {password}", flush=True)

        ok = (
            username == DEMO_USERNAME
            and secrets.compare_digest(derive_verifier(DEMO_SALT, password.encode()), DEMO_VERIFIER)
        )
        if ok:
            return jsonify({"status": "ok"})
        return jsonify({"status": "denied"}), 401

    # -----------------------------------------------------------------------
    # FIXED: the client sent {username, nonce, proof}. No password anywhere in
    # this request. The server logs only what it actually received -- the
    # nonce and the proof -- and recomputes the expected proof from the
    # verifier it STORED (never the password).
    # -----------------------------------------------------------------------
    nonce_hex = body.get("nonce", "")
    proof_hex = body.get("proof", "")
    if not isinstance(nonce_hex, str) or not isinstance(proof_hex, str):
        return jsonify({"status": "denied", "reason": "invalid nonce/proof fields"}), 400

    try:
        nonce = bytes.fromhex(nonce_hex)
        proof = bytes.fromhex(proof_hex)
    except ValueError:
        return jsonify({"status": "denied", "reason": "malformed nonce/proof"}), 400
    if len(nonce) != 16 or len(proof) != 32:
        return jsonify({"status": "denied", "reason": "wrong nonce/proof length"}), 400

    print(f"SERVER SAW: nonce={nonce.hex()} proof={proof.hex()}", flush=True)

    expected_nonce = _outstanding_nonces.pop(username, None)
    if expected_nonce is None:
        return jsonify({"status": "denied", "reason": "no outstanding challenge"}), 401

    if nonce != expected_nonce:
        return jsonify({"status": "denied", "reason": "stale or wrong nonce"}), 401

    if username == DEMO_USERNAME and verify_proof(DEMO_VERIFIER, nonce, proof):
        return jsonify({"status": "ok"})
    return jsonify({"status": "denied"}), 401


def main() -> None:
    print(f"SERVER: listening on {LISTEN_HOST}:{LISTEN_PORT} (PAKE={PAKE})", flush=True)
    # threaded=False keeps log ordering deterministic for the lab; a single
    # client makes one or two requests, so no concurrency is needed.
    app.run(host=LISTEN_HOST, port=LISTEN_PORT, threaded=False)


if __name__ == "__main__":
    main()
