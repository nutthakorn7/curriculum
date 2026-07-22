# {{ slot_label }} — AES / Block-Cipher Modes: CBC Bit-Flipping and Malleability

**Topic (KOSEN68 source):** `Week4_AES Questions.docx` · **Kind:** LAB
**Concepts:** AES block cipher, ECB/CBC/GCM modes, IV vs. nonce, malleability, authenticated
encryption (AEAD) · **Analogous CWE:** CWE-353 (Missing Support for Integrity Check), CWE-649
(Reliance on Obfuscation/Encryption Without Integrity), CWE-347 (Improper Verification of a
Cryptographic Signature)

## ✅ This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security`);
   skim last week's recap ({{ ref('macs') }} — MACs / length-extension). Notice the through-line: {{ ref('macs') }}
   showed a *keyed hash* isn't a MAC; {{ slot_label }} shows *encryption* isn't integrity.
2. **Lecture (120 min)** — AES the block cipher vs. the *mode* that wraps it; why ECB leaks
   patterns; CBC/IV mechanics; malleability of unauthenticated CBC; nonces in GCM and why reuse
   is catastrophic; AEAD (GCM / ChaCha20-Poly1305) as the modern default. Slides:
   `{{ slides }}` *(not yet written — see course-plan-19weeks.md)*.
3. **Lab (180 min)** — play the token game below, capture your flag, then complete
   **Worksheet 4** (`worksheet.md`, Part 1 Conventional + Part 2 AIR-Sec incl. *Audit the AI* +
   *EiPE* + *Prompt Problem* + viva). Kickoff: `docker compose up`.
4. **Submit** — worksheet PDF + flag → Classroom · exploit code → GitHub. (How: [SUBMISSION.md](../../SUBMISSION.md).)

## Objectives
- Explain why **AES itself being secure** does not make an AES-*based* scheme secure — the
  **mode** (ECB/CBC/GCM) and the **absence/presence of integrity** decide it.
- Execute a **CBC bit-flipping** attack: alter the decrypted plaintext of an unauthenticated
  AES-CBC token (`role=guest` → `role=admin`) **without the key**, by XOR-ing bytes into the
  previous ciphertext block.
- Explain why **authenticated encryption** (AES-GCM here) defeats the same tampering — the tag
  check rejects any altered ciphertext — and verify that empirically against a live target.
- Recognize the family of related mode pitfalls (ECB pattern leakage, IV/nonce reuse, "encrypt
  but don't authenticate") even where this week's exploit targets only malleability.

## 🔓 Token game — "Flip Your Way to Admin"
Two Flask targets, same endpoints, different token scheme:

| Service | Port | Token scheme | Malleable / tamperable? |
|---|---|---|---|
| `vulnerable_app.py` | `:8096` | `base64(IV ‖ AES-256-**CBC**(plaintext))` — **no MAC/tag** | **Yes** — CBC bit-flip |
| `fixed_app.py` | `:8097` | `base64(nonce ‖ AES-256-**GCM**(plaintext) ‖ tag)` — AEAD | **No** — tag check rejects |

**Why it's exciting:** flipping bytes you can't even read to seize admin is the closest thing to
"hacking in a movie" this course gets.

Both issue a session token at `GET /login` encoding a **fixed server-side plaintext** whose role
field is `guest`. `GET /whoami` decrypts and reports the parsed role. `GET /admin` returns the
flag **iff** the parsed role is `admin`.

1. **Capture:** `GET /login` on `:8096`; grab the `token` cookie (base64 of `IV ‖ C0 ‖ C1`).
2. **Flip:** without ever learning the AES key, XOR a small delta into the ciphertext block that
   sits **before** the role block, so the *next* block decrypts to `role=admin` instead of
   `role=guest` (`exploit.py` does this with pure byte math — no crypto library needed for the
   attack itself).
3. **Cash in:** replay the tampered token against `/admin` on `:8096` → flag.
4. **Confirm the fix:** apply the *same* tampering idea to a `:8097` (GCM) token → must be
   **rejected** (`403`, no flag). This is the empirical proof that *encryption ≠ integrity*, and
   that AEAD is what closes the gap.

### The block layout (why the flip is clean)
The server plaintext is a **fixed 32-byte constant** (two AES blocks); `/login` takes no input
that shifts the role offset, so the target byte range is deterministic:

```
            plaintext bytes            token bytes (after base64-decode)
Block 0     [ 0..15]  b"comment=FILLER!!"    IV = token[ 0:16]   (random per login)
Block 1     [16..31]  b"role=guest;xpad0"    C0 = token[16:32]   <- we edit THIS block
                                             C1 = token[32:48]
```
CBC decrypts block 1 as **`P1 = AES_decrypt(C1) XOR C0`**. So flipping byte `k` of **C0** flips
byte `k` of **P1** — and turns block 0's plaintext (`comment=FILLER!!`) into unpredictable
garbage, which is fine because the app never reads the comment. `guest` sits at `P1[5..9]` and
`admin` is the same length (5 bytes), so the flip is a clean, length-preserving XOR:
`C0[5+i] ^= guest[i] ^ admin[i]` for `i = 0..4`, i.e. edit `token[21..25]`.

## Run it
```bash
cd {{ labpath }}
docker compose up -d          # vulnerable_app.py on :8096, fixed_app.py on :8097
python exploit.py             # PASS on :8096 (flag), PASS on :8097 (correctly rejected); exit 0
```
Per-student flag: `python3 ../../instructor/seed_flags.py env <STUDENT_ID> > .env` before
`docker compose up` (once this course's `instructor/seed_flags.py` exists — see
`course-plan-19weeks.md` open decision #4; until then `FLAG_AES` defaults to
`FLAG{aes_cbc_is_malleable}`).

**Verified:** `docker compose up -d` followed by `python exploit.py` was run against live
containers on this machine; both PASS checks printed (`:8096` returned the flag to the
bit-flipped token; `:8097` returned `403` with no flag to the same tampering) and the script
exited `0`. `/whoami` confirmed the tampered vuln token parses as `role=admin` while the original
parses as `role=guest`. An `AES_KEY` **and** `FLAG_AES` env-var override was also confirmed: the
exploit still succeeds and returns the *new* flag — proving the attack never depends on the key
(it is pure ciphertext malleability). Negative controls confirmed: `/admin` with no cookie →
`403`; `/admin` with a legitimate (unflipped) `role=guest` token → `403`.

## Deliverable
The captured flag + your tampered token (base64) + a short note stating **exactly which token
byte range** you XOR-ed and **why editing that block** (not the role block itself) is what
changes `guest` → `admin`, plus one sentence on why AES-GCM rejects the identical edit. Full
tasks: `worksheet.md`.

## References
- Boneh & Shoup, *A Graduate Course in Applied Cryptography*, ch. 4–5 (block ciphers, modes, AE)
  — free online.
- NIST SP 800-38A (block-cipher modes: ECB/CBC/…) and SP 800-38D (GCM).
- RFC 5116 — *An Interface and Algorithms for Authenticated Encryption* (AEAD).
- https://en.wikipedia.org/wiki/Malleability_(cryptography) and
  https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation
