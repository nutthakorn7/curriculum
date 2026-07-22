"""
Shared helpers for the Week 13 End-to-End Encryption (E2EE) lab.

The lesson of this week is *where* the plaintext lives. A messaging server
(server.py) sits between two clients (alice.py sends, bob.py receives). The
server always logs what it stores -- "SERVER SAW: <payload>". What differs
between the two modes is *what alice puts in that payload*:

- VULNERABLE (E2E unset): alice sends the raw plaintext secret. The server --
  running byte-for-byte the *same* code -- stores and logs the plaintext.
  This models a provider that uses HTTPS in transit but can still read every
  message it relays (server-can-read).

- FIXED (E2E=1): bob publishes an RSA public key; alice fetches it and
  encrypts the secret CLIENT-SIDE (AES-256-GCM for the message, RSA-OAEP to
  wrap the AES key -- "hybrid" encryption) before sending. The server stores
  and logs only base64 ciphertext; bob decrypts client-side. The server never
  sees the plaintext (server-cannot-read = true end-to-end encryption).

This module provides the crypto helpers shared by all three services so the
AES-GCM / hybrid-wrap logic lives in exactly one place. There is NO real TLS
in this lab: vulnerable mode *models* "HTTPS-but-provider-reads-plaintext".
The point being taught is that transport encryption (TLS/HTTPS) is a
different guarantee from end-to-end encryption -- see README.
"""
import base64
import json
import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ---------------------------------------------------------------------------
# base64 helpers -- everything on the wire / in server logs is text.
# ---------------------------------------------------------------------------

def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def b64d(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))


# ---------------------------------------------------------------------------
# RSA keypair (used by bob only, in fixed mode). Generated fresh in-memory at
# container startup -- NO private key is ever written to disk or shipped in
# the repo.
# ---------------------------------------------------------------------------

def generate_rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


def public_key_to_b64(public_key) -> str:
    """Serialize an RSA public key to base64(PEM) for publishing via /pubkey."""
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return b64e(pem)


def public_key_from_b64(b64_pem: str):
    pem = b64d(b64_pem)
    return serialization.load_pem_public_key(pem)


# ---------------------------------------------------------------------------
# Hybrid encryption: AES-256-GCM for the message body, RSA-OAEP to wrap the
# random AES key. This is exactly how real E2EE messengers structure a
# message -- a fresh symmetric key per message, wrapped to the recipient's
# public key. The output is a small JSON object, base64-encoded so it is a
# single opaque string the server can store and log without understanding it.
# ---------------------------------------------------------------------------

def hybrid_encrypt(recipient_public_key, plaintext: bytes) -> str:
    aes_key = os.urandom(32)          # fresh AES-256 key, per message
    nonce = os.urandom(12)
    ct = AESGCM(aes_key).encrypt(nonce, plaintext, None)

    wrapped_key = recipient_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    envelope = {
        "enc_key": b64e(wrapped_key),   # AES key, RSA-OAEP wrapped to bob
        "nonce": b64e(nonce),
        "ct": b64e(ct),                 # AES-GCM ciphertext + tag
    }
    return b64e(json.dumps(envelope).encode("utf-8"))


def hybrid_decrypt(recipient_private_key, blob_b64: str) -> bytes:
    envelope = json.loads(b64d(blob_b64).decode("utf-8"))

    aes_key = recipient_private_key.decrypt(
        b64d(envelope["enc_key"]),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    nonce = b64d(envelope["nonce"])
    ct = b64d(envelope["ct"])
    return AESGCM(aes_key).decrypt(nonce, ct, None)
