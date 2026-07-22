"""
Week 5 lab -- relay, the network attacker.

Alice is configured to connect to `relay` instead of `bob` directly (that is
the whole point: in this lab "the attacker controls the network path", so
whoever Alice thinks is Bob is actually whoever sits on that path). Relay
then connects onward to the real Bob.

Two modes, controlled by the SIGNED env var:

Vulnerable (SIGNED unset/empty):
    Relay performs a FULL machine-in-the-middle attack. It completes an
    entirely independent, unauthenticated DH handshake with Alice (in which
    Relay plays the role of "Bob") AND a second, independent DH handshake
    with the real Bob (in which Relay plays the role of "Alice"). This gives
    Relay two different derived AES keys -- one shared with Alice, one shared
    with Bob -- and neither Alice nor Bob can tell, because plain
    (unauthenticated) DH gives no way to verify who you actually negotiated
    with. Relay decrypts Alice's message with the Alice-side key, prints
    "RELAY INTERCEPTED: <plaintext>", then re-encrypts the same plaintext
    under the Bob-side key and forwards it, so the handshake completes with
    no error on either end -- the attack is completely invisible to Alice
    and Bob.

Fixed (SIGNED=1):
    Alice and Bob authenticate their DH public keys with an HMAC under a
    pre-shared AUTH_KEY that Relay does NOT have. Relay still ATTEMPTS the
    exact same key-substitution attack as in vulnerable mode -- it generates
    its own DH keypairs and tries to splice itself into both handshakes --
    but since it has no AUTH_KEY, it cannot produce a valid HMAC tag for the
    substituted public keys it sends. Alice's and Bob's own verification of
    the peer's tag (see alice.py / bob.py) then fails and each side prints
    "AUTH FAILED - ABORTING" and exits nonzero, refusing to derive a session
    key from an unverified public key. Relay never reaches the point of
    decrypting anything in this mode, so it must never print
    "RELAY INTERCEPTED" here.
"""
import os
import socket
import sys

from common import (
    aes_gcm_decrypt,
    aes_gcm_encrypt,
    bytes_to_int,
    derive_aes_key,
    get_dh_parameters,
    int_to_bytes,
    recv_bytes,
    send_bytes,
)

LISTEN_HOST = os.environ.get("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "5000"))
UPSTREAM_HOST = os.environ.get("UPSTREAM_HOST", "bob")
UPSTREAM_PORT = int(os.environ.get("UPSTREAM_PORT", "5000"))
SIGNED = os.environ.get("SIGNED", "").strip() == "1"


# ---------------------------------------------------------------------------
# Fixed mode: Relay still ATTEMPTS the same active key-substitution attack as
# in vulnerable mode, but it has no AUTH_KEY, so it cannot produce a valid
# HMAC tag for the DH public keys it substitutes. It sends junk tags instead.
# Alice's and Bob's own verification catches this and they abort -- Relay
# never gets far enough to decrypt anything.
# ---------------------------------------------------------------------------

def handle_mitm_signed(alice_conn: socket.socket) -> None:
    from cryptography.hazmat.primitives.asymmetric import dh

    params = get_dh_parameters()

    # --- Relay <-> Alice, with Relay pretending to be Bob. ---
    relay_key_for_alice = params.generate_private_key()
    relay_pub_for_alice = int_to_bytes(relay_key_for_alice.public_key().public_numbers().y)
    junk_tag = os.urandom(32)  # Relay has no AUTH_KEY, so it cannot forge a real tag.

    send_bytes(alice_conn, relay_pub_for_alice)
    send_bytes(alice_conn, junk_tag)

    alice_pub_bytes = recv_bytes(alice_conn)
    _alice_tag = recv_bytes(alice_conn)
    print("RELAY: (fixed mode) attempted DH substitution with Alice (posing as Bob)", flush=True)

    # --- Relay <-> Bob, with Relay pretending to be Alice. ---
    bob_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bob_conn.connect((UPSTREAM_HOST, UPSTREAM_PORT))

    relay_key_for_bob = params.generate_private_key()
    relay_pub_for_bob = int_to_bytes(relay_key_for_bob.public_key().public_numbers().y)

    bob_pub_bytes = recv_bytes(bob_conn)
    _bob_tag = recv_bytes(bob_conn)
    send_bytes(bob_conn, relay_pub_for_bob)
    send_bytes(bob_conn, os.urandom(32))
    print("RELAY: (fixed mode) attempted DH substitution with Bob (posing as Alice)", flush=True)

    # Both Alice and Bob will now fail HMAC verification of Relay's
    # substituted public key and abort -- Relay never receives a ciphertext
    # to decrypt, so it has nothing further to do here.
    alice_conn.close()
    bob_conn.close()


# ---------------------------------------------------------------------------
# Vulnerable mode: full active MITM with two independent DH handshakes.
# ---------------------------------------------------------------------------

def handle_mitm(alice_conn: socket.socket) -> None:
    from cryptography.hazmat.primitives.asymmetric import dh

    params = get_dh_parameters()

    # --- Handshake #1: Relay <-> Alice, with Relay pretending to be Bob. ---
    relay_key_for_alice = params.generate_private_key()
    relay_pub_for_alice = int_to_bytes(relay_key_for_alice.public_key().public_numbers().y)

    send_bytes(alice_conn, relay_pub_for_alice)
    alice_pub_bytes = recv_bytes(alice_conn)
    alice_y = bytes_to_int(alice_pub_bytes)
    alice_public_key = dh.DHPublicNumbers(alice_y, params.parameter_numbers()).public_key()

    shared_with_alice = relay_key_for_alice.exchange(alice_public_key)
    key_with_alice = derive_aes_key(shared_with_alice)
    print("RELAY: completed independent DH handshake with Alice (posing as Bob)", flush=True)

    # --- Handshake #2: Relay <-> Bob, with Relay pretending to be Alice. ---
    bob_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bob_conn.connect((UPSTREAM_HOST, UPSTREAM_PORT))

    relay_key_for_bob = params.generate_private_key()
    relay_pub_for_bob = int_to_bytes(relay_key_for_bob.public_key().public_numbers().y)

    bob_pub_bytes = recv_bytes(bob_conn)
    send_bytes(bob_conn, relay_pub_for_bob)
    bob_y = bytes_to_int(bob_pub_bytes)
    bob_public_key = dh.DHPublicNumbers(bob_y, params.parameter_numbers()).public_key()

    shared_with_bob = relay_key_for_bob.exchange(bob_public_key)
    key_with_bob = derive_aes_key(shared_with_bob)
    print("RELAY: completed independent DH handshake with Bob (posing as Alice)", flush=True)

    # --- Intercept Alice's message, decrypt it, log it, then forward it. ---
    ciphertext_from_alice = recv_bytes(alice_conn)
    plaintext = aes_gcm_decrypt(key_with_alice, ciphertext_from_alice)
    print(f"RELAY INTERCEPTED: {plaintext.decode()}", flush=True)

    forwarded_blob = aes_gcm_encrypt(key_with_bob, plaintext)
    send_bytes(bob_conn, forwarded_blob)

    alice_conn.close()
    bob_conn.close()


def main() -> None:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((LISTEN_HOST, LISTEN_PORT))
    server_sock.listen(5)
    print(
        f"RELAY: listening on {LISTEN_HOST}:{LISTEN_PORT}, "
        f"forwarding to {UPSTREAM_HOST}:{UPSTREAM_PORT} (SIGNED={SIGNED})",
        flush=True,
    )

    while True:
        conn, addr = server_sock.accept()
        print(f"RELAY: connection from {addr}", flush=True)
        try:
            if SIGNED:
                handle_mitm_signed(conn)
            else:
                handle_mitm(conn)
        except Exception as exc:  # noqa: BLE001 -- lab code, log and keep serving
            print(f"RELAY: error handling connection: {exc}", flush=True)
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
