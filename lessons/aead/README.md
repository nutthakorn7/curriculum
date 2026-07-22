# {{ slot_label }} — Authenticated Encryption (AEAD): the CBC Padding Oracle

**Topic:** *(new topic — not in KOSEN68; built fresh)* · **Kind:** LAB
**Concepts:** authenticated encryption (AEAD), unauthenticated-CBC malleability, PKCS#7 padding
oracle, AES-GCM, encrypt-then-MAC · **Analogous CWE:** CWE-347 (Improper Verification of
Cryptographic Signature), CWE-757 (Selection of Less-Secure Algorithm), CWE-208
(Observable Timing/Response Discrepancy — the side channel)

This is the **capstone of the symmetric block**: {{ ref('macs') }} gave you a MAC (integrity), {{ ref('aes-modes') }} gave
you AES-CBC (confidentiality) and showed CBC ciphertext is *malleable*. Bolt those two together
*wrong* and you get a **padding oracle** — an attacker decrypts your ciphertext byte-by-byte
without ever seeing the key. Bolt them together *right* — encrypt-then-MAC, or use a single AEAD
primitive like AES-GCM — and the attack evaporates. That "combine them correctly" primitive is
**AEAD**.

## ✅ This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security`);
   re-skim {{ ref('aes-modes') }} (AES-CBC, bit-flipping malleability) and {{ ref('macs') }} (MACs) — this week is those two
   combined.
2. **Lecture (120 min)** — what AEAD guarantees (confidentiality + integrity + authenticity in one
   primitive); Encrypt-then-MAC vs MAC-then-Encrypt vs Encrypt-and-MAC; why unauthenticated CBC
   leaks to a padding oracle; why AES-GCM has no padding step and checks the tag first. Slides:
   `{{ slides }}` *(not yet written — see course-plan-19weeks.md)*.
3. **Lab (180 min)** — play the decryption game below, capture your flag, then complete
   **Worksheet 6** (`worksheet.md`, Part 1 Conventional + Part 2 AIR-Sec incl. *Audit the AI* +
   *EiPE* + *Prompt Problem*). Kickoff: `docker compose up`.
4. **Submit** — worksheet PDF + flag → Classroom · exploit notes → GitHub. (How: [SUBMISSION.md](../../SUBMISSION.md).)

## Objectives
- State what **AEAD** stands for and the three guarantees it delivers in one primitive.
- Explain a **padding oracle**: how a single distinguishable "bad padding" response turns
  unauthenticated CBC into a byte-by-byte decryption of arbitrary ciphertext — *without the key*.
- Run the standard CBC padding-oracle attack to recover a secret plaintext (containing your flag)
  from ciphertext alone, using only a 200-vs-403 side channel.
- Explain why **AES-GCM** (an AEAD cipher) has no padding oracle — stream mode means no padding to
  probe, and the authentication tag is verified *before* any plaintext is released — and verify
  that empirically against a fixed target that returns a uniform error for every failure.
- Distinguish the *provably safe* generic composition (encrypt-then-MAC) from the unsafe ones.

## 🔓 Decryption game — "Read the Secret Without the Key"
Two Flask targets, same endpoints, different cipher:

| Service | Port | Cipher | Vulnerable to a padding oracle? |
|---|---|---|---|
| `vulnerable_app.py` | `:8098` | AES-256-**CBC**, unauthenticated, `/decrypt` leaks padding validity | **Yes** |
| `fixed_app.py` | `:8099` | AES-256-**GCM** (AEAD), `/decrypt` returns a **uniform** error | **No** |

**Why it's exciting:** a padding oracle turns a plain 403 error into a skeleton key, recovering a
whole secret one byte at a time from nothing but yes/no answers.

Both serve the *same* secret message (which **contains the flag**) at `GET /secret` as
base64. Both expose `POST /decrypt {"ciphertext": "<base64>"}`. The difference is the *decrypt
response*:

- **Vulnerable (`:8098`, CBC):** `200` if the decrypted plaintext has **valid PKCS#7 padding**,
  `403 "bad padding"` if not. Those two distinguishable answers are the **oracle** — the endpoint
  *never returns the plaintext*, yet the attacker recovers it purely from the 200/403 signal.
- **Fixed (`:8099`, GCM):** `200` only if the 128-bit tag verifies; **`403` (uniform)** for *any*
  failure — bad base64, wrong length, bad nonce, tag mismatch — all indistinguishable. No signal.

1. **Grab the ciphertext:** `GET /secret` on `:8098` → `base64(IV || ct)`.
2. **Recover it:** using only the `/decrypt` oracle, run the CBC padding-oracle attack to recover
   the full plaintext **byte-by-byte, without the AES key** (`exploit.py` implements it from
   scratch — no crypto library needed on the attacker side, only `requests`).
3. **Read the flag:** the recovered plaintext is `msg:FLAG{...}` → that's your flag.
4. **Confirm the fix:** run the *identical* attack against `:8099` (AES-GCM). It gets **zero**
   usable signal (every query is `403`), recovers nothing → the AEAD app is safe.

**The key is never known to the attacker.** The whole point is that unauthenticated CBC + a
padding side channel gives *decryption without the key*; AEAD removes both the side channel and
the malleability.

## Run it
```bash
cd {{ labpath }}
docker compose up -d          # vulnerable_app.py on :8098, fixed_app.py on :8099
python exploit.py             # PASS on :8098 (recovers plaintext + flag), PASS on :8099
                              #   (attack gets no signal); exit 0
docker compose down
```
Per-student flag: `python3 ../../instructor/seed_flags.py env <STUDENT_ID> > .env` before
`docker compose up` (once this course's `instructor/seed_flags.py` exists — see
`course-plan-19weeks.md` open decision; until then `FLAG_AEAD` defaults to
`FLAG{padding_oracle_leaks_all}`). The exploit derives the block count from `/secret`, so
flags of any length work.

**Verified:** `docker compose up -d --build` (from a scratch copy — OneDrive placeholders can
break in-place `docker build`) followed by `python exploit.py` was run against live containers on
this machine. Both PASS checks printed and the script exited `0`: the padding oracle recovered
the full plaintext `msg:FLAG{padding_oracle_leaks_all}` from `:8098` **without the key**, and the
identical attack recovered **nothing** from the AES-GCM app on `:8099` (uniform `403`). The
`FLAG_AEAD` env-override was confirmed with a different-length flag (`FLAG{aead_student_42_xyz}` →
a 2-block ciphertext instead of 3) — the exploit derived the new block count from `/secret` and
recovered it correctly, PKCS#7 padding stripped. Negative controls confirmed: garbage/empty
ciphertext → `403` on both apps; a tampered GCM tag → `403` on `:8099`; the original secret →
`200` on both.

## Deliverable
The recovered flag + a short note on **which byte you force to `0x01`, `0x02 0x02`, … in the
forged previous block**, why that reveals one byte of the intermediate value `D(C_t)` per query,
and why AES-GCM has no equivalent probe. Full tasks: `worksheet.md`.

## References
- Boneh & Shoup, *A Graduate Course in Applied Cryptography*, ch. 9 (Authenticated Encryption) —
  free online.
- Vaudenay (2002), *Security Flaws Induced by CBC Padding* — the original padding-oracle paper.
- NIST SP 800-38D — *Galois/Counter Mode (GCM) and GMAC*.
- RFC 5116 — *An Interface and Algorithms for Authenticated Encryption* (defines the AEAD API).
- https://en.wikipedia.org/wiki/Padding_oracle_attack
