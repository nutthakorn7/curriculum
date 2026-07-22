# {{ slot_label }} — Secure Transport (TLS): Certificate-Validation-Bypass MITM

**Topic (KOSEN68 source):** `Week11 Questions.docx` · **Kind:** HYBRID
**Concepts:** TLS handshake, X.509 certificates, certificate-authority chain of trust, hostname
verification, machine-in-the-middle · **Analogous CWE:** CWE-295 (Improper Certificate
Validation), CWE-300 (Channel Accessible by Non-Endpoint)

## This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security` and
   this course's earlier weeks); skim the {{ ref('key-exchanges') }} (Key Exchanges) MITM recap — this week is its
   TLS-layer sequel.
2. **Lecture (120 min)** — weekly quiz first (~10 min), then the lecture: SSL→TLS 1.3 evolution,
   what the handshake actually authenticates, and why "the traffic is encrypted" is not the same
   claim as "encrypted *to the right person*". Slides: `{{ slides }}` *(not yet written — see
   `course-plan-19weeks.md`)*.
3. **Lab (180 min)** — run the demo in both modes below, then complete **Worksheet 12**
   (`worksheet.md`, Part 1 — Conventional essays; Part 2 — AIR-Sec arm: lab evidence,
   Audit-the-AI, EiPE, Prompt Problem, viva prep).
4. **Submit** — worksheet PDF + captured log evidence → Classroom · code unchanged (this is a
   read/run/observe lab, not an exploit-and-fix-the-code lab) → GitHub. (How: [SUBMISSION.md](../../SUBMISSION.md).)

## Objectives
- Explain what a TLS handshake authenticates and what it does *not*: encryption protects the
  channel, but only **certificate validation** ties that channel to a specific identity.
- Explain the Web PKI chain of trust: why a server cert is trusted because a **Certificate
  Authority signed it**, and why a self-signed cert claiming the same name proves nothing.
- **Execute and observe** a full machine-in-the-middle against a TLS client that skips certificate
  validation: the attacker presents a self-signed cert claiming to be the server, the client
  completes a "successful" (encrypted!) handshake with the *attacker*, and hands over its secret.
- Explain why loading the CA as a trust anchor and keeping `check_hostname=True` defeats that
  MITM — the impostor cert has no chain to the CA, so verification fails **before** any secret is
  sent, with a *trust/issuer* error, not a name mismatch.
- Recognize the single most common real-world form of this bug: `verify=False` /
  `CERT_NONE` / `InsecureSkipVerify` copy-pasted from a "just make it work" answer (the planted
  flaw you audit in Part 2b).

## 🎭 Signature game — "The Impostor's Certificate"
Stand in for the server with nothing but a self-signed certificate you generated yourself, and
watch a careless client hand you its secret anyway, "encrypted" the whole time. Then flip on
real certificate validation and watch the exact same impostor cert get rejected before a single
byte of the secret is sent.

**Why it's exciting:** your forgery sails through TLS's lock icon and green padlock — until one
line of validation code slams the door in your face.

## How this maps to the TLS certificate-validation concept

Four services on one Docker network. `gen_certs` runs first (an init step), then the three roles:

| Service | Role | What it does |
|---|---|---|
| `gen_certs.py` | Init | Using Python `cryptography`, generates a demo **CA**, **Bob's** server cert (`CN=bob`, `SAN=DNS:bob`, **signed by the CA**), and a **self-signed impostor** cert (also `CN=bob`, `SAN=DNS:bob`, but **no CA signature**). Writes them to a shared volume and exits. Keys are generated at startup — none are committed to the repo. |
| `bob.py` | Legit server | TLS server presenting its CA-signed cert. The legitimate endpoint. In the attack topology Alice is pointed at the MITM, so Bob mostly sits idle — that is expected. |
| `mitm.py` | Attacker | TLS server on the exposed path, presenting the **self-signed impostor** cert (claiming `CN=bob`). On a successful handshake it reads Alice's secret and logs `MITM INTERCEPTED: <secret>`. Its code is identical in both modes. |
| `alice.py` | Client | TLS client that dials the **MITM** (believing it is Bob) and sends the secret. Controlled by env var `VERIFY`: unset = **vulnerable** (`CERT_NONE`, `check_hostname=False`); `VERIFY=1` = **fixed** (loads the CA, keeps hostname checking). |

The premise: **Alice's `PEER_HOST` is `mitm`, not `bob`.** That is the whole lesson — over a
network an attacker controls, "whoever answers when I dial Bob's address" is not the same claim as
"Bob." TLS *encryption* still works perfectly against the MITM in vulnerable mode — the handshake
completes, a session key is negotiated, the bytes on the wire are ciphertext. But encryption to
the wrong endpoint is worthless: the MITM *is* the other endpoint, so it holds the session key and
reads the plaintext directly. The one thing that would have caught it — **checking that the
server's certificate chains to a trusted CA** — is exactly what the vulnerable client turned off.

The fix (`VERIFY=1`) does **not** change the MITM's code at all. The MITM still presents the same
impostor cert. What changes is that Alice now loads the demo CA (`ca.crt`) as her only trust
anchor and keeps `check_hostname=True`. The impostor cert is self-signed — there is no chain from
it to the demo CA — so Alice's TLS stack raises `ssl.SSLCertVerificationError` **during the
handshake, before she sends anything**. She prints `CERT VERIFICATION FAILED - ABORTING` and
exits nonzero; the MITM receives no data to intercept.

**What this lab does *not* show:** the rest of the Web PKI failure surface — a genuinely
*compromised or misbehaving* CA (which *would* produce a validly-chained cert and defeat this
exact check), certificate pinning, revocation (CRL/OCSP/stapling), or Certificate Transparency.
Those stay conceptual this week (Part 1 Q5, and Part 2c EiPE). The running demo is specifically
the *client-skips-validation* bug — the single most common real-world TLS mistake — not a CA
compromise.

## Run it

Vulnerable mode — client skips cert validation, MITM intercepts:
```bash
cd {{ labpath }}
docker compose -f docker-compose.vulnerable.yml up --build
```
Expected log lines (interleaving/ports/IPs vary run to run — the container names and message text
do not):
```
week12-gencerts  | GEN_CERTS: wrote ca.crt, bob.crt (CN=bob, signed by CA), impostor.crt (CN=bob, self-signed) to /certs
week12-mitm      | MITM: TLS server listening on 0.0.0.0:8443 (presenting SELF-SIGNED impostor cert, CN=bob)
week12-alice     | ALICE: connecting to mitm:8443 as if it were 'bob' -- VULNERABLE (no cert check)
week12-alice     | ALICE: TLS handshake succeeded WITHOUT verifying the server cert -- sending secret to whoever answered
week12-alice     | ALICE: sent encrypted message ('the vault code is 7731')
week12-mitm      | MITM INTERCEPTED: the vault code is 7731
week12-bob       | BOB: TLS server listening on 0.0.0.0:8443 (presenting CA-signed cert, CN=bob)
```
`alice` exits `0` once her message is sent; `bob` and `mitm` are long-running servers — stop the
stack with `Ctrl-C` then tear it down:
```bash
docker compose -f docker-compose.vulnerable.yml down -v
```
The `MITM INTERCEPTED: the vault code is 7731` line is your **personalized/attributable evidence
artifact** for this HYBRID week (in place of a CTF flag) — captured together with your identity
proof, per the worksheet's Evidence & Integrity section.

Fixed mode — client validates the cert against the demo CA:
```bash
docker compose -f docker-compose.fixed.yml up --build
```
Expected log lines:
```
week12-gencerts  | GEN_CERTS: wrote ca.crt, bob.crt (CN=bob, signed by CA), impostor.crt (CN=bob, self-signed) to /certs
week12-mitm      | MITM: TLS server listening on 0.0.0.0:8443 (presenting SELF-SIGNED impostor cert, CN=bob)
week12-alice     | ALICE: connecting to mitm:8443 as if it were 'bob' -- FIXED (VERIFY=1)
week12-alice     | CERT VERIFICATION FAILED - ABORTING
week12-alice     | ALICE: (reason: self-signed certificate)
week12-mitm      | MITM: handshake aborted by client, intercepted NOTHING (SSLError)
```
`alice` exits `1`. There is **no** `MITM INTERCEPTED` line anywhere in this mode's logs — that
absence is your evidence the fix worked. Note the abort *reason*: `self-signed certificate` — a
**trust/issuer** failure, not a hostname mismatch. The impostor claims `CN=bob` with `SAN=DNS:bob`
just like the real Bob; the *only* thing that distinguishes it is the missing CA signature, and
that is exactly what the check catches. Tear down the same way:
```bash
docker compose -f docker-compose.fixed.yml down -v
```

No environment variables need to be set by hand — which compose file you point `-f` at is the
*only* thing that selects vulnerable vs. fixed mode (`VERIFY` is baked into each file's
`environment:` block; the two files are functionally identical but for Alice's `VERIFY` flag —
diff them and the only behavioral difference is that one line). Use `down -v` to also drop the
shared `certs` volume so the next run regenerates fresh certs.

Write-it-yourself mode — after completing `alice_student.py` (worksheet Part 2a, step 5):
```bash
docker compose -f docker-compose.student-task.yml up --build
```
Same expected output as fixed mode above. This is the one lab in the course where you write the
fix instead of just confirming a pre-built one — see the worksheet and `alice_student.py`'s
docstring for exactly what's required.

## Verified

Both modes were Docker-tested against the actual files in this directory, run fresh from a
scratchpad copy (OneDrive placeholder files can break `docker build` COPY, so the lab was copied
to a local scratch dir first) with `docker compose -f <file> up --build --abort-on-container-exit
--exit-code-from alice`, then torn down (`docker compose down -v`) and the built images removed.

- **Cert chain (pre-flight, `openssl`):** `openssl verify -CAfile ca.crt bob.crt` → `OK`;
  `openssl verify -CAfile ca.crt impostor.crt` → `verification failed` / `self-signed
  certificate`. Both `bob.crt` and `impostor.crt` carry `subject=CN=bob` and
  `X509v3 Subject Alternative Name: DNS:bob`; only their issuer differs (`Week12 Demo CA` vs.
  self). This is what makes the fixed-mode failure a *trust* failure, not a name mismatch.
- **Vulnerable:** printed `MITM INTERCEPTED: the vault code is 7731` (`grep -c "MITM INTERCEPTED"`
  = `1`), Alice logged the handshake succeeded *without* verifying the cert and exited `0`; no
  `CERT VERIFICATION FAILED` line present.
- **Fixed:** printed `CERT VERIFICATION FAILED - ABORTING` and `ALICE: (reason: self-signed
  certificate)` from `alice` (exit `1`), the MITM logged `intercepted NOTHING`, and
  `docker compose -f docker-compose.fixed.yml logs | grep -c "MITM INTERCEPTED"` returned `0`.
- No private key is committed to the repo; `ca.key`/`bob.key`/`impostor.key` exist only inside the
  ephemeral `certs` Docker volume, are regenerated every run, and are removed by `down -v`.
  (`.gitignore` also excludes `*.pem`/`*.key` as a second line of defense.)

## Deliverable
Worksheet 12 (`worksheet.md`, Parts 1–2), including the captured log evidence from both modes
(Part 2a), the Audit-the-AI finding on the planted `verify=False` snippet (Part 2b), the EiPE
explanation of why a CA signature matters (Part 2c), the Prompt Problem critique (Part 2d), and
viva prep (Part 2e).

## References
- RFC 8446, *The Transport Layer Security (TLS) Protocol Version 1.3* — the handshake, key
  exchange + authentication separation, 0-RTT / early data.
- RFC 5280, *Internet X.509 Public Key Infrastructure Certificate and CRL Profile* — cert chains,
  `basicConstraints`, revocation.
- RFC 6125, *Representation and Verification of Domain-Based Application Service Identity* —
  hostname verification and SubjectAltName (why `SAN=DNS:bob` matters).
- OWASP, *Transport Layer Security Cheat Sheet* and *Testing for Weak Transport Layer Security* —
  the `verify=False` / disabled-validation anti-pattern.
- Python docs, `ssl` module — `create_default_context`, `check_hostname`, `CERT_NONE` vs.
  `CERT_REQUIRED` (the exact knobs `alice.py` toggles).
- Trevor Perrin (ed.), *The Noise Protocol Framework* (noiseprotocol.org) — background for Q6
  (TLS vs. Noise).
