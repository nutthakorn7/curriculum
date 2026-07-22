# {{ slot_label }} — Digital Signatures & Zero-Knowledge Proofs

**Topic (KOSEN68 source):** `Week10_Signatures Questions.docx` · **Kind:** HYBRID
(lab-style flag demo + conceptual ZKP content)
**Concepts:** digital signatures vs. MACs, ECDSA/EdDSA, signature malleability, SUF-CMA vs.
EUF-CMA, Schnorr identification, signatures as non-interactive zero-knowledge proofs ·
**Analogous CWE:** CWE-347 (Improper Verification of Cryptographic Signature), CWE-345
(Insufficient Verification of Data Authenticity)

## ✅ This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security`);
   skim last week's recap ({{ ref('hybrid-encryption') }} — hybrid encryption).
2. **Lecture (120 min)** — signatures vs. MACs; RSA/ECDSA/EdDSA; the Schnorr identification
   protocol and the Fiat–Shamir transform (challenge → hash) that turns a zero-knowledge *proof
   of knowledge* into a *signature*; why an ECDSA signature `(r, s)` has a valid twin `(r, n−s)`
   (malleability). Slides: `{{ slides }}` *(not yet written — see course-plan-19weeks.md)*.
3. **Lab (180 min)** — play the signature game below, capture your flag, then complete
   **Worksheet 11** (`worksheet.md`, Part 1 conventional essays + Part 2 AIR-Sec arm). Kickoff:
   `docker compose up`.
4. **Submit** — worksheet PDF + flag → Classroom · exploit code → GitHub. (How: [SUBMISSION.md](../../SUBMISSION.md).)

## Objectives
- Explain the difference between a digital signature and a MAC (asymmetric vs. symmetric key,
  *anyone* can verify vs. only key-holders), and why signatures — not MACs — underpin public PKI.
- Define **signature malleability** and demonstrate it against ECDSA: given a valid signature
  `(r, s)`, produce the valid twin `(r, n − s)` (same message, same key, different bytes).
- Exploit a system that deduplicates transactions **by signature hash** to process one authorized
  withdrawal **twice** (a MtGox-style double-spend), and explain why **low-S / BIP-62**
  normalization closes it.
- Explain a signature as a **non-interactive zero-knowledge proof of knowledge** of the private
  key (Schnorr + Fiat–Shamir), and why **SUF-CMA** (strong unforgeability) is a stronger goal
  than **EUF-CMA** when malleable signatures are used as transaction identifiers.

## How it maps to the concept
The essays (Part 1) cover the *theory*: signatures vs. MACs (Q1), signatures as ZKPs from Schnorr
(Q2), the RSA/ECDSA/EdDSA comparison (Q3), substitution attacks (Q4), and malleability + MtGox +
SUF-CMA (Q5). The lab (Part 2) is the **runnable twin of Q5**: instead of *describing* how
malleability contributed to MtGox, you *perform* it. A demo bank authorizes exactly one
withdrawal with an ECDSA signature and — like the real exchange — treats a hash of the signature
bytes as the transaction id. You submit a valid signature, then its malleated `(r, n−s)` twin, and
because the twin hashes to a different "txid," the bank processes the same authorization twice.

## 🔓 Signature game — "Double-Spend the Bank"
Two Flask targets, same endpoints, different acceptance rule:

| Service | Port | Dedup / validity rule | Vulnerable to `(r, n−s)` malleability? |
|---|---|---|---|
| `vulnerable_app.py` | `:8102` | `txid = sha256(str(r)+str(s))`; accepts any valid `(r,s)` | **Yes** |
| `fixed_app.py` | `:8103` | rejects `s > n//2` first (**low-S / BIP-62**), then dedups | **No** |

**Why it's exciting:** the same signature, mathematically mutated, buys a second withdrawal —
real exchanges have lost real money to exactly this trick.

Each bank holds its **own** SECP256k1 keypair, **generated fresh at container startup** (repo
policy: no private key is ever committed). `GET /sign` is a lab convenience — it signs the one
fixed message `"withdraw 100 to attacker"` with that bank's key so you can obtain a starting
`(r, s)` without owning the key. `POST /withdraw {message, sig_r, sig_s}` verifies the signature,
deduplicates, and processes the withdrawal; when the total moved from a single authorization
exceeds the authorized amount, it returns the flag.

1. **Get a signature:** `GET /sign` on `:8102` → a valid `(r, s)` for the withdraw message.
2. **Withdraw once:** `POST /withdraw` with `(r, s)` → processed, `total_withdrawn = 100`.
3. **Malleate & double-spend:** compute the twin `(r, n − s)` (`n = SECP256k1 order`) — a
   *different* byte string, so a *different* txid, but still a valid signature for the *same*
   message and key. `POST /withdraw` with `(r, n − s)` → processed **again** →
   `total_withdrawn = 200 > 100` authorized → **flag**.
4. **Confirm the fix:** run the identical `(r, s)` then `(r, n − s)` sequence against `:8103`.
   The low-S first submission is accepted (one legitimate withdrawal); the high-S twin is
   **rejected (403)** — no double-process, **no flag**. That is the empirical proof that low-S
   normalization ≠ "just verify the signature."

> **Why "PASS" on the fixed app is *not* "both rejected".** With low-S enforced, the *legitimate*
> withdrawal must still succeed — only the malleated twin is rejected. So the fixed-app PASS
> condition is precisely: **first submission accepted, malleated twin rejected, flag never
> returned.**

## Run it
```bash
cd {{ labpath }}
docker compose up -d          # vulnerable_app.py on :8102, fixed_app.py on :8103
pip install ecdsa requests    # once, on the host
python exploit.py             # defaults to localhost:8102 / localhost:8103 — both ports are published
```
No Docker network name to get right — both apps publish their ports to the host, so `exploit.py`
just talks to `localhost`. (If you'd rather not install anything on the host, run it in a
throwaway container instead: `docker run --rm --network "$(basename "$PWD")_default" -v "$PWD:/w" -w /w
python:3.12-slim bash -c "pip install --no-cache-dir -q ecdsa requests && VULN_HOST=vulnerable
FIXED_HOST=fixed python exploit.py"` — this only works if the directory keeps its checkout name,
since Compose derives the network name from it.)
Expect two `PASS` lines and exit `0`: a double-spend + flag on `:8102`, a rejected twin (no flag)
on `:8103`.

Per-student flag: `python3 ../../instructor/seed_flags.py env <STUDENT_ID> > .env` before
`docker compose up` (once this course's `instructor/seed_flags.py` exists — see
`course-plan-19weeks.md` open decision #4; until then `FLAG_SIG` defaults to
`FLAG{ecdsa_malleable_double_spend}`).

**Evidence artifact (HYBRID note).** This week is HYBRID in the 19-week skeleton but is delivered
with the **flag pattern** (single `docker-compose.yml`, per-student `FLAG_SIG`): the attributable
evidence artifact is the **captured `FLAG_SIG`** returned by the *vulnerable* bank on the second
(malleated) withdrawal. The fixed bank never emits it. Submitting another student's flag is a
violation.

**Verified:** `docker compose up -d` was run on this machine; `exploit.py` ran from a throwaway
container on the compose network. Real captured output:
```
=== Target 1: VULNERABLE bank (dedup by signature hash) ===
[*] (vuln) message      = 'withdraw 100 to attacker'
[*] (vuln) s   (low-S)  = 13056399202723869400706208410144883875844706484262026735256855771853935945737   low-S? True
[*] (vuln) n-s (twin)   = 102735690034592326022864776598543023976992857794812877647348307369664225548600   low-S? False
[*] (vuln) txid(r,s)    = 9a6b38dd0d220e24
[*] (vuln) txid(r,n-s)  = 5350b66936e15245   (different txid, same transaction)
[*] (vuln) submit (r,s)     -> 200 {"amount":100,"status":"processed","total_withdrawn":100,...}
[*] (vuln) submit (r,n-s)   -> 200 {"amount":100,"double_spend_detected":true,
                                    "flag":"FLAG{ecdsa_malleable_double_spend}","total_withdrawn":200,...}
PASS: malleated twin double-spent on vulnerable app (:8102) -- total_withdrawn=200, flag = FLAG{ecdsa_malleable_double_spend}

=== Target 2: FIXED bank (low-S / BIP-62 enforcement) ===
[*] (fixed) submit (r,s)     -> 200 {"total_withdrawn":100,...}
[*] (fixed) submit (r,n-s)   -> 403 {"error":"non-canonical signature: s must be <= n/2 (BIP-62 low-S)"}
PASS: malleated twin correctly REJECTED by fixed app (:8103) -- first withdrawal accepted, high-S twin -> 403, no flag
```
Exit code `0`. `FLAG_SIG=FLAG{sig_override_test123} docker compose up` was also confirmed to
propagate the override into the captured flag. Negative controls confirmed: a bad signature
(`r=s=1`) → `403`; an **exact byte-for-byte replay** of the same `(r, s)` → `409` (the dedup set
*does* stop identical replays — only the malleated *different-bytes* twin slips through); a wrong
`message` → `400`. **The concrete `r`, `s`, and txids differ every run** (fresh keypair per boot +
random ECDSA nonce `k`) — only the **flag** is stable and attributable; do not expect to
reproduce the exact numbers above.

## Deliverable
The captured flag + the specific `(r, s)` you started from and the twin `(r, n − s)` you submitted
(with both txids), + a short note on why the two share a `(message, pubkey)` yet the vulnerable
bank saw them as two transactions, and why low-S closes the gap. Full tasks: `worksheet.md`.

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
  encoding malleability*) — the low-S rule.
- Wuille et al., the MtGox transaction-malleability incident write-ups (CVE-2014-* era).
- NIST FIPS 186-5 — *Digital Signature Standard* (ECDSA, EdDSA).
- RFC 8032 — *Edwards-Curve Digital Signature Algorithm (EdDSA)*.
- `ecdsa` PyPI library docs — `sigdecode_string` / `sigencode_string` for raw `(r, s)` access.
