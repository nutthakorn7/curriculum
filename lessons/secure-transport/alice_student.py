"""
Week 12 lab -- YOUR TASK (the one place in this course where you write the fix
yourself, not just confirm a pre-built one).

Everything in this file works except ONE function: `build_client_context()`.
Right now it deliberately raises NotImplementedError. Your job is to replace
that with real code so Alice PROPERLY validates the server's TLS certificate
before sending her secret.

Your fix must, against the SAME self-signed impostor `mitm` this lab's
vulnerable/fixed pair already uses:
  1. Trust ONLY the demo CA (its cert is at CERT_DIR/ca.crt, written by
     gen_certs.py at container startup) as a root of trust -- never the
     impostor's own self-signed cert.
  2. Verify the certificate CHAIN (the presented cert must be signed by that
     CA -- the impostor's is not, so this must fail against it).
  3. Verify the HOSTNAME (the cert must actually be issued to "bob", not just
     signed by a CA -- SERVER_HOSTNAME below is what you must check against).

Hint: you do not need to hand-roll chain or hostname validation yourself --
`ssl.create_default_context(cafile=...)` already performs both correctly by
default. Read `alice.py` (the reference vulnerable/fixed pair for this same
lab) for the shape of a working, secure client context -- but do not just
copy its `if VERIFY:` branch verbatim without understanding why each line is
there; you are expected to be able to explain your own code in the worksheet
and in a viva spot-check.

When you're done:
    docker compose -f docker-compose.student-task.yml up --build
Expect Alice to print "CERT VERIFICATION FAILED - ABORTING" (rejecting the
impostor) -- NOT "TLS handshake succeeded" and NOT a Python traceback. If you
see a traceback, `build_client_context()` still isn't finished.
"""
import os
import socket
import ssl
import sys
import time

PEER_HOST = os.environ.get("PEER_HOST", "mitm")
PEER_PORT = int(os.environ.get("PEER_PORT", "8443"))
SERVER_HOSTNAME = os.environ.get("SERVER_HOSTNAME", "bob")
CERT_DIR = os.environ.get("CERT_DIR", "/certs")
SECRET_MESSAGE = os.environ.get("SECRET_MESSAGE", "the vault code is 7731")

CONNECT_RETRIES = 20
CONNECT_RETRY_DELAY_S = 0.5


def wait_for_ca_cert() -> str:
    """Wait until the demo CA cert is readable in the shared volume (provided,
    do not modify)."""
    ca_path = os.path.join(CERT_DIR, "ca.crt")
    for _ in range(CONNECT_RETRIES):
        if os.path.exists(ca_path) and os.path.getsize(ca_path) > 0:
            return ca_path
        time.sleep(CONNECT_RETRY_DELAY_S)
    raise FileNotFoundError(f"CA cert never appeared at {ca_path}")


def connect_with_retry() -> socket.socket:
    """Provided, do not modify."""
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


def build_client_context() -> ssl.SSLContext:
    # ============================ YOUR TASK ==================================
    # Delete the `raise NotImplementedError(...)` line below and write your fix
    # in its place. Your context must end up with check_hostname=True and
    # verify_mode=CERT_REQUIRED, trusting ONLY the demo CA -- not CERT_NONE,
    # not a hand-rolled "just check the public key bytes match" scheme.
    raise NotImplementedError(
        "TODO: build_client_context() -- see this file's module docstring"
    )
    # ==========================================================================


def main() -> None:
    print(
        f"ALICE (student task): connecting to {PEER_HOST}:{PEER_PORT} as if it "
        f"were '{SERVER_HOSTNAME}'",
        flush=True,
    )

    ctx = build_client_context()
    raw_sock = connect_with_retry()

    try:
        try:
            tls_sock = ctx.wrap_socket(raw_sock, server_hostname=SERVER_HOSTNAME)
        except ssl.SSLCertVerificationError as exc:
            print("CERT VERIFICATION FAILED - ABORTING", flush=True)
            print(f"ALICE: (reason: {exc.verify_message})", flush=True)
            sys.exit(1)

        with tls_sock:
            print("ALICE: TLS handshake succeeded -- sending secret", flush=True)
            tls_sock.sendall(SECRET_MESSAGE.encode())
            print(f"ALICE: sent encrypted message ({SECRET_MESSAGE!r})", flush=True)
    finally:
        try:
            raw_sock.close()
        except OSError:
            pass


if __name__ == "__main__":
    main()
