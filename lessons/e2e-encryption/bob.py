"""
Week 13 lab -- Bob, the message *recipient*.

Bob talks only to the server (never directly to Alice -- that is the premise:
they communicate through a provider). Two modes, chosen by the E2E env var:

VULNERABLE (E2E unset):
    Bob does nothing special. He waits for the server to have a message, then
    GET /fetch and reads the plaintext directly:
        BOB RECEIVED: meet at pier 39 at midnight
    But note: the server already logged that same plaintext (SERVER SAW: ...).
    The provider read the message too.

FIXED (E2E=1):
    Bob generates an RSA keypair IN MEMORY at startup (no key touches disk),
    publishes the PUBLIC key via POST /pubkey, then waits for and fetches the
    ciphertext and decrypts it CLIENT-SIDE with his private key:
        BOB DECRYPTED: meet at pier 39 at midnight
    The server only ever saw base64 ciphertext -- it could not read this.

Both modes use two layers of waiting: (1) connection retry until the server
is listening, and (2) application-level polling of GET /fetch until a message
exists (the server returns 404 until Alice has sent). depends_on only waits
for the container to *start*, not for the message to be *present*.
"""
import os
import sys
import time

import requests

from common import generate_rsa_keypair, hybrid_decrypt, public_key_to_b64

SERVER = os.environ.get("SERVER_URL", "http://server:8080")
E2E = os.environ.get("E2E", "").strip() == "1"

CONNECT_RETRIES = 60
POLL_RETRIES = 60
RETRY_DELAY_S = 0.5


def wait_for_server() -> None:
    """Layer 1: retry until the server process is up and answering."""
    for _ in range(CONNECT_RETRIES):
        try:
            requests.get(f"{SERVER}/", timeout=2)
            return
        except requests.RequestException:
            time.sleep(RETRY_DELAY_S)
    raise ConnectionError(f"server never came up at {SERVER}")


def poll_for_message() -> str:
    """Layer 2: poll GET /fetch until a message exists (404 until then)."""
    for _ in range(POLL_RETRIES):
        resp = requests.get(f"{SERVER}/fetch", timeout=2)
        if resp.status_code == 200:
            return resp.json()["payload"]
        time.sleep(RETRY_DELAY_S)
    raise TimeoutError("no message appeared on the server in time")


def main() -> None:
    print(f"BOB: starting (E2E={E2E}), server at {SERVER}", flush=True)
    wait_for_server()

    if E2E:
        # Generate keypair in memory and publish the PUBLIC half so Alice can
        # encrypt to us. The private key never leaves this process.
        private_key, public_key = generate_rsa_keypair()
        requests.post(
            f"{SERVER}/pubkey",
            json={"pubkey": public_key_to_b64(public_key)},
            timeout=5,
        )
        print("BOB: published my public key, waiting for a message", flush=True)

        blob_b64 = poll_for_message()
        plaintext = hybrid_decrypt(private_key, blob_b64)
        print(f"BOB DECRYPTED: {plaintext.decode()}", flush=True)
    else:
        print("BOB: waiting for a message (no E2EE)", flush=True)
        payload = poll_for_message()
        # In vulnerable mode the payload IS the plaintext -- the server (and
        # anyone who read its logs) already saw exactly this.
        print(f"BOB RECEIVED: {payload}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
