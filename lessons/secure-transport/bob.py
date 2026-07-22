"""
Week 12 lab -- Bob, the LEGITIMATE TLS server.

Bob wraps a listening socket in a TLS server context that presents his
CA-SIGNED certificate (bob.crt, SAN=DNS:bob). A client that trusts the demo CA
and connects to Bob directly would get a clean, verified handshake.

Bob is present for completeness -- the legitimate path exists. In the attack
scenario, though, Alice is pointed at the MITM (see docker-compose.*.yml), NOT
at Bob, so in these runs Bob mostly sits idle. That is fine and expected: the
lesson is about who Alice ends up talking to, not about Bob misbehaving.

Bob never logs Alice's secret in the attack topology because Alice never
reaches him -- the MITM terminates her connection first.
"""
import os
import socket
import ssl
import time

LISTEN_HOST = os.environ.get("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "8443"))
CERT_DIR = os.environ.get("CERT_DIR", "/certs")


def wait_for(path: str, retries: int = 20, delay_s: float = 0.5) -> str:
    """Wait until a cert file is readable in the shared volume (compose gates
    us on gen_certs, but named-volume writes can lag the writer's exit)."""
    for _ in range(retries):
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path
        time.sleep(delay_s)
    raise FileNotFoundError(f"cert never appeared at {path}")


def build_server_context() -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(
        certfile=wait_for(os.path.join(CERT_DIR, "bob.crt")),
        keyfile=wait_for(os.path.join(CERT_DIR, "bob.key")),
    )
    return ctx


def main() -> None:
    ctx = build_server_context()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((LISTEN_HOST, LISTEN_PORT))
    server_sock.listen(5)
    print(
        f"BOB: TLS server listening on {LISTEN_HOST}:{LISTEN_PORT} "
        f"(presenting CA-signed cert, CN=bob)",
        flush=True,
    )

    while True:
        raw_conn, addr = server_sock.accept()
        try:
            with ctx.wrap_socket(raw_conn, server_side=True) as tls_conn:
                data = tls_conn.recv(4096)
                if data:
                    print(f"BOB RECEIVED: {data.decode(errors='replace')}", flush=True)
        except ssl.SSLError as exc:
            print(f"BOB: TLS handshake failed: {exc}", flush=True)
        except Exception as exc:  # noqa: BLE001 -- lab code, log and keep serving
            print(f"BOB: error handling connection: {exc}", flush=True)
        finally:
            try:
                raw_conn.close()
            except OSError:
                pass


if __name__ == "__main__":
    main()
