# {{ slot_label }} — Secure Transport (TLS): "encrypted" is not "encrypted to the right person"

**Kind:** Docker lab, guided step by step. No math; one short code edit (3 lines) with the correct lines shown first. Local containers only, no open ports.
**Concepts:** TLS handshake, X.509 certificates, the certificate-authority chain of trust, hostname verification, machine-in-the-middle ·
**Analogous CWE:** CWE-295 (Improper Certificate Validation), CWE-300 (Channel Accessible by Non-Endpoint)

## 100-minute class and assigned worksheet version

**In class:** 10 min retrieval quiz + 10 min brief + 60 min lab + 15 min debrief + 5 min evidence = 100 min.

**Common part — every student (60 points):** three guided tasks: A1 Alice does not check the certificate and Eve reads the secret, A2 Alice checks and Eve gets nothing, A3 the student fixes `build_client_context()` in `alice_student.py` (3 lines) and tests it against the impostor (rejected) and the real Bob (accepted).

**Assessment:** the common 60 points plus **one assigned version** (40 points): Conventional written questions Q1–Q4, or AIR-Sec Audit-the-AI 20 + EiPE 10 + Prompt Problem 10. Both versions total 100. The other version is ungraded practice.

**Evidence:** copy the commands and results from your own machine into the answer sheet, with your name and student ID. The secret `the vault code is 7731` is the same for everyone. **This week every student also commits the completed `alice_student.py` to branch `wk12` in their own GitHub fork and gives the commit link** (no separate marks; see [SUBMISSION.md](../../SUBMISSION.md), W12).

## ✅ This week — what to do
1. **Before class** — Docker Desktop working, the lab ZIP downloaded or the fork cloned, and the image built (worksheet "ก่อนเริ่ม", `docker compose -f docker-compose.vulnerable.yml build`).
2. **In class** — follow **Worksheet 12** step by step. Slides: `slides/week12.md`.
3. **Assigned version** — Conventional answers four questions; AIR-Sec audits an AI-written `verify=False` client, and writes the EiPE and the Prompt Problem.
4. **Submit** — one PDF `Wk12_<StudentID>.pdf` at `learn.zcr.ai/submit` plus the GitHub commit link.

## Objectives
- Show that a TLS connection can be fully encrypted and still reach the **wrong endpoint** when the client does not validate the certificate.
- Explain what a certificate claims, why anyone can make one, and what a trusted CA's signature adds.
- Fix a client with `ssl.create_default_context(cafile=...)`, which trusts only the demo CA and checks the chain and the hostname.
- Test a fix **both ways**: reject the impostor and accept the real server (a client that rejects everything also passes the first test).
- Name the limit: a dishonest or hacked CA can still sign a fake certificate (not covered by the lab).

## 🎭 The impostor's certificate
Three programs on one Docker network:

| Service | Role | Certificate |
|---|---|---|
| `alice.py` | the client; sends `the vault code is 7731` | decides whether to verify (`VERIFY=1` or not) |
| `bob.py` | the real server | **real**, signed by the demo CA (`CN=bob`) |
| `mitm.py` (Eve) | answers where Alice dials | **self-signed impostor** that also says `CN=bob` |

Alice is told to dial `mitm`, never `bob`: an attacker on the network path answers. `gen_certs.py` writes the demo CA, Bob's certificate and the impostor into a shared volume at start (no private key is ever committed).

| Compose file | Alice | Result |
|---|---|---|
| `docker-compose.vulnerable.yml` | no checking (`CERT_NONE`, `check_hostname=False`) | handshake succeeds, `MITM INTERCEPTED: the vault code is 7731` |
| `docker-compose.fixed.yml` | `VERIFY=1` (trust only the demo CA) | `CERT VERIFICATION FAILED - ABORTING`, reason `self-signed certificate`, Eve `intercepted NOTHING` |
| `docker-compose.student-task.yml` | the student's `alice_student.py` | the same rejection once `build_client_context()` is written; accepts Bob with `PEER_HOST=bob` |

## Run it (what the worksheet does)

```bash
cd labs/week12-secure-transport
docker compose -f docker-compose.vulnerable.yml build
docker compose -f docker-compose.vulnerable.yml run --rm alice
docker compose -f docker-compose.vulnerable.yml logs mitm
docker compose -f docker-compose.fixed.yml run --rm alice
docker compose -f docker-compose.fixed.yml logs mitm
# edit alice_student.py (3 lines), save, then:
docker compose -f docker-compose.student-task.yml run --rm --build alice
docker compose -f docker-compose.student-task.yml up -d bob
docker compose -f docker-compose.student-task.yml run --rm --no-deps -e PEER_HOST=bob alice
docker compose -f docker-compose.vulnerable.yml down -v
docker compose -f docker-compose.fixed.yml down -v
docker compose -f docker-compose.student-task.yml down -v
```

`run --rm alice` starts the certificate generator and Eve and prints only Alice's output; `logs mitm` shows what Eve saw. The `--build` is needed because the image copies `alice_student.py`. The older `up --build` and `logs` flow still works too.

## Verified

The vulnerable and fixed modes were Docker-tested against these files in a local checkout.
The shipped student stub was also tested: it fails loudly with `NotImplementedError`.
A scratch copy with the instructor's answer substituted into `alice_student.py` rejected the
impostor and accepted Bob using the positive-control commands above. Each stack was torn down
with `docker compose down -v` after testing. This is a Mac Docker test, not a Windows pilot.

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
- **Student task with a correct context:** rejected the impostor (Alice exit `1`); the same
  student file connected to Bob with `PEER_HOST=bob`, exited `0`, and Bob logged
  `BOB RECEIVED: the vault code is 7731`.
- No private key is committed to the repo; `ca.key`/`bob.key`/`impostor.key` exist only inside the
  ephemeral `certs` Docker volume, are regenerated every run, and are removed by `down -v`.
  (`.gitignore` also excludes `*.pem`/`*.key` as a second line of defense.)

**Re-verified 15 Nov 2026:** every command of the Run-it block above was executed in order (vulnerable, fixed, student stub failing with `NotImplementedError`, student fix rejecting the impostor and accepting Bob, and `run --rm --entrypoint grep alice` over `alice.py`). The vulnerable and fixed stacks run in the same session without a `down` between them.

## Deliverable
The common 60 points plus the assigned 40, as in the worksheet rubric, and the GitHub commit link of `alice_student.py`.

## References
- RFC 9846 (supersedes RFC 8446), *The Transport Layer Security (TLS) Protocol Version 1.3* — the handshake, key
  exchange + authentication separation, 0-RTT / early data.
- RFC 5280, *Internet X.509 Public Key Infrastructure Certificate and CRL Profile* — cert chains,
  `basicConstraints`, revocation.
- RFC 9525 (supersedes RFC 6125), *Service Identity in TLS* —
  hostname verification and SubjectAltName (why `SAN=DNS:bob` matters).
- OWASP, *Transport Layer Security Cheat Sheet* and *Testing for Weak Transport Layer Security* —
  the `verify=False` / disabled-validation anti-pattern.
- Python docs, `ssl` module — `create_default_context`, `check_hostname`, `CERT_NONE` vs.
  `CERT_REQUIRED` (the exact knobs `alice.py` toggles).
- Trevor Perrin (ed.), *The Noise Protocol Framework* (noiseprotocol.org) — background for Q6
  (TLS vs. Noise).
