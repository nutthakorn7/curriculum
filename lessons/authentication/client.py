"""
Week 14 lab -- the login client.

Runs the flow that matches the server's mode (selected by the same PAKE env
var so the compose file drives both ends), then prints "LOGIN OK" on success.

VULNERABLE (PAKE unset): POST /login {username, password}. The client hands
the server the actual password -- which the server then logs. This is what a
normal "send my password to log in" form does; TLS would hide it on the wire
but not from the server itself.

FIXED (PAKE=1): the client
    1. GET /challenge?username=... -> receives {nonce, salt}
    2. derives verifier = KDF(salt, password) LOCALLY (password never leaves)
    3. computes proof = HMAC(verifier, nonce)
    4. POST /login {username, nonce, proof}
The password is never put into any request. The client proves it KNOWS the
password without transmitting it.

HONEST SCOPE: this fixed flow demonstrates only "password never transmitted".
It is not a full PAKE (no offline-dictionary resistance on the stored
verifier, no mutual authentication of the server). See README.md.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

from common import compute_proof, derive_verifier

PAKE = os.environ.get("PAKE", "").strip() == "1"
SERVER_HOST = os.environ.get("SERVER_HOST", "server")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
USERNAME = os.environ.get("USERNAME", "alice")
PASSWORD = os.environ.get("PASSWORD", "correct-horse-battery")

BASE = f"http://{SERVER_HOST}:{SERVER_PORT}"
CONNECT_RETRIES = 30
CONNECT_RETRY_DELAY_S = 0.5


def _get(path: str) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=5) as resp:
        return json.loads(resp.read().decode())


def _post_json(path: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"raw": body}


def wait_for_server() -> None:
    """Block until the Flask server is accepting connections."""
    last_exc = None
    for _ in range(CONNECT_RETRIES):
        try:
            urllib.request.urlopen(BASE + "/challenge?username=__probe__", timeout=2)
            return
        except urllib.error.HTTPError:
            # Any HTTP response (even 400/404) means the server is up.
            return
        except (urllib.error.URLError, OSError) as exc:
            last_exc = exc
            time.sleep(CONNECT_RETRY_DELAY_S)
    raise ConnectionError(f"could not reach {BASE}: {last_exc}")


def run_vulnerable() -> None:
    print(f"CLIENT: plain-password login to {BASE} as {USERNAME!r} (PAKE=False)", flush=True)
    # The client puts the actual password in the request body. This is the
    # whole problem: the server (which terminates TLS) now holds the plaintext.
    status, body = _post_json("/login", {"username": USERNAME, "password": PASSWORD})
    if status == 200 and body.get("status") == "ok":
        print("LOGIN OK", flush=True)
    else:
        print(f"LOGIN FAILED ({status}): {body}", flush=True)
        sys.exit(1)


def run_fixed() -> None:
    print(f"CLIENT: challenge-response login to {BASE} as {USERNAME!r} (PAKE=True)", flush=True)

    # 1. Ask the server for a fresh nonce (and the public salt for our account).
    chal = _get(f"/challenge?username={USERNAME}")
    nonce = bytes.fromhex(chal["nonce"])
    salt = bytes.fromhex(chal["salt"])

    # 2. Derive the verifier LOCALLY from the password. The password stays on
    #    this machine -- it is never placed in any request.
    verifier = derive_verifier(salt, PASSWORD.encode())

    # 3. Prove knowledge of the password by HMAC-ing the nonce under the
    #    verifier. Only the nonce and this proof ever go on the wire.
    proof = compute_proof(verifier, nonce)

    status, body = _post_json(
        "/login",
        {"username": USERNAME, "nonce": nonce.hex(), "proof": proof.hex()},
    )
    if status == 200 and body.get("status") == "ok":
        print("LOGIN OK", flush=True)
    else:
        print(f"LOGIN FAILED ({status}): {body}", flush=True)
        sys.exit(1)


def main() -> None:
    wait_for_server()
    if PAKE:
        run_fixed()
    else:
        run_vulnerable()


if __name__ == "__main__":
    main()
