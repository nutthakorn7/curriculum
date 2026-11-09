#!/usr/bin/env python3
"""Week 6 helper: ask a server "is this ciphertext OK?" with ONE letter changed, and print its answer.

Usage (inside the container, from labs/week06-aead):
    python ask.py vuln original     # the untouched ciphertext
    python ask.py vuln start        # change one letter near the START of the ciphertext
    python ask.py vuln end          # change one letter near the END of the ciphertext
    python ask.py fixed original    # the same three questions for the AES-GCM server
    python ask.py fixed start
    python ask.py fixed end

"vuln" = the AES-CBC server on port 8098, "fixed" = the AES-GCM server on port 8099.
It only reads /secret and calls /decrypt (the same two endpoints exploit.py uses). It never sees any key.
Standard library only, so no packages are needed."""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

PORTS = {"vuln": 8098, "fixed": 8099}
# Inside the lab container the other server is reachable by its service name; on the host it is localhost.
HOSTS = {"vuln": [os.environ.get("VULN_HOST", "localhost")],
         "fixed": [os.environ.get("FIXED_HOST", ""), "localhost", "fixed"]}


def call(host, port, path, data=None):
    req = urllib.request.Request(f"http://{host}:{port}{path}", data=data,
                                 headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read().decode().strip()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode().strip()


def find_host(which):
    for h in HOSTS[which]:
        if not h:
            continue
        try:
            call(h, PORTS[which], "/")
            return h
        except Exception:
            continue
    sys.exit(f"Cannot reach the {which} server. Did you run 'docker compose up -d' and wait for the logs?")


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in PORTS or sys.argv[2] not in ("original", "start", "end"):
        sys.exit(__doc__)
    which, where = sys.argv[1], sys.argv[2]
    host, port = find_host(which), PORTS[which]
    status, body = call(host, port, "/secret")
    token = json.loads(body)["ciphertext"]

    note = "the ciphertext exactly as the server gave it"
    if where != "original":
        # position 0 is the very first letter; the end position is 6 letters before the end of the text
        i = 0 if where == "start" else len(token) - 6
        new = "A" if token[i] != "A" else "B"
        token = token[:i] + new + token[i + 1:]
        note = f"letter number {i + 1} of {len(token)} changed from {json.loads(body)['ciphertext'][i]} to {new}"
    base64.b64decode(token)  # sanity check: still valid base64
    status, body = call(host, port, "/decrypt", json.dumps({"ciphertext": token}).encode())
    print(f"server: {which} (port {port})   asked about: {where}   ({note})")
    print(f"answer: HTTP {status} {body}")


if __name__ == "__main__":
    main()
