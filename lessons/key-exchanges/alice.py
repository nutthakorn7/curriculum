"""
Week 5 lab -- Alice, the TCP client.

Connects to PEER_HOST:PEER_PORT (in the vulnerable topology this is `relay`,
not `bob` -- Alice has no way to tell the difference over an unauthenticated
channel). Performs a Diffie-Hellman handshake, derives an AES-256-GCM key
from the shared secret, encrypts a fixed secret message, and sends it.

In "fixed" (authenticated) mode -- SIGNED=1 -- Alice additionally HMAC-signs
her DH public key with a pre-shared AUTH_KEY and verifies the peer's HMAC tag
on their public key before deriving any session key. If verification fails,
Alice prints "AUTH FAILED - ABORTING" and exits nonzero.
"""
import os
import socket
import sys
import time

from common import (
    aes_gcm_encrypt,
    bytes_to_int,
    derive_aes_key,
    get_dh_parameters,
    hmac_pubkey,
    int_to_bytes,
    recv_bytes,
    send_bytes,
    verify_hmac,
)

PEER_HOST = os.environ.get("PEER_HOST", "relay")
PEER_PORT = int(os.environ.get("PEER_PORT", "5000"))
SIGNED = os.environ.get("SIGNED", "").strip() == "1"
AUTH_KEY = os.environ.get("AUTH_KEY", "").encode()
SECRET_MESSAGE = os.environ.get("SECRET_MESSAGE", "the launch code is 4471")

CONNECT_RETRIES = 20
CONNECT_RETRY_DELAY_S = 0.5


def connect_with_retry() -> socket.socket:
    last_exc = None
    for _ in range(CONNECT_RETRIES):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((PEER_HOST, PEER_PORT))
            return sock
        except OSError as exc:
            last_exc = exc
            time.sleep(CONNECT_RETRY_DELAY_S)
    raise ConnectionError(f"could not connect to {PEER_HOST}:{PEER_PORT}: {last_exc}")


def main() -> None:
    if SIGNED and not AUTH_KEY:
        print("AUTH FAILED - ABORTING (no AUTH_KEY configured)", flush=True)
        sys.exit(1)

    print(f"ALICE: connecting to {PEER_HOST}:{PEER_PORT} (SIGNED={SIGNED})", flush=True)
    sock = connect_with_retry()

    try:
        params = get_dh_parameters()
        private_key = params.generate_private_key()
        my_public_numbers = private_key.public_key().public_numbers()
        my_pub_bytes = int_to_bytes(my_public_numbers.y)

        if SIGNED:
            peer_pub_bytes = recv_bytes(sock)
            peer_tag = recv_bytes(sock)

            my_tag = hmac_pubkey(AUTH_KEY, my_pub_bytes)
            send_bytes(sock, my_pub_bytes)
            send_bytes(sock, my_tag)

            if not verify_hmac(AUTH_KEY, peer_pub_bytes, peer_tag):
                print("AUTH FAILED - ABORTING", flush=True)
                sys.exit(1)
        else:
            peer_pub_bytes = recv_bytes(sock)
            send_bytes(sock, my_pub_bytes)

        peer_y = bytes_to_int(peer_pub_bytes)
        from cryptography.hazmat.primitives.asymmetric import dh

        peer_public_numbers = dh.DHPublicNumbers(peer_y, params.parameter_numbers())
        peer_public_key = peer_public_numbers.public_key()

        shared_secret = private_key.exchange(peer_public_key)
        aes_key = derive_aes_key(shared_secret)

        blob = aes_gcm_encrypt(aes_key, SECRET_MESSAGE.encode())
        send_bytes(sock, blob)
        print(f"ALICE: sent encrypted message ({SECRET_MESSAGE!r})", flush=True)
    finally:
        sock.close()


if __name__ == "__main__":
    main()
