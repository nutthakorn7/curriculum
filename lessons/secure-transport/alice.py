"""
Week 12 lab -- Alice, the TLS client (the decision point).

Alice opens a TCP connection to PEER_HOST:PEER_PORT. In the attack topology
that host is `mitm`, not `bob` -- but Alice believes she is reaching Bob, so
she wraps the socket in TLS with server_hostname="bob" in BOTH modes. Whether
she is protected depends on ONE environment variable:

  VERIFY unset / empty  ->  VULNERABLE client.
      ctx.check_hostname = False   (set FIRST -- required before CERT_NONE, or
                                    Python raises ValueError)
      ctx.verify_mode   = ssl.CERT_NONE
      -> Alice accepts ANY certificate, including the MITM's self-signed
         impostor. The handshake succeeds, she sends her secret, and the MITM
         reads it in the clear. Encryption worked -- to the wrong endpoint.

  VERIFY=1              ->  FIXED client.
      ctx = ssl.create_default_context()           (check_hostname=True,
                                                     CERT_REQUIRED by default)
      ctx.load_verify_locations(ca.crt)            (trust ONLY the demo CA)
      -> The impostor cert is self-signed, so the chain to the demo CA does not
         exist. Alice's TLS stack raises ssl.SSLCertVerificationError during the
         handshake. She catches it, prints "CERT VERIFICATION FAILED -
         ABORTING", exits nonzero, and sends NOTHING.

The secret is fixed for the whole class; it is the leak *event* (captured in
the MITM's log with your identity proof) that is your attributable evidence.
"""
import os
import socket
import ssl
import sys
import time

PEER_HOST = os.environ.get("PEER_HOST", "mitm")
PEER_PORT = int(os.environ.get("PEER_PORT", "8443"))
# Alice always THINKS she is talking to Bob, so she asks TLS to check for "bob"
# regardless of the TCP host she dialed. In fixed mode this makes the failure a
# clean trust/issuer error, not a name mismatch.
SERVER_HOSTNAME = os.environ.get("SERVER_HOSTNAME", "bob")
CERT_DIR = os.environ.get("CERT_DIR", "/certs")
VERIFY = os.environ.get("VERIFY", "").strip() == "1"
SECRET_MESSAGE = os.environ.get("SECRET_MESSAGE", "the vault code is 7731")

CONNECT_RETRIES = 20
CONNECT_RETRY_DELAY_S = 0.5


def wait_for_ca_cert() -> str:
    """Wait until the demo CA cert is readable in the shared volume.

    The compose files already gate Alice on `gen_certs` completing, but named
    volume writes can take a moment to become visible after the writer exits,
    so we retry rather than assume the file is instantly there. Only needed in
    fixed mode (the vulnerable client loads no CA)."""
    ca_path = os.path.join(CERT_DIR, "ca.crt")
    for _ in range(CONNECT_RETRIES):
        if os.path.exists(ca_path) and os.path.getsize(ca_path) > 0:
            return ca_path
        time.sleep(CONNECT_RETRY_DELAY_S)
    raise FileNotFoundError(f"CA cert never appeared at {ca_path}")


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


def build_client_context() -> ssl.SSLContext:
    if VERIFY:
        # FIXED: trust only the demo CA, verify the chain and the hostname.
        ca_path = wait_for_ca_cert()
        ctx = ssl.create_default_context(cafile=ca_path)
        # create_default_context already sets check_hostname=True and
        # verify_mode=CERT_REQUIRED; we keep both.
        return ctx

    # VULNERABLE: disable all certificate checking. Order matters --
    # check_hostname must be turned off BEFORE setting CERT_NONE, or Python
    # raises "Cannot set verify_mode to CERT_NONE when check_hostname is
    # enabled".
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def main() -> None:
    mode = "FIXED (VERIFY=1)" if VERIFY else "VULNERABLE (no cert check)"
    print(
        f"ALICE: connecting to {PEER_HOST}:{PEER_PORT} as if it were "
        f"'{SERVER_HOSTNAME}' -- {mode}",
        flush=True,
    )

    ctx = build_client_context()
    raw_sock = connect_with_retry()

    try:
        try:
            tls_sock = ctx.wrap_socket(raw_sock, server_hostname=SERVER_HOSTNAME)
        except ssl.SSLCertVerificationError as exc:
            # FIXED path against the impostor: the chain to the demo CA does not
            # exist (self-signed), so verification fails before any data is sent.
            print("CERT VERIFICATION FAILED - ABORTING", flush=True)
            print(f"ALICE: (reason: {exc.verify_message})", flush=True)
            sys.exit(1)

        with tls_sock:
            # Under CERT_NONE the parsed dict from getpeercert() is empty (the
            # stack never validated the cert), so note that the handshake was
            # accepted WITHOUT any identity check -- which is the whole bug.
            print(
                "ALICE: TLS handshake succeeded WITHOUT verifying the server "
                "cert -- sending secret to whoever answered",
                flush=True,
            )
            tls_sock.sendall(SECRET_MESSAGE.encode())
            print(f"ALICE: sent encrypted message ({SECRET_MESSAGE!r})", flush=True)
    finally:
        try:
            raw_sock.close()
        except OSError:
            pass


if __name__ == "__main__":
    main()
