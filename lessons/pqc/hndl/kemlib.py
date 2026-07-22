"""Shared crypto helpers for the Harvest-Now-Decrypt-Later (HNDL) lab.

TEACHING SIMULATION — sandbox only, never real crypto. Two deliberate shrinks, both stated loudly
so students know exactly what is real and what is modelled:

  1. The "classical" KEM is textbook RSA with a DELIBERATELY SMALL modulus (default 64-bit `n`).
     A real ECDH/RSA key exchange uses 256/3072-bit parameters that no classical computer can
     break. We shrink it ONLY so the "a future quantum computer breaks the classical half" step
     is demonstrable on a laptop *today* (factoring a 64-bit n takes well under a second). The
     lesson — recorded traffic becomes readable once its key-exchange primitive falls — is
     identical at real sizes; only the wall-clock of the break changes.

  2. The "PQC" half of the hybrid is REAL ML-KEM-512 (NIST FIPS 203) via the pure-Python `kyber-py`
     — genuinely lattice-based, not a stand-in. Its private key never appears in the captured
     transcript, so an attacker who breaks the small RSA half still cannot recover the ML-KEM
     shared secret.

The point the lab makes is structural and true at any size: a hybrid session key derived from TWO
independent shared secrets stays confidential as long as EITHER KEM holds — so breaking the
classical half alone is not enough.
"""
import hashlib
import secrets

from sympy import randprime, factorint
from Crypto.Cipher import AES

RSA_BITS = 64  # size of the small "classical" modulus — breakable on a laptop, see module docstring
E = 65537


# ---- small classical RSA-KEM: the quantum-breakable half --------------------------------------
def gen_small_rsa(bits=RSA_BITS):
    """Return (n, e, d) for a small textbook-RSA modulus. Private d is the server's secret."""
    half = bits // 2
    p = randprime(2 ** (half - 1), 2 ** half)
    q = randprime(2 ** (half - 1), 2 ** half)
    while q == p:
        q = randprime(2 ** (half - 1), 2 ** half)
    n = p * q
    d = pow(E, -1, (p - 1) * (q - 1))
    return n, E, d


def rsa_encaps(n, e):
    """Encapsulate: pick a random secret s, return (s, ciphertext = s^e mod n)."""
    s = secrets.randbelow(n - 2) + 2
    return s, pow(s, e, n)


def rsa_break(n, e, kem_ct):
    """The 'quantum arrives later' step: factor the small n, recover d, decapsulate s.
    This is exactly the classical break a large quantum computer would perform via Shor."""
    primes = [pr for pr, mult in factorint(n).items() for _ in range(mult)]
    p, q = primes[0], primes[1]
    d = pow(e, -1, (p - 1) * (q - 1))
    s = pow(kem_ct, d, n)
    return s, (p, q)


def _int_bytes(x, n):
    return x.to_bytes((n.bit_length() + 7) // 8, "big")


# ---- key derivation + authenticated encryption ------------------------------------------------
def kdf(*parts):
    """Derive a 32-byte session key from one or more shared secrets (length-prefixed, order-fixed).
    Hybrid = pass BOTH the classical and the ML-KEM secret; classical-only = pass just the one."""
    h = hashlib.sha256()
    for p in parts:
        h.update(len(p).to_bytes(4, "big"))
        h.update(p)
    return h.digest()


def classical_secret_bytes(s, n):
    return _int_bytes(s, n)


def seal(key, msg):
    """AES-256-GCM seal. Returns (nonce, ciphertext||tag)."""
    nonce = secrets.token_bytes(12)
    ct, tag = AES.new(key, AES.MODE_GCM, nonce=nonce).encrypt_and_digest(msg)
    return nonce, ct + tag


def unseal(key, nonce, blob):
    """AES-256-GCM open. Raises ValueError if the key is wrong (auth-tag mismatch) — which is
    exactly what happens to an attacker who recovered only the classical half of a hybrid key."""
    ct, tag = blob[:-16], blob[-16:]
    return AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)
