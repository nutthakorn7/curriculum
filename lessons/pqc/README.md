# {{ slot_label }} — Post-Quantum Cryptography: Lamport One-Time Signatures and Key Reuse

**Topic:** Post-quantum cryptography (PQC) — the quantum threat, the four PQC families, and
hash-based signatures · **Kind:** LAB
**Concepts:** Shor vs. Grover, harvest-now-decrypt-later, crypto-agility, Lamport OTS, one-time
keys, hash-based signatures (SPHINCS+/XMSS) · **Weakness:** one-time signing-key reuse.
> **CWE precision:** CWE-323 names nonce/key-pair reuse *in encryption* and is only an analogy here; CWE-347 does not describe this lab because signature verification itself works correctly.

> **Companion confidentiality lab:** [`hndl/`](hndl/) — "Harvest Now, Decrypt Later" + hybrid KEM.
> This directory is the *signature* half of PQC; `hndl/` is the *key-exchange/confidentiality* half
> (harvest a session, break its classical KEM later, decrypt it; watch a hybrid classical+ML-KEM
> channel resist the same attack). **Lamport is the required core; HNDL is optional, adds 0 points and does not replace Lamport.**

## 100-minute class and assigned worksheet version

**In class:** 10 min Week 14 retrieval quiz/review + 10 min brief explanation + 70 min guided practice + 10 min evidence review/exit = 100 min. The scored Week 15 quiz opens in Week 16.

**Shared core — every student:** Collect fresh Lamport signatures in class, assemble the forgery, test it, compare the one-time-enforcement control and explain the confidentiality/signature migration distinction.

**Preparation and extensions:** Before class, prepare images/dependencies and read the construction only. Collect live key material in class after startup. Complete the longer analysis and the assigned version-specific work outside the core block. The HNDL companion is optional and adds no points.

**70-minute practice:** collect fresh signatures 15; assemble/test the forgery 25; verify the one-time control 20; reasoning 10. Do not spend the fixed server's one signing opportunity during preparation; recreate its state for a new controlled run.


**Assessment:** everyone completes the shared core (60 points) plus **one assigned version** (40 points): Conventional written analysis, or AIR-Sec Audit-the-AI 20 + EiPE 10 + Prompt Problem 10. Both versions total 100. All questions remain available; complete the assigned version's full questions, using out-of-class time for extended responses. The other version is ungraded reference practice, not an additional requirement. Viva/micro-demo questions are formative checks of the submitted explanation, with no separate points or automatic pass/fail score gate.

**Evidence:** record reproducible observations or reasoning and your name/student ID. Where the local target prints a shared placeholder flag, record it as observed; a personalized flag or live CTFd account is not a prerequisite. Follow SUBMISSION.md for the announced hand-in channel.

## ✅ This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security`);
   skim the earlier signature weeks ({{ ref('macs') }} MACs, {{ ref('key-exchanges') }} key exchange) — this week is where the
   *quantum* threat to those primitives lands.
2. **Concept preparation and brief explanation (within the 100-minute plan)** — why a large-scale quantum computer breaks RSA/ECC (Shor) but only
   dents AES/SHA (Grover); "harvest now, decrypt later"; the four PQC families; NIST's ML-KEM
   (Kyber) and ML-DSA (Dilithium); hash-based signatures and the one-time-key discipline;
   crypto-agility as the real engineering lesson. Slides: `{{ slides }}` *(see course plan)*.
3. **Practice and assigned-version work (core in class; extensions outside class)** — play the signature game below, forge an admin signature by exploiting a
   **reused Lamport one-time key**, capture your flag, then complete **Worksheet 15**
   (`worksheet.md`, shared practical plus the assigned Conventional written questions or AIR-Sec Audit-the-AI/EiPE/Prompt).
   Kickoff: `docker compose up`.
4. **Submit** — shared-core evidence/reasoning plus your assigned 40-point version in the worksheet PDF via [SUBMISSION.md](../../SUBMISSION.md). Include the observed flag/log artifact where applicable. Supplied exploit/reference code does not require an unchanged GitHub commit.

## Objectives
- Explain **why quantum matters for cryptography**: Shor's algorithm breaks RSA/ECC outright,
  Grover's only halves symmetric/hash security (a doubling of key/output length mitigates it).
- Explain "**harvest now, decrypt later**" and why it makes PQC migration urgent *today* even
  though large quantum computers do not yet exist.
- Name the **four PQC families** (lattice, hash-based, code-based, multivariate) and what NIST's
  **ML-KEM** (Kyber, a KEM) and **ML-DSA** (Dilithium, a signature) are each *for*.
- Explain a **hash-based signature** (Lamport → SPHINCS+) and its defining limitation: a Lamport
  keypair is a **one-time signature (OTS)** — its normal security guarantee assumes one signed message. Re-signing the same bit string deterministically reveals no additional preimages, but this toy server uses a conservative one-use policy to avoid key-state errors.
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
docker compose up -d                                  # vulnerable_app.py on :8100, fixed_app.py on :8101
docker compose exec vulnerable python lamport.py sign 00000000   # step-by-step helper: sign, both, forge
docker compose exec -e FIXED_HOST=fixed vulnerable python exploit.py   # PASS on :8100 (flag), PASS on :8101 (correctly defeated); exit 0
docker compose down
```
These commands run **inside the `vulnerable` container**, so you need no Python on your own computer and no `curl`. `lamport.py` (standard library only) has three subcommands: `sign <hex>` signs a message and checks bit 0, `both <bit>` shows both secret tokens of one key position after you signed `00000000` and `ffffffff`, and `forge` builds the admin signature and submits it. Type the `exploit.py` line only once per lab start: the fixed server can sign only once. The downloaded student packet has no `instructor/seed_flags.py`: the default flag is a shared lab placeholder, and your own commands, observations and explanation are the evidence.

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
Complete the shared core (60 points) and only the assigned version (40 points), as listed in the worksheet rubric. Include reproducible evidence/reasoning in your worksheet PDF. All unassigned-version questions remain available for ungraded practice.
Lamport is the required signature core. HNDL is an optional confidentiality extension, with zero additional points and no substitution for the required core.

## References
- NIST FIPS 203 (**ML-KEM** / Kyber), FIPS 204 (**ML-DSA** / Dilithium), FIPS 205
  (**SLH-DSA** / SPHINCS+) — the standardized PQC schemes (2024).
- Bernstein & Lange, *Post-Quantum Cryptography* (survey) — free online; the four families.
- Lamport (1979), *Constructing Digital Signatures from a One-Way Function* — the OTS this lab
  implements.
- NIST, *Migration to Post-Quantum Cryptography* (NCCoE project) — crypto-agility guidance.
- https://en.wikipedia.org/wiki/Lamport_signature · https://en.wikipedia.org/wiki/Shor%27s_algorithm
