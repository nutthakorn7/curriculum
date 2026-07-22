# Worksheet 4 — AES / Block-Cipher Modes: CBC Bit-Flipping (3 hrs)

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Topic source:** `Week4_AES Questions.docx` (KOSEN68) — 10 essay questions, ported into
> **Part 1** (Conventional arm) below.
> **Token game:** "Flip Your Way to Admin" (CBC bit-flipping against an unauthenticated
> AES-256-CBC session token; the AES-GCM version resists it).

> **Ethics note:** Attack only the two local containers this lab spins up
> (`vulnerable_app.py` / `fixed_app.py`, ports 8096/8097). Tampering with session tokens or
> ciphertext on systems you don't own and aren't authorized to test is illegal. Keep your
> `AES_KEY` and flag inside this lab environment.

## Student Information
| Name | Student ID | Date | Group | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

# Part 1 — Conventional Arm: Written Questions (ported from KOSEN68, Q1–Q10)

Answer each in your own words (4–8 sentences; more where the question asks for a design or a
comparison). **This is a normal written/essay task — no AI-resilience layer applies to this
part; answer it yourself.** These questions are graded on your reasoning, and an instructor may
ask you to defend any answer verbally (see the viva in Part 2).

**Q1.** Why is **AES-ECB** not recommended for real-world data even though AES itself is secure?
(Think about what happens to two identical plaintext blocks. The classic "ECB penguin" image is
the canonical illustration.)

**Q2.** What is the risk if **AES-CBC uses the same IV repeatedly**? Explain simply — what does
an observer learn about two messages that begin with the same bytes?

**Q3.** If a system **encrypts data but does NOT verify integrity** (no MAC, no auth tag), what
attacks become possible? (This is exactly the vulnerability the lab exploits — answer in general
terms, then note how the lab is a concrete instance.)

**Q4.** Why do modern systems (TLS/HTTPS) prefer **AES-GCM over AES-CBC**?

**Q5.** What is a **"nonce"** in AES-GCM, and why must it **never repeat** (for a given key)?

**Q6.** If a **GCM nonce is accidentally reused**, what advantage does the attacker gain?
(Compare the two ciphertexts produced under the same key+nonce — what leaks, and what happens to
GCM's *authentication* guarantee specifically?)

**Q7.** Between **AES-GCM and ChaCha20-Poly1305**, which is better for **mobile / IoT**, and
why? (Consider hardware AES acceleration vs. its absence, timing/side-channel behavior, and
performance on constrained CPUs.)

**Q8.** Why do disk-encryption systems (**LUKS, BitLocker**) use **AES-XTS** instead of AES-GCM?
(A disk sector is a fixed size with no room to store an extra nonce+tag per sector; what does
that constraint force, and what does XTS give up as a result?)

**Q9.** Why do protocols like **HTTPS require "authenticated encryption"** instead of encryption
alone? (Tie this back to Q3 — what property does confidentiality-only *not* provide?)

**Q10.** If a developer uses **AES-GCM correctly but fails to verify the auth tag** (e.g. calls a
decrypt-without-verify path, or ignores the exception), what could go wrong? (You've now *seen*
what unauthenticated ciphertext lets an attacker do — apply it.)

---

# Part 2 — AIR-Sec Arm

## 2A — Hands-on Lab (180 min)

**Learning goals:** exploit an unauthenticated AES-CBC token via bit-flipping, then verify
AES-GCM (authenticated encryption) closes the gap — the *practical* twin of Part 1's Q3/Q4/Q9.
**Prerequisites:** Docker; Python 3.12 (with the `requests` package) on the host to run
`exploit.py` — or run it inside the `vulnerable` container.

**Environment setup**
```bash
cd {{ labpath }}
docker compose up -d        # vulnerable_app.py on :8096, fixed_app.py on :8097
curl localhost:8096/        # confirm it's up
```

**Task 0 — Onboarding (10 min).** *Goal:* see the vulnerable construction. *Steps:* read
`vulnerable_app.py`'s `issue_token`/`parse_role` functions and the BLOCK LAYOUT comment at the
top; identify exactly which line encrypts the token and confirm it is **AES-CBC with no MAC/tag**
(`_aes_cbc_encrypt`), not GCM. *Deliverable:* quote the line and state which of Q3/Q4 failure
modes it matches.

**Task 1 — Capture a legitimate token (10 min).** *Goal:* get a real token. *Steps:*
`curl -i "localhost:8096/login"`; record the `token` cookie. Then
`curl --cookie "token=<...>" localhost:8096/whoami` → confirm `{"role":"guest"}`. *Deliverable:*
the token value + the `/whoami` output.

**Task 2 — Locate the bytes you must flip (30 min).** *Goal:* understand the attack, not just run
it. *Steps:* base64-decode your token into `IV ‖ C0 ‖ C1` (16 bytes each). On paper (or in your
write-up), explain: CBC decrypts block 1 as `P1 = AES_decrypt(C1) XOR C0`; the plaintext block 1
is `role=guest;xpad0`, so `guest` occupies `P1[5..9]`; therefore to change `P1[5..9]` you XOR
into **C0** at positions `5..9`, i.e. absolute token-byte indices `16+5 .. 16+9 = 21..25`. Write
out the five XOR deltas `guest[i] ^ admin[i]` for `i=0..4`. *Deliverable:* your five deltas (in
hex) and the absolute token indices they apply to.

**Task 3 — Run the flip and cash in the flag (20 min).** *Goal:* confirm the tampered token is
accepted. *Steps:* read `exploit.py`'s `bitflip_cbc_token`; confirm it edits `token[21..25]`
exactly as you computed. Run `python exploit.py` and note the flag it printed. Then reproduce it
by hand with `curl`: take the *forged* token the script printed and
`curl --cookie "token=<forged>" localhost:8096/admin`. *Deliverable:* the flag + your `curl`
command and its JSON output, to convince yourself the script isn't doing anything hidden.

**Task 4 — Confirm GCM rejects the same trick (20 min).** *Goal:* prove the fix works, not just
claim it. *Steps:* `exploit.py` applies the same "flip a ciphertext byte" idea to a `:8097` (GCM)
token; confirm it printed `403`/rejected. Read `fixed_app.py`'s `issue_token`/`parse_role` and
identify the change from `vulnerable_app.py` (CBC → `AESGCM`, and that decrypt now *raises* on a
bad tag). *Deliverable:* the rejection evidence + the diff (in words) between the two token
schemes. **Also answer:** why can't you reproduce the *exact* CBC byte offsets on a GCM token?
(Hint: GCM's layout is `nonce ‖ ct ‖ tag`, not `IV ‖ C0 ‖ C1` — there's no "previous block" to
XOR into, and any edit fails the tag.)

**Task 5 — Explain why, precisely (20 min).** *Goal:* connect the exploit to the theory. Answer
in your own words: (a) Why does editing **C0** change **P1** but *not* C0's own plaintext block in
a way that matters? (b) Why is `guest → admin` a *clean* flip but `user → admin` would **not**
work with a plain bit-flip? (c) What does AES-GCM compute over the ciphertext that makes the same
edit fail, and why can't the attacker recompute it without the key? *Deliverable:* three short
paragraphs, one per sub-question.

---

## 2B — Evidence & Integrity (required)

- **Identity proof:** your terminal/screenshot evidence for Tasks 1–4 must show your
  `whoami` / login email / student ID and a timestamp.
- **Personalized flag:** ____________________
  *Flags are unique per student (via `AES_KEY`/`FLAG_AES` env override — see README) —
  submitting another student's flag is a violation.*
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the bit-flip work** (name the token byte range you edited)?
  2. **Why does AES-GCM actually stop it** — and is switching to GCM enough on its own, or does
     the developer still have to *check the tag / not swallow the exception* (tie back to Q10)?

---

## 2C — 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

A teammate asked an AI assistant: *"Write me a Python helper that encrypts a session token so
clients can't read or change the role field."* The AI produced the snippet below. It runs, it
uses a real AES library, and it looks professional — but it has **at least one subtly serious
flaw** that is exactly this week's topic. Your job: find it.

> **AI's answer:**
> ```python
> import os, base64
> from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
> from cryptography.hazmat.primitives import padding
>
> KEY = bytes.fromhex(os.environ["TOKEN_KEY"])  # 64 hex chars -> 32 bytes, AES-256
>
> def make_token(role: str) -> str:
>     data = f"role={role}".encode()
>     iv = os.urandom(16)
>     padder = padding.PKCS7(128).padder()
>     data = padder.update(data) + padder.finalize()
>     enc = Cipher(algorithms.AES(KEY), modes.CBC(iv)).encryptor()
>     ct = enc.update(data) + enc.finalize()
>     return base64.b64encode(iv + ct).decode()   # clients get IV || ciphertext
>
> def read_role(token: str) -> str:
>     raw = base64.b64decode(token)
>     iv, ct = raw[:16], raw[16:]
>     dec = Cipher(algorithms.AES(KEY), modes.CBC(iv)).decryptor()
>     data = dec.update(ct) + dec.finalize()
>     unpadder = padding.PKCS7(128).unpadder()
>     data = unpadder.update(data) + unpadder.finalize()
>     return data.decode().split("role=")[1]   # trust the decrypted role
> ```
> "This uses AES-256 in CBC mode with a random IV per token and standard PKCS7 padding, so the
> ciphertext is confidential and the client cannot read the role. Because the data is encrypted
> with a key only the server knows, the client also cannot change the role — they'd have to break
> AES to produce a valid token."
>
> — end of AI answer —

1. **Find what's wrong or risky.** Quote the exact sentence(s) and/or line(s). (Hint: the AES
   call, the random-IV-per-token, and the PKCS7 padding are all **fine** — don't waste your
   critique there. The false claim is the *last sentence*: "the client also cannot change the
   role — they'd have to break AES." Explain, using this week's lab, why that is wrong. What can
   an attacker do to the ciphertext *without* breaking AES or knowing the key?)
2. **Produce the correct, verified version yourself.** Rewrite `make_token`/`read_role` to use
   **authenticated encryption** (AES-GCM via `cryptography`'s `AESGCM`, or CBC + a separate
   encrypt-then-HMAC), so that any tampering is *rejected*. In 2–3 sentences, explain why the
   AI's version would happily accept a bit-flipped `role=admin` token even though it "passes its
   own `read_role`," and how your version stops that. **You may verify your rewrite against the
   lab** (drop it into `vulnerable_app.py`'s scheme and re-run `exploit.py` — a correct AEAD
   rewrite should make the vuln side start *rejecting* the flip too).

> Disclose your AI use (if any, beyond this provided artifact) in the Student Information table.
> This task counts toward your Defense + Reflection score.

---

## 2D — 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** Explain to a teammate — a working developer who knows
what "encrypt" means but has never heard "malleability" or "CBC bit-flipping" — **why AES-CBC
*alone* lets an attacker change the message** even though they can't read the key. In 2–4
sentences: what can the attacker do to the token, and *why* does the "it's encrypted, so it's
safe" intuition fail here? Avoid jargon-dropping (don't just say "CBC is malleable" back at
them) — explain the *mechanism* in terms of "each block's decryption is XOR-ed with the previous
ciphertext block, and the attacker controls that previous block."

**B. Prompt Problem.** Write a **single prompt** that asks an AI to explain *why AES-CBC without
a MAC is vulnerable to bit-flipping while AES-GCM is not*. Run it, then critique the AI's answer:
- Does it correctly explain the CBC relation `P_i = D(C_i) XOR C_{i-1}` (i.e. *why* editing the
  previous ciphertext block flips predictable plaintext bytes)?
- Does it correctly say that GCM's **authentication tag** — not its confidentiality — is what
  rejects the tamper, and that GCM is an **AEAD**?
- Does it **hallucinate** anything? (Common errors to watch for: claiming CBC "encrypts each
  block independently" — that's **ECB**, not CBC; claiming a random IV alone prevents tampering;
  claiming AES-GCM is "just AES-CBC with a checksum"; or inventing a wrong NIST/RFC number.)

Submit the **final prompt + the AI's answer + your critique** (3–5 sentences covering the three
bullet points above).

---

## 2E — 🎤 Viva spot-check (instructor use — 3 questions)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "Show me on your printed token hex dump exactly which byte range you XOR-ed, and explain why
   editing **C0** (not C1) is what changed the *role* block — and what happened to the *comment*
   block as a side effect."
2. "The benign role is `guest` and the target is `admin`. Why does the flip work cleanly for
   those two, but you could **not** bit-flip `user` into `admin`? What would you need instead?"
3. "Point to the one conceptual change between `vulnerable_app.py` and `fixed_app.py`'s token
   scheme, and explain in one sentence why AES-GCM rejects the exact edit that AES-CBC accepted —
   what does GCM check that CBC doesn't?"

---

## Grading rubric (100)

| Criterion | Points |
|---|---|
| Part 1 — Conventional written questions (Q1–Q10) | 25 |
| Part 2A — Lab tasks 0–5 (evidence: token hex dump, computed XOR deltas, curl output) | 30 |
| Part 2B — Evidence & Integrity (flag capture + own-words explanation) | 10 |
| Part 2C — Audit the AI (flaw found + AEAD-corrected, verified rewrite) | 20 |
| Part 2D — Comprehension & Prompt (EiPE + Prompt Problem) | 15 |

*Viva spot-checks (Part 2E) are pass/fail gates on the Lab + Audit-the-AI scores, not separately
scored — an instructor who isn't convinced you did the work yourself may re-score those sections
down.*
