"""
Shared helpers for the Week 5 Diffie-Hellman MITM lab.

Provides:
- The standard DH group RFC3526 MODP Group 14 (2048-bit safe prime), used by
  all three services so their DH math is compatible.
- Length-prefixed framing helpers for sending bytes over a raw TCP socket.
- AES-256-GCM encrypt/decrypt helpers using a key derived from the DH shared
  secret (SHA-256 of the raw shared secret bytes).
- HMAC helpers used only in "fixed" (authenticated) mode to sign/verify DH
  public keys with a pre-shared key that the relay does not know.
"""
import hashlib
import hmac
import os
import struct

from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# RFC3526, Section 3 -- "1536-bit MODP Group" is Group 5; this is Group 14,
# the 2048-bit MODP group. Verified programmatically to be a 2048-bit safe
# prime (p prime and (p-1)/2 prime) before being committed here.
P_HEX = (
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD"
    "129024E088A67CC74020BBEA63B139B22514A08798E3404"
    "DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C"
    "245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406"
    "B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE"
    "45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD"
    "24CF5F83655D23DCA3AD961C62F356208552BB9ED529077"
    "096966D670C354E4ABC9804F1746C08CA18217C32905E46"
    "2E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF"
    "06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68"
    "FFFFFFFFFFFFFFFF"
)

G = 2

_P_INT = int(P_HEX, 16)


def get_dh_parameters() -> dh.DHParameters:
    """Return DH parameters built from the RFC3526 Group 14 prime/generator."""
    pn = dh.DHParameterNumbers(_P_INT, G)
    return pn.parameters()


# ---------------------------------------------------------------------------
# Socket framing helpers: every "message" on the wire is a 4-byte big-endian
# length prefix followed by that many bytes of payload.
# ---------------------------------------------------------------------------

def send_bytes(sock, data: bytes) -> None:
    sock.sendall(struct.pack(">I", len(data)) + data)


def recv_exact(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("peer closed connection unexpectedly")
        buf += chunk
    return buf


def recv_bytes(sock) -> bytes:
    (length,) = struct.unpack(">I", recv_exact(sock, 4))
    return recv_exact(sock, length)


def int_to_bytes(n: int) -> bytes:
    length = (n.bit_length() + 7) // 8
    return n.to_bytes(length, "big")


def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


# ---------------------------------------------------------------------------
# Key derivation / AEAD helpers
# ---------------------------------------------------------------------------

def derive_aes_key(shared_secret_bytes: bytes) -> bytes:
    """Derive a 256-bit AES key from the raw DH shared secret via SHA-256."""
    return hashlib.sha256(shared_secret_bytes).digest()


def aes_gcm_encrypt(key: bytes, plaintext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ct


def aes_gcm_decrypt(key: bytes, blob: bytes) -> bytes:
    nonce, ct = blob[:12], blob[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None)


# ---------------------------------------------------------------------------
# HMAC helpers (used only in "fixed"/authenticated mode)
# ---------------------------------------------------------------------------

def hmac_pubkey(auth_key: bytes, pubkey_bytes: bytes) -> bytes:
    """Compute HMAC-SHA256(auth_key, pubkey_bytes) -- authenticates a DH
    public key so a MITM without auth_key cannot substitute its own."""
    return hmac.new(auth_key, pubkey_bytes, hashlib.sha256).digest()


def verify_hmac(auth_key: bytes, pubkey_bytes: bytes, tag: bytes) -> bool:
    expected = hmac_pubkey(auth_key, pubkey_bytes)
    return hmac.compare_digest(expected, tag)
