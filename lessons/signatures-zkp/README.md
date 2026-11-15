# {{ slot_label }} — Digital Signatures (the "twin" signature that pays the bank twice)

**Kind:** Docker lab, guided step by step. No math and no programming for the common 60 points. Two local containers, ports `8102` and `8103`, local demo only.
**Concepts:** digital signatures vs. MACs, ECDSA signature malleability (the twin `(r, n−s)`), low-S, signed transaction identity, the Schnorr proof of knowledge ·
**Analogous CWE:** CWE-347 (Improper Verification of Cryptographic Signature), CWE-345 (Insufficient Verification of Data Authenticity)

## 100-minute class and assigned worksheet version

**In class:** 10 min retrieval quiz + 10 min brief + 70 min lab + 10 min evidence = 100 min.

**Common part — every student (60 points):** three guided tasks with `bank.py`: A1 get a signature and see its twin, A2 pay with the original, replay it (`409`), pay with the twin (the bank pays twice and shows the flag), A3 the fixed bank rejects the twin (`403`), then find the `is_low_s` line and explain what low-S does and does not fix.

**Assessment:** the common 60 points plus **one assigned version** (40 points): Conventional written questions Q1–Q4, or AIR-Sec Audit-the-AI 20 + EiPE 10 + Prompt Problem 10. Both versions total 100. The other version is ungraded practice.

**Evidence:** copy the commands and results from your own machine into the answer sheet, with your name and student ID. Signatures are random per run; the status codes (`200`, `409`, `403`), the totals (`100`, `200`) and the flag are the same for everyone. There is no personal flag this week.

## ✅ This week — what to do
1. **Before class** — Docker Desktop working and the lab ZIP downloaded (worksheet "ก่อนเริ่ม"). Skim last week's recap (Week 10, hybrid encryption).
2. **In class** — follow **Worksheet 11** step by step. Do the whole lab **without restarting** (a restart gives each bank a new key and a zero balance). Slides: `slides/week11.md`.
3. **Assigned version** — Conventional answers the four questions in the worksheet; AIR-Sec audits the AI's dedup code, and writes the EiPE and the Prompt Problem.
4. **Submit** — one PDF `Wk11_<StudentID>.pdf` at `learn.zcr.ai/submit` (see [SUBMISSION.md](../../SUBMISSION.md)).

## Objectives
- Explain the difference between a digital signature and a MAC, and why signatures underpin public PKI.
- See that every valid ECDSA signature `(r, s)` has a valid twin `(r, n − s)` (same message, same key, different numbers).
- Show that a bank that identifies transactions by a hash of the **signature** pays one authorization twice, while an exact replay is caught.
- See that the **low-S** rule rejects this twin, and explain why the transaction id should still come from the signed message.
- Describe the Schnorr proof of knowledge (commitment, challenge, response) in plain words.

## 🔓 The two banks

| Service | Port | Dedup / validity rule | Twin `(r, n−s)` |
|---|---|---|---|
| `vulnerable_app.py` | `:8102` | `txid = sha256(str(r)+str(s))`; accepts any valid `(r, s)` | **accepted** (pays twice) |
| `fixed_app.py` | `:8103` | rejects `s > n//2` first (**low-S / BIP-62**), then dedups the same way | **rejected** (`403`) |

Each bank holds its **own** SECP256k1 keypair, generated fresh at container start (no private key is ever committed). `GET /sign` is a lab convenience that signs the one fixed message `withdraw 100 to attacker`. The owner authorized **one** withdrawal of 100; when the total exceeds 100 the bank returns the flag.

The fixed bank stops this twin only. A second fresh low-S signature for the same message still passes its signature-hash dedup (worksheet step 10 shows it), so a real system should take the transaction id from the signed message, not from the signature.

## Files
| File | What it is |
|---|---|
| `docker-compose.yml`, `requirements.txt` | the two banks (installs `flask`, `requests`, `ecdsa`) |
| `bank.py` | the student helper: `vuln\|fixed sign`, `vuln\|fixed pay original\|twin` (standard library only, runs in the container) |
| `vulnerable_app.py`, `fixed_app.py` | the two banks |
| `exploit.py` | the automated confirmation (instructor / optional), see below |
| `img/signature-malleability.svg` | picture used on the slides |

## Run it (what the worksheet does)

```bash
cd labs/week11-signatures-zkp
docker compose up -d
docker compose exec vulnerable python bank.py vuln sign
docker compose exec vulnerable python bank.py vuln pay original
docker compose exec vulnerable python bank.py vuln pay original   # 409 replay
docker compose exec vulnerable python bank.py vuln pay twin       # 200, total 200, flag
docker compose exec vulnerable python bank.py fixed sign
docker compose exec vulnerable python bank.py fixed pay original  # 200, total 100
docker compose exec vulnerable python bank.py fixed pay twin      # 403
docker compose down
```

`bank.py sign` saves the signature in `/tmp` inside the container so `pay` can use it; after a restart run `sign` again.

## Automated check (`exploit.py`, optional)
`exploit.py` runs the same story from **fresh state** and prints two `PASS` lines. Because the banks keep their totals in memory, run it only after `docker compose down && docker compose up -d --wait`, never after the manual steps:

```bash
docker compose down && docker compose up -d --wait
docker compose exec -e VULN_HOST=vulnerable -e FIXED_HOST=fixed vulnerable python exploit.py
```

Expect `100 → 200` with a flag on `:8102`, and one accepted withdrawal then a rejected twin (`403`, no flag) on `:8103`. Per-student flag, if the instructor assigns one: set `SC_FLAG_SALT` and run `python3 instructor/seed_flags.py env <STUDENT_ID> > labs/week11-signatures-zkp/.env` before `docker compose up -d --wait`; otherwise `FLAG_SIG` is the shared local placeholder.

**Verified 15 Nov 2026:** every command of the worksheet was run in order from a stopped lab; a second `fixed sign` + `fixed pay original` returns total `200` with the flag (low-S alone is not a full fix). Signatures and txids differ every run (fresh keypair per boot and a random nonce `k`); the flag text is stable. An exact replay of the same `(r, s)` returns `409`; a bad signature returns `403`; a wrong message returns `400`.

## Deliverable
The common 60 points plus the assigned 40, as in the worksheet rubric. AIR-Sec keeps every deliverable of its form.

## Known dependency risk (accepted, not fixed)
This lab's `ecdsa` dependency carries **CVE-2024-23342 / GHSA-wj6h-64fc-37mp** (a "Minerva" timing
attack that can leak the signing nonce via response-time measurements) — **there is no patched
version**; the `python-ecdsa` maintainers have stated side-channel resistance is out of scope for
the project and no fix is planned. Every other Dependabot finding on this repo (`flask`,
`cryptography`, `requests`) was fixed by bumping to a patched release; this one can't be.

**Accepted here, not overlooked, because:** the keypair is generated fresh in-memory at container
startup and discarded on teardown (never reused, never of value beyond the lab run), the container
is an ephemeral local sandbox, not an internet-facing service, and this week's actual lesson
(signature malleability, `(r,s)` → `(r,n-s)` — not nonce reuse) is a *separate, deliberate, far easier* attack than a timing
side-channel would be. If this lab is ever deployed somewhere timing measurements from an
untrusted network are realistic (e.g. exposed on a shared CTFd host to many students
simultaneously), reconsider migrating to `cryptography`'s own EC signing (`ec.generate_private_key`
+ `utils.decode_dss_signature` to get raw `(r, s)`) — not done here as it would require rewriting
and re-verifying `vulnerable_app.py`/`fixed_app.py`/`exploit.py`, a larger change than a version bump.

## References
- Boneh & Shoup, *A Graduate Course in Applied Cryptography*, ch. 8 (digital signatures) & the
  Schnorr / Fiat–Shamir treatment — free online.
- Bitcoin **BIP-62** (*Dealing with malleability*) and **BIP-146** (*Dealing with signature
  encoding malleability*) — historical low-S proposals, not a complete transaction-identity fix.
- Decker and Wattenhofer, [Bitcoin Transaction Malleability and MtGox](https://arxiv.org/abs/1403.6676) (2014): distinguish the exchange's claim from the paper's measured evidence.
- [RFC 8235](https://www.rfc-editor.org/rfc/rfc8235.html), Schnorr NIZK proof and its assumptions.
- NIST FIPS 186-5 — *Digital Signature Standard* (ECDSA, EdDSA).
- RFC 8032 — *Edwards-Curve Digital Signature Algorithm (EdDSA)*.
- `ecdsa` PyPI library docs — `sigdecode_string` / `sigencode_string` for raw `(r, s)` access.
