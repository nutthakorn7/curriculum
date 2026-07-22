"""
Week 5 lab -- Bob, the TCP server.

Performs a Diffie-Hellman handshake with whoever connects (in the vulnerable
topology, that is actually `relay`, not `alice`), derives an AES-256-GCM key
from the shared secret, reads one encrypted message, decrypts it, and prints
"BOB RECEIVED: <plaintext>".

In "fixed" (authenticated) mode -- SIGNED=1 -- Bob additionally HMAC-signs his
DH public key with a pre-shared AUTH_KEY and verifies the peer's HMAC tag on
their public key before deriving any session key. If verification fails, Bob
prints "AUTH FAILED - ABORTING" and exits nonzero, refusing to proceed with a
handshake that may have been tampered with by a relay/MITM.
"""
import os
import socket
import sys

from common import (
    aes_gcm_decrypt,
    bytes_to_int,
    derive_aes_key,
    get_dh_parameters,
    hmac_pubkey,
    int_to_bytes,
    recv_bytes,
    send_bytes,
    verify_hmac,
)

LISTEN_HOST = os.environ.get("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "5000"))
SIGNED = os.environ.get("SIGNED", "").strip() == "1"
AUTH_KEY = os.environ.get("AUTH_KEY", "").encode()


def handle_connection(conn: socket.socket) -> None:
    params = get_dh_parameters()
    private_key = params.generate_private_key()
    my_public_numbers = private_key.public_key().public_numbers()
    my_pub_bytes = int_to_bytes(my_public_numbers.y)

    if SIGNED:
        my_tag = hmac_pubkey(AUTH_KEY, my_pub_bytes)
        send_bytes(conn, my_pub_bytes)
        send_bytes(conn, my_tag)

        peer_pub_bytes = recv_bytes(conn)
        peer_tag = recv_bytes(conn)

        if not verify_hmac(AUTH_KEY, peer_pub_bytes, peer_tag):
            print("AUTH FAILED - ABORTING", flush=True)
            sys.exit(1)
    else:
        send_bytes(conn, my_pub_bytes)
        peer_pub_bytes = recv_bytes(conn)

    peer_y = bytes_to_int(peer_pub_bytes)
    from cryptography.hazmat.primitives.asymmetric import dh

    peer_public_numbers = dh.DHPublicNumbers(peer_y, params.parameter_numbers())
    peer_public_key = peer_public_numbers.public_key()

    shared_secret = private_key.exchange(peer_public_key)
    aes_key = derive_aes_key(shared_secret)

    ciphertext_blob = recv_bytes(conn)
    plaintext = aes_gcm_decrypt(aes_key, ciphertext_blob)
    print(f"BOB RECEIVED: {plaintext.decode()}", flush=True)


def main() -> None:
    if SIGNED and not AUTH_KEY:
        print("AUTH FAILED - ABORTING (no AUTH_KEY configured)", flush=True)
        sys.exit(1)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((LISTEN_HOST, LISTEN_PORT))
    server_sock.listen(5)
    print(f"BOB: listening on {LISTEN_HOST}:{LISTEN_PORT} (SIGNED={SIGNED})", flush=True)

    while True:
        conn, addr = server_sock.accept()
        print(f"BOB: connection from {addr}", flush=True)
        try:
            handle_connection(conn)
        except SystemExit:
            raise
        except Exception as exc:  # noqa: BLE001 -- lab code, log and keep serving
            print(f"BOB: error handling connection: {exc}", flush=True)
        finally:
            conn.close()


if __name__ == "__main__":
    main()
