"""Week 11 helper: ask the two demo banks for a signature, make its "twin", and try to withdraw.

Usage (inside the container, from labs/week11-signatures-zkp):
    python bank.py vuln sign            # get a signature (r, s) from the vulnerable bank and show its twin
    python bank.py vuln pay original    # withdraw with the signature (r, s)
    python bank.py vuln pay twin        # withdraw with the twin (r, n-s)
    python bank.py fixed sign           # the same three commands for the fixed bank
    python bank.py fixed pay original
    python bank.py fixed pay twin

"vuln" = the bank on port 8102 (dedups by a hash of the signature), "fixed" = the bank on port 8103 (also
rejects the twin). `sign` saves the signature in /tmp so that `pay` can use it. A restart gives the bank a new
key, so run `sign` again after a restart. Local demo only. Standard library only, no packages needed.
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141   # the secp256k1 curve order
HALF = N // 2
BANKS = {"vuln": ("VULN_URL", "http://localhost:8102", 8102), "fixed": ("FIXED_URL", "http://fixed:8103", 8103)}


def base(bank):
    env, default, _ = BANKS[bank]
    return os.environ.get(env, default)


def call(url, body=None):
    req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except (urllib.error.URLError, OSError):
        sys.exit(f"Cannot reach the {url.split('/')[2]} bank. Is the lab running? (docker compose up -d)")


def txid(r, s):
    return hashlib.sha256((str(r) + str(s)).encode()).hexdigest()[:8]


def short(n):
    t = str(n)
    return f"{t[:10]}... ({len(t)} digits)"


def cache(bank):
    return f"/tmp/w11-{bank}.json"


def do_sign(bank):
    status, text = call(base(bank) + "/sign")
    j = json.loads(text)
    r, s = int(j["sig_r"]), int(j["sig_s"])
    twin = N - s
    json.dump({"message": j["message"], "r": r, "s": s}, open(cache(bank), "w"))
    print(f"bank: {bank} (port {BANKS[bank][2]})   message: {j['message']}")
    print(f"signature (r, s)   : s = {short(s)}   {'low-S' if s <= HALF else 'high-S'}")
    print(f"twin (r, n-s)      : n-s = {short(twin)}   {'low-S' if twin <= HALF else 'high-S'}")
    print(f"txid of (r, s) = {txid(r, s)}   txid of the twin = {txid(r, twin)}   (different)")


def do_pay(bank, which):
    try:
        c = json.load(open(cache(bank)))
    except FileNotFoundError:
        sys.exit(f"No signature saved yet. Run: python bank.py {bank} sign")
    s = c["s"] if which == "original" else N - c["s"]
    status, text = call(base(bank) + "/withdraw", {"message": c["message"], "sig_r": str(c["r"]), "sig_s": str(s)})
    print(f"bank: {bank} (port {BANKS[bank][2]})   paid with: {which}   ({'low-S' if s <= HALF else 'high-S'})")
    print(f"answer: HTTP {status} {text.strip()}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] in BANKS and a[1] == "sign":
        do_sign(a[0])
    elif len(a) == 3 and a[0] in BANKS and a[1] == "pay" and a[2] in ("original", "twin"):
        do_pay(a[0], a[2])
    else:
        sys.exit(__doc__)
