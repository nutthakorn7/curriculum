"""
Week 13 lab -- Alice, the message *sender*.

Alice talks only to the server (never directly to Bob). What she sends decides
whether the provider can read the message. Two modes, chosen by the E2E env var:

VULNERABLE (E2E unset):
    Alice sends the raw plaintext secret straight to POST /send. The server
    stores and logs it verbatim -- so the provider (and anyone reading the
    server logs) sees "meet at pier 39 at midnight". This models a chat app
    that uses HTTPS in transit but keeps plaintext on the server.

FIXED (E2E=1):
    Alice first waits for Bob to publish his public key (GET /pubkey returns
    404 until then), fetches it, encrypts the secret CLIENT-SIDE with hybrid
    encryption (AES-256-GCM + RSA-OAEP key wrap), and sends only the resulting
    base64 ciphertext to POST /send. The server stores and logs only opaque
    gibberish -- it never sees the plaintext. Only Bob, holding the matching
    private key, can decrypt.

Two layers of waiting, as in bob.py: (1) connection retry until the server is
up, and (2) application-level polling of GET /pubkey until Bob has published
(fixed mode only).
"""
import os
import sys
import time

import requests

from common import hybrid_encrypt, public_key_from_b64

SERVER = os.environ.get("SERVER_URL", "http://server:8080")
E2E = os.environ.get("E2E", "").strip() == "1"
SECRET_MESSAGE = os.environ.get("SECRET_MESSAGE", "meet at pier 39 at midnight")

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


def poll_for_pubkey() -> str:
    """Layer 2: poll GET /pubkey until Bob has published (404 until then)."""
    for _ in range(POLL_RETRIES):
        resp = requests.get(f"{SERVER}/pubkey", timeout=2)
        if resp.status_code == 200:
            return resp.json()["pubkey"]
        time.sleep(RETRY_DELAY_S)
    raise TimeoutError("bob never published a public key in time")


def main() -> None:
    print(f"ALICE: starting (E2E={E2E}), server at {SERVER}", flush=True)
    wait_for_server()

    if E2E:
        # Fetch Bob's public key and encrypt to it. The server never receives
        # the plaintext -- only the ciphertext envelope.
        bob_pub_b64 = poll_for_pubkey()
        bob_public_key = public_key_from_b64(bob_pub_b64)
        payload = hybrid_encrypt(bob_public_key, SECRET_MESSAGE.encode())
        print("ALICE: encrypted the secret to bob's public key (client-side)", flush=True)
    else:
        # No E2EE: hand the server the plaintext directly. It will log it.
        payload = SECRET_MESSAGE
        print("ALICE: sending the raw plaintext (no E2EE)", flush=True)

    requests.post(f"{SERVER}/send", json={"payload": payload}, timeout=5)
    print("ALICE: message sent", flush=True)


if __name__ == "__main__":
    sys.exit(main())
