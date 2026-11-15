"""Week 10 helper: Bob sends two messages to Alice (hybrid encryption), and Eve listens.

Usage (inside the container, from labs/week10-hybrid-encryption):
    python demo.py good            # Bob uses a NEW nonce for every message
    python demo.py reuse           # Bob uses the SAME nonce for both messages (the bug)
    python demo.py attack good     # Eve tries to read message 2 from the "good" session
    python demo.py attack reuse    # Eve tries to read message 2 from the "reuse" session

How hybrid encryption works here:
  1. Alice makes an RSA key pair and publishes only the PUBLIC key.
  2. Bob makes ONE random AES-256 session key and locks it with Alice's public key (sent once).
  3. Bob encrypts every message with that session key using AES-GCM and a 12-byte nonce.
  4. Alice unlocks the session key with her PRIVATE key, then opens the messages.
Eve only sees what travels on the network: the locked session key, the nonces and the ciphertexts.
She never sees any key. Local demo only. Standard library plus the `cryptography` package.
"""
import os
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MSG1 = b"Hello Alice, this is Bob, report #1"   # a greeting Eve already knows Bob always sends
MSG2 = b"Secret: FLAG{same_nonce_leaks_it}"
TAG_BYTES = 16


def run_session(mode):
    """Bob -> Alice. Returns the two (nonce, ciphertext-with-tag) pairs that travel on the network."""
    alice_private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    alice_public = alice_private.public_key()
    oaep = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)

    session_key = AESGCM.generate_key(bit_length=256)
    locked_key = alice_public.encrypt(session_key, oaep)          # sent to Alice once
    aes = AESGCM(session_key)

    if mode == "reuse":
        nonces = [os.urandom(12)] * 2                              # the SAME nonce for both messages
    else:
        nonces = [os.urandom(12), os.urandom(12)]                  # a NEW nonce for each message
    sent = [(nonce, aes.encrypt(nonce, msg, None)) for nonce, msg in zip(nonces, (MSG1, MSG2))]

    # Alice's side: unlock the session key, then open both messages.
    alice_key = alice_private.decrypt(locked_key, oaep)
    opened = [AESGCM(alice_key).decrypt(n, c, None) for n, c in sent]
    return locked_key, sent, opened


def show_session(mode):
    locked_key, sent, opened = run_session(mode)
    print("Alice made a key pair and published only her PUBLIC key (RSA 2048).")
    print(f"Bob made ONE session key (AES-256) and locked it with Alice's public key: {len(locked_key)} bytes, sent once.")
    for i, (nonce, ct) in enumerate(sent, 1):
        print(f"message {i}: nonce {nonce.hex()}  ciphertext {len(ct) - TAG_BYTES} bytes + {TAG_BYTES}-byte tag")
    print("Alice unlocked the session key with her PRIVATE key and opened both messages:")
    for i, m in enumerate(opened, 1):
        print(f"  message {i} -> {m.decode()}")
    same = sent[0][0] == sent[1][0]
    print("nonces equal? " + ("YES (the same nonce was used twice)" if same else "NO (a new nonce for every message)"))


def attack(mode):
    _, sent, _ = run_session(mode)
    (n1, c1), (n2, c2) = sent
    print("Eve recorded both messages. She has NO key. She only knows that message 1 is Bob's usual greeting:")
    print(f"  known message 1: {MSG1.decode()}")
    print("nonces equal? " + ("YES" if n1 == n2 else "NO"))
    n = min(len(c1), len(c2)) - TAG_BYTES
    guess = bytes(a ^ b ^ k for a, b, k in zip(c1[:n], c2[:n], MSG1))   # c1 xor c2 xor known = message 2
    shown = "".join(chr(b) if 32 <= b < 127 else "?" for b in guess)
    print(f"Eve's reading of message 2: {shown}")
    if guess == MSG2[:n]:
        print("RESULT: Eve read message 2 WITHOUT the key.")
    else:
        print("RESULT: Eve got nothing readable.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 1 and a[0] in ("good", "reuse"):
        show_session(a[0])
    elif len(a) == 2 and a[0] == "attack" and a[1] in ("good", "reuse"):
        attack(a[1])
    else:
        sys.exit(__doc__)
