"""
Week 13 lab -- the messaging server (the "provider").

This is the whole point of the lab, so read it carefully: this file is
COMPLETELY MODE-AGNOSTIC. It does not know or care whether E2EE is on. It
runs byte-for-byte the same in both docker-compose files. Its only job is:

  POST /pubkey  -- bob publishes his public key here (fixed mode only; alice
                   fetches it from here). Body: {"pubkey": "<base64 PEM>"}.
  POST /send    -- alice posts a message for bob. Body: {"payload": "<string>"}.
                   The server STORES the payload and LOGS it verbatim:
                       SERVER SAW: <payload>
                   That log line is the evidence artifact for this week.
  GET  /pubkey  -- returns the stored pubkey, or 404 until bob has published.
  GET  /fetch   -- returns the stored message, or 404 until alice has sent.

Because the server just logs whatever bytes alice hands it, the difference
between "the provider can read your messages" and "the provider cannot" is
decided ENTIRELY by what alice chose to send:

  - vulnerable mode: alice sends raw plaintext  -> "SERVER SAW: meet at pier 39 at midnight"
  - fixed (E2EE) mode: alice sends ciphertext    -> "SERVER SAW: <base64 gibberish>"

Same server, same log statement -- yet in E2EE mode the server structurally
cannot see the plaintext. That is end-to-end encryption: the guarantee comes
from the *clients*, not from trusting the server.

Runs single-process (app.run, not a multi-worker WSGI server) so the
module-level in-memory store is shared across /pubkey and /fetch requests.
"""
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory store. Single process => shared across requests. Nothing is
# persisted; a fresh `up` starts empty.
STORE = {
    "pubkey": None,     # base64(PEM) published by bob (fixed mode)
    "message": None,    # the payload alice sent (plaintext OR ciphertext)
}

E2E = os.environ.get("E2E", "").strip() == "1"


@app.get("/")
def index():
    # Liveness probe target for the clients' connection-retry loop.
    return jsonify(ok=True, e2e=E2E)


@app.post("/pubkey")
def publish_pubkey():
    body = request.get_json(force=True)
    STORE["pubkey"] = body["pubkey"]
    print("SERVER: bob published a public key", flush=True)
    return jsonify(ok=True)


@app.get("/pubkey")
def get_pubkey():
    if STORE["pubkey"] is None:
        return jsonify(error="no pubkey published yet"), 404
    return jsonify(pubkey=STORE["pubkey"])


@app.post("/send")
def send():
    body = request.get_json(force=True)
    payload = body["payload"]
    STORE["message"] = payload

    # THE line. The server logs exactly what it stored -- and what it stored
    # is exactly what alice chose to hand it. In vulnerable mode that is the
    # plaintext secret; in E2EE mode it is opaque base64 ciphertext. The
    # server code is identical either way.
    print(f"SERVER SAW: {payload}", flush=True)
    return jsonify(ok=True)


@app.get("/fetch")
def fetch():
    if STORE["message"] is None:
        return jsonify(error="no message yet"), 404
    return jsonify(payload=STORE["message"])


def main() -> None:
    host = os.environ.get("LISTEN_HOST", "0.0.0.0")
    port = int(os.environ.get("LISTEN_PORT", "8080"))
    print(f"SERVER: listening on {host}:{port} (E2E={E2E})", flush=True)
    # threaded=True so a client polling GET /fetch does not block another
    # client's POST; single process, so STORE stays shared.
    app.run(host=host, port=port, threaded=True)


if __name__ == "__main__":
    main()
