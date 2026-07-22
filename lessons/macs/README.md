# {{ slot_label }} — MACs: Hash-Only Cookies and Length-Extension

**Topic (KOSEN68 source):** `Week3_MACs Questions.docx` · **Kind:** LAB
**Concepts:** message authentication codes, secret-prefix hashing, Merkle-Damgard
length-extension, HMAC · **Analogous CWE:** CWE-347 (Improper Verification of Cryptographic
Signature), CWE-290 (Authentication Bypass by Spoofing)

## ✅ This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security`);
   skim last week's recap ({{ ref('hash') }} — hash functions / password cracking).
2. **Lecture (120 min)** — MACs vs. hashes vs. signatures; why `H(key || message)` is not a MAC;
   HMAC's nested construction; timing attacks on tag comparison. Slides: `{{ slides }}`
   *(not yet written — see course-plan-19weeks.md)*.
3. **Lab (180 min)** — play the signature game below, capture your flag, then complete
   **Worksheet 3** (`worksheet.md`, Parts 1–3 incl. *Audit the AI* + *EiPE/Prompt*; Part 5 is an
   appendix, not assigned this week). Kickoff: `docker compose up`.
4. **Submit** — worksheet PDF + flag → Classroom · exploit code → GitHub. (How: [SUBMISSION.md](../../SUBMISSION.md).)

## Objectives
- Explain why a bare hash of `key || message` (or `message || key`) is **not** a secure MAC.
- Execute a SHA-256 length-extension attack to forge a cookie without knowing the secret.
- Explain why HMAC's nested `H(key⊕opad || H(key⊕ipad || message))` construction defeats
  length-extension, and verify that empirically against a fixed target.
- Recognize related MAC-verification pitfalls (non-constant-time comparison, replay) even
  where this week's exploit doesn't target them directly.

## 🔓 Signature game — "Forge the Admin Cookie"
Two Flask targets, same endpoints, different signature scheme:

| Service | Port | Signature scheme | Vulnerable to length-extension? |
|---|---|---|---|
| `vulnerable_app.py` | `:8092` | `sig = SHA256(MAC_SECRET + data)` (secret-prefix hash) | **Yes** |
| `fixed_app.py` | `:8093` | `sig = HMAC-SHA256(MAC_SECRET, data)` | **No** |

**Why it's exciting:** forging your way into someone else's cookie with pure math, no password
needed, feels like a magic trick — until HMAC slams the door shut.

Both issue a cookie at `GET /login?user=<name>` encoding `data="user=<name>&admin=false"` plus a
signature. `GET /admin` recomputes the signature and, if it matches **and** `data` contains
`admin=true`, returns the flag.

1. **Capture:** log in as `guest` against `:8092` and grab the `data`/`sig` cookie pair.
2. **Forge:** without ever learning `MAC_SECRET`, compute a new `(data, sig)` pair that appends
   `&admin=true` to the message and still validates — using the length-extension property of
   SHA-256's Merkle-Damgard construction (`exploit.py` does this from scratch, no crypto library
   beyond the standard `hashlib`/`hmac`/`struct`).
3. **Cash in:** replay the forged cookie against `/admin` on `:8092` → flag.
4. **Confirm the fix:** replay the *same* forgery technique against `:8093` (HMAC) → must be
   rejected (`403`, no flag). This is the empirical proof that HMAC ≠ "hash with a key stuck on."

**MAC_SECRET length:** both apps use a demo secret that is **exactly 16 ASCII bytes**
(`0123456789abcdef` by default — override via the `MAC_SECRET` env var, keeping it 16 bytes so
`exploit.py`'s `SECRET_LEN` constant still matches). `exploit.py` assumes the secret's *length*
is known (a realistic assumption in practice — e.g. a fixed-width key field, or brute-forceable
over a small range of plausible lengths) but never its *value*.

## Run it
```bash
cd {{ labpath }}
docker compose up -d          # vulnerable_app.py on :8092, fixed_app.py on :8093
python exploit.py             # PASS on :8092 (flag), PASS on :8093 (correctly rejected); exit 0
```
Per-student flag: `python3 ../../instructor/seed_flags.py env <STUDENT_ID> > .env` before
`docker compose up` (once this course's `instructor/seed_flags.py` exists — see
`course-plan-19weeks.md` open decision #4; until then `FLAG_MACS` defaults to
`FLAG{macs_demo}`).

**Verified:** `docker compose up -d` followed by `python exploit.py` was run against live
containers on this machine; both PASS checks printed and the script exited `0`. `MAC_SECRET`
env-var override was also confirmed to change both the captured signature and the forged
signature consistently, and negative controls (`/admin` with no cookie, `/admin` with a
legitimate non-admin cookie) both correctly returned `403`.

## Deliverable
The captured flag + your forged `(data, sig)` pair + a short note on exactly which byte range in
`data` is the SHA-256 glue padding your forgery relied on, and why HMAC closes the gap. Full
tasks: `worksheet.md`.

## References
- Boneh & Shoup, *A Graduate Course in Applied Cryptography*, ch. 6 (MACs) — free online.
- RFC 2104 — *HMAC: Keyed-Hashing for Message Authentication*.
- https://en.wikipedia.org/wiki/Length_extension_attack
- NIST FIPS 198-1 — *The Keyed-Hash Message Authentication Code (HMAC)*.
