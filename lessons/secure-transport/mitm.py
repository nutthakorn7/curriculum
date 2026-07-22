"""
Week 12 lab -- the MITM (machine-in-the-middle) TLS server.

Alice is configured to dial the MITM's address believing it is Bob (see
docker-compose.*.yml: Alice's PEER_HOST is `mitm`, never `bob`). The MITM
listens on the exposed port and wraps each connection in a TLS SERVER context
that presents the IMPOSTOR certificate -- impostor.crt, which claims CN=bob /
SAN=DNS:bob but is SELF-SIGNED (no CA vouches for it).

Two outcomes, decided entirely by Alice, not by anything the MITM does:

  * If Alice does NOT validate the server certificate (CERT_NONE,
    check_hostname=False -- the vulnerable client), her TLS handshake with the
    impostor cert SUCCEEDS. She then sends her secret, believing she has a
    secure channel to Bob. The MITM receives it in plaintext and logs
    "MITM INTERCEPTED: <secret>". Encryption did its job perfectly -- to the
    wrong endpoint.

  * If Alice DOES validate against the demo CA (the fixed client), her TLS
    stack rejects the impostor cert during the handshake ("unable to get local
    issuer" / self-signed), sends a TLS alert, and closes without ever sending
    the secret. The MITM's do_handshake() or recv() then raises, it receives
    NOTHING, and it must never print "MITM INTERCEPTED" in this case.

The MITM's code is IDENTICAL across both compose files -- it always presents
the impostor cert and always tries to read the secret. What changes is purely
Alice's trust configuration. That is the lesson: the defense lives in the
client's certificate validation, not in the server.

(An onward relay to the real Bob is intentionally omitted -- it adds a second
TLS client and failure surface but nothing to the evidence line. Bob sitting
idle in the attack topology is expected.)
"""
import os
import socket
import ssl
import time

LISTEN_HOST = os.environ.get("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "8443"))
CERT_DIR = os.environ.get("CERT_DIR", "/certs")


def wait_for(path: str, retries: int = 20, delay_s: float = 0.5) -> str:
    """Wait until a cert file is readable in the shared volume. compose gates
    us on gen_certs completing, but named-volume writes can lag the writer's
    exit slightly, so we retry rather than assume instant visibility."""
    for _ in range(retries):
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path
        time.sleep(delay_s)
    raise FileNotFoundError(f"cert never appeared at {path}")


def build_impostor_context() -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # Present the SELF-SIGNED impostor cert (CN=bob, but no CA signature).
    ctx.load_cert_chain(
        certfile=wait_for(os.path.join(CERT_DIR, "impostor.crt")),
        keyfile=wait_for(os.path.join(CERT_DIR, "impostor.key")),
    )
    return ctx


def main() -> None:
    ctx = build_impostor_context()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((LISTEN_HOST, LISTEN_PORT))
    server_sock.listen(5)
    print(
        f"MITM: TLS server listening on {LISTEN_HOST}:{LISTEN_PORT} "
        f"(presenting SELF-SIGNED impostor cert, CN=bob)",
        flush=True,
    )

    while True:
        raw_conn, addr = server_sock.accept()
        print(f"MITM: connection from {addr}", flush=True)
        try:
            # If Alice validates certs, the handshake here raises ssl.SSLError
            # (she rejects the impostor cert and sends an alert). We must
            # survive that cleanly and NOT log any secret.
            with ctx.wrap_socket(raw_conn, server_side=True) as tls_conn:
                data = tls_conn.recv(4096)
                if data:
                    # Reached only when Alice accepted the impostor cert.
                    print(f"MITM INTERCEPTED: {data.decode(errors='replace')}", flush=True)
                else:
                    print("MITM: peer sent no data (nothing to intercept)", flush=True)
        except ssl.SSLError as exc:
            # Expected in fixed mode: Alice rejected the impostor cert.
            print(
                f"MITM: handshake aborted by client, intercepted NOTHING ({exc.__class__.__name__})",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001 -- lab code, log and keep serving
            print(f"MITM: error handling connection: {exc}", flush=True)
        finally:
            try:
                raw_conn.close()
            except OSError:
                pass


if __name__ == "__main__":
    main()
