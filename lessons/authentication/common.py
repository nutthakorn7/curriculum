"""
Shared helpers for the Week 14 user-authentication lab.

The lab contrasts two ways a client can "log in" to a server:

- VULNERABLE (plain password submission): the client sends the actual
  password in the request body. Even over TLS, the *server* then holds the
  plaintext password in memory / logs / request handlers -- a malicious,
  compromised, or over-logging server harvests it. This models real password
  harvesting by the endpoint you are trusting.

- FIXED (challenge-response, PAKE-flavoured): the server stores only a
  *verifier* v = KDF(salt, password) -- never the password. To log in, the
  client fetches a fresh random nonce (the "challenge") and returns a proof =
  HMAC(v, nonce). The server recomputes the same HMAC from its stored verifier
  and compares. The password itself is never transmitted, so a compromised or
  logging server never sees it.

HONEST SCOPE (read this): the fixed side here demonstrates ONLY the
"password is never transmitted" property. It is a deliberately simplified
challenge-response, NOT a full PAKE. A real PAKE (SRP, OPAQUE) additionally
(a) makes the stored verifier resistant to offline dictionary attacks if the
server database leaks, and (b) provides mutual authentication (the client also
verifies it is talking to the genuine server). This demo provides neither of
those extra properties -- do not present it as a complete PAKE. See README.md
and the worksheet for where this simplification matters.
"""
import hashlib
import hmac
import struct


# ---------------------------------------------------------------------------
# Verifier / KDF helpers
# ---------------------------------------------------------------------------
#
# derive_verifier() is the server-side key-derivation function. In a real
# system this would be bcrypt/argon2 with a per-user salt and a high work
# factor (see Week 2). Here we use a salted SHA-256 purely to keep the demo
# self-contained and fast -- the lesson this week is "the password is never
# sent", NOT "this KDF resists offline cracking". The worksheet answer key is
# explicit that a real deployment MUST use a slow, memory-hard KDF here.

def derive_verifier(salt: bytes, password: bytes) -> bytes:
    """Return the stored verifier v = KDF(salt, password).

    The server stores only (salt, v). It never stores or logs the password.
    """
    return hashlib.sha256(salt + password).digest()


def compute_proof(verifier: bytes, nonce: bytes) -> bytes:
    """Client- and server-side proof = HMAC-SHA256(verifier, nonce).

    The client computes this from verifier = KDF(salt, password) it derived
    locally; the server recomputes it from the verifier it has stored. If the
    two match, the client has demonstrated knowledge of the password WITHOUT
    ever sending the password itself -- only this proof and the public nonce
    ever go on the wire.
    """
    return hmac.new(verifier, nonce, hashlib.sha256).digest()


def verify_proof(verifier: bytes, nonce: bytes, proof: bytes) -> bool:
    """Constant-time comparison of a received proof against the expected one."""
    expected = compute_proof(verifier, nonce)
    return hmac.compare_digest(expected, proof)


# ---------------------------------------------------------------------------
# Length-prefixed socket framing (unused by the HTTP path, kept for parity
# with the rest of the course's lab helpers and any raw-socket experiments).
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
