#!/usr/bin/env python3
"""Week 15 helper: small commands for the guided steps (no curl, no host Python needed).

Run it INSIDE the lab container, from the lab folder:
  docker compose exec vulnerable python lamport.py sign 00000000   # get a signature on a message, check bit 0
  docker compose exec vulnerable python lamport.py both 0          # show both secret halves of key position 0
  docker compose exec vulnerable python lamport.py forge           # build the admin signature and submit it

It talks to the vulnerable server on localhost:8100 (override with VULN_HOST / VULN_PORT).
Only the Python standard library is used. The signatures are saved as sig_<message>.json in the
lab folder, and the forged request body as forged_admin.json (the same file exploit.py writes).
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

HOST = os.environ.get("VULN_HOST", "localhost")
PORT = int(os.environ.get("VULN_PORT", "8100"))
BASE = f"http://{HOST}:{PORT}"
HERE = Path(__file__).resolve().parent
ZEROS, ONES = "00000000", "ffffffff"


def H(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def bits(value: int, n: int = 32):
    return [(value >> (n - 1 - i)) & 1 for i in range(n)]          # most significant bit first


def call(method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")
    except urllib.error.URLError as e:
        sys.exit(f"cannot reach {BASE}: {e.reason}. Is the lab running? (docker compose up -d)")


def short(b: bytes) -> str:
    return b.hex()[:12] + "..."


def cmd_sign(msg_hex):
    msg_hex = msg_hex.lower().removeprefix("0x").zfill(8)
    status, body = call("POST", "/sign", {"message_hex": msg_hex})
    if status != 200:
        sys.exit(f"the server answered HTTP {status}: {body}")
    pk = call("GET", "/pubkey")[1]["pk"]
    sig = body["sig"]
    (HERE / f"sig_{msg_hex}.json").write_text(json.dumps(sig))
    b0 = bits(int(msg_hex, 16))[0]
    h0 = H(bytes.fromhex(sig[0]))
    print(f"signed 0x{msg_hex} on the vulnerable server (:{PORT}): {len(sig)} preimages revealed")
    print(f"message bit 0 = {b0}")
    print(f"SHA256(sig[0])        = {short(h0)}")
    print(f"matches pk[0][0] (value 0): {h0.hex() == pk[0][0]}")
    print(f"matches pk[0][1] (value 1): {h0.hex() == pk[0][1]}")
    print(f"saved sig_{msg_hex}.json")


def load(msg_hex):
    p = HERE / f"sig_{msg_hex}.json"
    if not p.exists():
        sys.exit(f"{p.name} not found: run  python lamport.py sign {msg_hex}  first")
    return json.loads(p.read_text())


def recover(sig_a, hex_a, sig_b, pk):
    """Both preimages per bit from the two signatures (message hex_a and its complement)."""
    n = len(pk)
    ba = bits(int(hex_a, 16), n)
    sk = [[None, None] for _ in range(n)]
    for i in range(n):
        sk[i][ba[i]] = bytes.fromhex(sig_a[i])
        sk[i][1 - ba[i]] = bytes.fromhex(sig_b[i])
    ok = all(H(sk[i][b]).hex() == pk[i][b] for i in range(n) for b in (0, 1))
    return sk, ok


def cmd_both(pos):
    pos = int(pos)
    pk = call("GET", "/pubkey")[1]["pk"]
    sig0, sig1 = load(ZEROS), load(ONES)
    if not 0 <= pos < len(pk):
        sys.exit(f"bit position must be 0 to {len(pk) - 1}")
    p0, p1 = bytes.fromhex(sig0[pos]), bytes.fromhex(sig1[pos])
    print(f"key position {pos}")
    print(f"from sig_{ZEROS}.json (message bit = 0): preimage {short(p0)}  SHA256 matches pk[{pos}][0]: {H(p0).hex() == pk[pos][0]}")
    print(f"from sig_{ONES}.json (message bit = 1): preimage {short(p1)}  SHA256 matches pk[{pos}][1]: {H(p1).hex() == pk[pos][1]}")
    print(f"both secret halves of key position {pos} are now known")


def cmd_forge():
    pub = call("GET", "/pubkey")[1]
    pk, admin = pub["pk"], int(pub["admin_message_hex"], 16)
    sk, ok = recover(load(ZEROS), ZEROS, load(ONES), pk)
    print(f"recovered both preimages for all {len(pk)} positions; every one hashes to the public key: {ok}")
    if not ok:
        sys.exit("the recovered key does not match the public key")
    ab = bits(admin, len(pk))
    forged = [sk[i][ab[i]].hex() for i in range(len(pk))]
    (HERE / "forged_admin.json").write_text(json.dumps({"sig": forged}, indent=2) + "\n")
    print(f"admin message = 0x{admin:08x}")
    print(f"wrote forged_admin.json ({len(forged)} preimages)")
    status, body = call("POST", "/admin", {"sig": forged})
    print(f"POST /admin -> HTTP {status} {json.dumps(body)}")


USAGE = __doc__.split("Run it INSIDE")[1].split("It talks")[0]
if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "sign":
        cmd_sign(a[1])
    elif len(a) == 2 and a[0] == "both":
        cmd_both(a[1])
    elif len(a) == 1 and a[0] == "forge":
        cmd_forge()
    else:
        sys.exit("usage:" + USAGE.rstrip())
