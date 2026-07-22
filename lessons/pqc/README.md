# {{ slot_label }} — Post-Quantum Cryptography: Lamport One-Time Signatures and Key Reuse

**Topic:** Post-quantum cryptography (PQC) — the quantum threat, the four PQC families, and
hash-based signatures · **Kind:** LAB
**Concepts:** Shor vs. Grover, harvest-now-decrypt-later, crypto-agility, Lamport OTS, one-time
keys, hash-based signatures (SPHINCS+/XMSS) · **Analogous CWE:** CWE-323 (Reusing a Nonce/Key
Pair in Encryption), CWE-347 (Improper Verification of Cryptographic Signature)

> **Companion confidentiality lab:** [`hndl/`](hndl/) — "Harvest Now, Decrypt Later" + hybrid KEM.
> This directory is the *signature* half of PQC; `hndl/` is the *key-exchange/confidentiality* half
> (harvest a session, break its classical KEM later, decrypt it; watch a hybrid classical+ML-KEM
> channel resist the same attack). Run either or both.

## ✅ This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security`);
   skim the earlier signature weeks ({{ ref('macs') }} MACs, {{ ref('key-exchanges') }} key exchange) — this week is where the
   *quantum* threat to those primitives lands.
2. **Lecture (120 min)** — why a large-scale quantum computer breaks RSA/ECC (Shor) but only
   dents AES/SHA (Grover); "harvest now, decrypt later"; the four PQC families; NIST's ML-KEM
   (Kyber) and ML-DSA (Dilithium); hash-based signatures and the one-time-key discipline;
   crypto-agility as the real engineering lesson. Slides: `{{ slides }}` *(see course plan)*.
3. **Lab (180 min)** — play the signature game below, forge an admin signature by exploiting a
   **reused Lamport one-time key**, capture your flag, then complete **Worksheet 15**
   (`worksheet.md`, Part 2 Conventional + Part 3 AIR-Sec incl. *Audit the AI* + *EiPE/Prompt*).
   Kickoff: `docker compose up`.
4. **Submit** — worksheet PDF + flag → Classroom · exploit code → GitHub. (How: [SUBMISSION.md](../../SUBMISSION.md).)

## Objectives
- Explain **why quantum matters for cryptography**: Shor's algorithm breaks RSA/ECC outright,
  Grover's only halves symmetric/hash security (a doubling of key/output length mitigates it).
- Explain "**harvest now, decrypt later**" and why it makes PQC migration urgent *today* even
  though large quantum computers do not yet exist.
- Name the **four PQC families** (lattice, hash-based, code-based, multivariate) and what NIST's
  **ML-KEM** (Kyber, a KEM) and **ML-DSA** (Dilithium, a signature) are each *for*.
- Explain a **hash-based signature** (Lamport → SPHINCS+) and its defining limitation: a Lamport
  keypair is a **one-time signature (OTS)** — secure *if and only if* it signs one message.
- **Execute** the key-reuse attack: recover a full Lamport private key from two signatures under
  a reused key (a message and its complement) and forge a signature on a target message.
- Explain why the fix is **operational, not mathematical** — refuse the second signature — and
  connect this to stateful (XMSS/LMS) vs. stateless (SPHINCS+) hash-based schemes.

## 🔓 Signature game — "Forge the Admin Signature"
Two Flask targets, same Lamport one-time signature scheme, one difference:

| Service | Port | One-time key rule | Forgeable by key reuse? |
|---|---|---|---|
| `vulnerable_app.py` | `:8100` | **REUSES** one keypair on every `/sign` | **Yes** |
| `fixed_app.py` | `:8101` | Signs **at most once**; 2nd `/sign` → `403` | **No** |

**Why it's exciting:** a keypair meant to sign exactly once, signed twice — and the private key
just falls out of the math, no brute force required.

Both hold ONE fixed Lamport keypair over a **32-bit** message that is signed **directly** (no
pre-hash — so every message bit is attacker-controllable). Endpoints on both:

- `POST /sign {message_hex}` → the Lamport signature (list of 32 preimages, one per bit).
- `POST /verify {message_hex, sig}` → `{"valid": bool}`.
- `POST /admin {sig}` → if `sig` is a **valid Lamport signature on the fixed admin message**
  `0xA5A5C3C3` under the server's public key, return `{"flag": FLAG_PQC}`; else `403`.
- `GET /pubkey` → the public key (public by definition; the attack does *not* need it — it
  recovers the **private** key).

**Shared baseline (both apps):** `/sign` **refuses to sign the admin message directly** (`403`)
— otherwise the flag would be a one-line `curl` and there would be no lesson. So the *only*
difference between the two apps is the one-time enforcement, which is exactly the variable this
week teaches.

1. **Collect:** `POST /sign` a message `M = 0x00000000` and its bitwise complement
   `~M = 0xFFFFFFFF` against `:8100`. A Lamport signature reveals, per bit, the ONE secret
   preimage selected by that bit's value; `M` and `~M` differ in *every* bit, so between the two
   responses you learn **both** preimages for **every** position — the entire private key.
2. **Forge:** with the full private key, assemble a valid signature on the admin message
   `0xA5A5C3C3` **offline** — select, per bit, the preimage that bit needs. (`exploit.py` does
   this with nothing beyond the standard-library `hashlib` + `requests`.)
3. **Cash in:** `POST /admin {sig}` on `:8100` → flag.
4. **Confirm the fix:** run the *identical* two-signature attack against `:8101`. The **second**
   `/sign` is refused (`403` "one-time key already used"), so you never obtain the complementary
   preimage set, cannot complete the private key, and `/admin` rejects the forgery (`403`, no
   flag). This is the empirical proof that a one-time signature's security is a **usage
   discipline**, not just a hash property.

## Run it
```bash
cd {{ labpath }}
docker compose up -d          # vulnerable_app.py on :8100, fixed_app.py on :8101
python exploit.py             # PASS on :8100 (flag), PASS on :8101 (correctly defeated); exit 0
```
Per-student flag: `python3 ../../instructor/seed_flags.py env <STUDENT_ID> > .env` before
`docker compose up` (once this course's `instructor/seed_flags.py` exists — see the shared
`software-security` template; add a `"pqc"` entry to its `CHALLENGES` list). Until then
`FLAG_PQC` defaults to `FLAG{lamport_one_time_only}`. Set `LAMPORT_SEED=<anything>` to make the
keypair deterministic for reproducible grading (unset = fresh random key each boot).

**Verified:** `docker compose up -d` followed by `python exploit.py` was run against live
containers on this machine. Both PASS checks printed and the script exited `0`:
`vulnerable (:8100)` forgery succeeded (flag captured) and `fixed (:8101)` attack defeated (2nd
`/sign` refused with `403`, forgery rejected). Additional checks confirmed on live containers:
(a) the `FLAG_PQC` env override propagates into the captured flag and `LAMPORT_SEED` yields a
reproducible keypair; (b) the **direct-sign bypass is closed** — `POST /sign` of the admin
message `a5a5c3c3` returns `403` on *both* apps, while a normal non-admin message signs `200`;
(c) negative controls — `/admin` with no signature → `403`, and `/admin` with a valid signature
on a *non-admin* message → `403`; (d) `exploit.py` exits **nonzero** when the "fixed" target is
made to reuse its key (pointing `FIXED_PORT` at `:8100`), proving the pass/fail gate is real.

## Deliverable
The captured flag + your recovered private key (or at least: for one bit position, both
preimages and the `SHA-256` hashes that show each matches the published public key) + a short
note explaining, in your own words, why signing `M` and `~M` reveals the *whole* key while
signing `M` alone reveals only *half*. Full tasks: `worksheet.md`.

## References
- NIST FIPS 203 (**ML-KEM** / Kyber), FIPS 204 (**ML-DSA** / Dilithium), FIPS 205
  (**SLH-DSA** / SPHINCS+) — the standardized PQC schemes (2024).
- Bernstein & Lange, *Post-Quantum Cryptography* (survey) — free online; the four families.
- Lamport (1979), *Constructing Digital Signatures from a One-Way Function* — the OTS this lab
  implements.
- NIST, *Migration to Post-Quantum Cryptography* (NCCoE project) — crypto-agility guidance.
- https://en.wikipedia.org/wiki/Lamport_signature · https://en.wikipedia.org/wiki/Shor%27s_algorithm
