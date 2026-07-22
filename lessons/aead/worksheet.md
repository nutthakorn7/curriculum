# Worksheet 6 — Authenticated Encryption (AEAD): the CBC Padding Oracle (3 hrs)

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Topic:** Authenticated Encryption (AEAD) — new this year (capstone of the symmetric block:
> {{ ref('macs') }} MAC + {{ ref('aes-modes') }} AES "combined correctly").
> **Decryption game:** "Read the Secret Without the Key" — a CBC padding-oracle attack against
> unauthenticated AES-CBC, then the same attack defeated by AES-GCM (AEAD).

> **Ethics note:** Attack only the two local containers this lab spins up
> (`vulnerable_app.py` / `fixed_app.py`, ports 8098/8099). A padding oracle is a real,
> deployed-in-the-wild attack (POODLE, Lucky-13, dozens of CVEs). Running it against systems you
> don't own and aren't authorized to test is illegal. Keep your key, ciphertext, and flag inside
> this lab environment.

## Part 1 — Student Information
| Name | Student ID | Date | Group |
|---|---|---|---|

---

## Part 2 — Conventional Arm: Written Questions

Answer each in your own words (4–8 sentences, more where the question asks for a design or a
comparison). This is a normal written/essay task — **no AI-resilience layer applies to this
part; answer it yourself.** These eight questions are the conventional-arm assessment for {{ slot_label }}.

**Q1. What is AEAD?** What does "AEAD" stand for, and what **three** guarantees does an AEAD
cipher provide in a single primitive? For each guarantee, name the attack it stops.

**Q2. Safe composition.** Compare **Encrypt-then-MAC**, **MAC-then-Encrypt**, and
**Encrypt-and-MAC**. Which is the *provably safe* generic composition (gives authenticated
encryption for any secure cipher + any secure MAC), and *why* are the other two fragile? Tie your
answer to what the verifier gets to touch before the MAC is checked.

**Q3. Padding oracle.** What is a padding oracle? Explain concretely how distinguishing "bad
padding" from other outcomes lets an attacker **decrypt a ciphertext without the key**. Walk
through how forcing the padding to `0x01`, then `0x02 0x02`, … recovers one plaintext byte per
round.

**Q4. Why AES-GCM has no padding oracle.** Give the two independent reasons AES-GCM is immune to
the attack in Q3 — one about *what mode it is* (stream vs block, padding or no padding) and one
about *ordering* (when the authentication tag is checked relative to releasing plaintext).

**Q5. Associated data.** What is the "associated data" (the **AD** in AEAD)? Give a concrete
example of data you want to **authenticate but not encrypt**, and explain what breaks if that data
is left unauthenticated.

**Q6. CBC malleability (ties to {{ ref('aes-modes') }}).** Why is unauthenticated CBC **malleable** — i.e. why can
an attacker flip a chosen bit of plaintext block *P\_i* by flipping a bit of ciphertext block
*C\_{i-1}*? Show the CBC decryption relation `P_i = D(C_i) XOR C_{i-1}` and use it to explain the
bit-flip, and why a padding oracle is *malleability weaponized into full decryption*.

**Q7. Forgetting to check the tag.** A system uses AES-GCM but a developer, "for performance,"
uses the plaintext returned by the cipher *before* the tag verification result is checked (or
ignores an `InvalidTag` exception). What security property is lost, and what class of attack does
this re-enable? Name the property precisely.

**Q8. Choosing an AEAD.** One line each: when would you reach for **AES-GCM** vs
**ChaCha20-Poly1305** vs **AES-GCM-SIV**? Anchor each to a concrete deployment concern (hardware
support, nonce-misuse risk, constant-time software performance).

---

## Part 3 — AIR-Sec Arm: Hands-on Lab (180 min)

**Learning goals:** turn a single "bad padding" side channel into a full plaintext recovery
against unauthenticated CBC, then prove AES-GCM (AEAD) gives the attacker no signal — the
*practical* twin of Part 2's Q3/Q4.
**Prerequisites:** Docker; Python 3.12 (or the `requests` package) on the host to run
`exploit.py`.

**Environment setup**
```bash
cd {{ labpath }}
docker compose up -d        # vulnerable_app.py on :8098, fixed_app.py on :8099
curl localhost:8098/        # confirm it's up
curl localhost:8098/secret  # base64(IV||ct) of the secret that contains your flag
```

**Task 0 — Onboarding (10 min).** *Goal:* see the oracle. *Steps:* read `vulnerable_app.py`'s
`/decrypt` handler and the `pkcs7_valid` function; identify the exact line where a `200` and a
`403` diverge, and confirm it is *only* the PKCS#7 padding check that distinguishes them.
*Deliverable:* quote that line and state, in one sentence, why "the endpoint never returns the
plaintext" does **not** make it safe.

**Task 1 — Grab the ciphertext (5 min).** *Goal:* capture the target. *Steps:*
`curl localhost:8098/secret`; base64-decode it and note its length. *Deliverable:* the ciphertext
length in bytes, and how many 16-byte blocks that is *after* subtracting the IV block.

**Task 2 — Understand one oracle query (30 min).** *Goal:* understand the primitive, not just run
it. *Steps:* read `exploit.py`'s `recover_intermediate`. On paper, for the **last** ciphertext
block *C\_t*: you submit `forged_prev || C_t` as a 2-block `IV||ct`. The server computes
`P = D(C_t) XOR forged_prev` and tells you (200/403) whether `P` ends in valid PKCS#7 padding.
Explain: (a) why guessing `forged_prev[15]` until you get `200` almost always means the last byte
of `P` is `0x01`; (b) what `D(C_t)[15]` then equals, in terms of your winning guess and `0x01`;
(c) the false-positive case where `P` ends `…0x02 0x02` instead, and how the code's neighbour-byte
re-query disambiguates it. *Deliverable:* your three short answers + the formula
`D(C_t)[15] = winning_guess XOR 0x01`.

**Task 3 — Recover the plaintext & read the flag (20 min).** *Goal:* full recovery, no key.
*Steps:* `python exploit.py`. Watch it recover the plaintext block-by-block and print the flag.
Then manually reproduce **one** oracle query with `curl` (POST a `forged_prev || C_t` blob to
`/decrypt`) and confirm you get the `200`/`403` the script expected, to convince yourself nothing
is hidden. *Deliverable:* the recovered plaintext, your flag, and your one manual `curl` query +
its status code.

**Task 4 — Confirm AES-GCM rejects the same attack (15 min).** *Goal:* prove the fix, don't just
claim it. *Steps:* `exploit.py` re-runs the identical routine against `:8099`. Confirm it printed
"no usable padding signal … nothing recovered". Read `fixed_app.py`'s `/decrypt`: identify (a) the
line that makes *every* failure return the **same** `403`, and (b) where the tag is verified
relative to any use of the plaintext. *Deliverable:* the "nothing recovered" evidence + the two
lines you identified, with a one-sentence why-each-matters.

**Task 5 — Explain why, precisely (20 min).** *Goal:* connect exploit to theory. *Steps:* answer
in your own words: (a) In CBC, why does the attacker's control of `forged_prev` give a *per-byte*
oracle on `D(C_t)` even though they don't know the key? (b) Why does AES-GCM's **stream** structure
mean there is no "valid vs invalid padding" question to ask at all? (c) Even if GCM *did* pad, why
would checking the **tag first** and returning a **uniform** error still kill the oracle?
*Deliverable:* 3 short paragraphs, one per sub-question.

---

## Evidence & Integrity (required)

- **Identity proof:** your terminal/screenshot evidence for Tasks 1–4 must show your
  `whoami` / login email / student ID and a timestamp.
- **Personalized flag:** ____________________
  *Flags are unique per student (via the `FLAG_AEAD` env override — see README) — submitting
  another student's flag is a violation.*
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the padding-oracle recovery work** against `:8098`?
  2. **Why does AES-GCM actually stop it** — and name one *separate* mistake (not fixed by simply
     "switching to GCM") that could still reintroduce a decryption oracle (hint: think about
     Q7, and about nonce reuse — which {{ ref('hybrid-encryption') }} audits).

---

## 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

Below is an AI assistant's "secure decrypt-and-validate" helper for an AES-CBC service. It looks
careful — it validates padding, it validates the message format, it logs errors — but it
**reintroduces a padding oracle** through its error handling, plus one deeper design flaw. Your
job: find them.

> **AI's answer — "a safe CBC decrypt endpoint":**
>
> ```python
> @app.post("/decrypt")
> def decrypt():
>     blob = base64.b64decode(request.json["ciphertext"])
>     iv, ct = blob[:16], blob[16:]
>     plaintext = aes_cbc_decrypt(key, iv, ct)   # raw, padding not yet removed
>     try:
>         unpadded = pkcs7_unpad(plaintext)      # raises ValueError on bad padding
>     except ValueError:
>         return {"error": "invalid padding"}, 400
>     if not unpadded.startswith(b"MSG:"):
>         return {"error": "malformed message"}, 422
>     return {"plaintext": unpadded.decode()}, 200
> ```
>
> "This endpoint is safe: it decrypts the ciphertext, strips PKCS#7 padding, and rejects anything
> whose padding is invalid with a clear `400` error so the client knows to resend. It further
> validates that the message has the expected `MSG:` prefix, returning a distinct `422` if not, so
> callers get precise diagnostics. Because we always validate the padding before using the
> plaintext, tampered ciphertexts are caught early and cannot corrupt downstream logic."
>
> — end of AI answer —

1. **Find what's wrong or risky in it.** Quote the exact line(s). (Hint: the crypto *call* is
   fine and PKCS#7 unpadding *is* the right first step — don't waste your critique there. Look at
   what an attacker learns from the **three different responses** this endpoint can return
   (`400` vs `422` vs `200`), and separately at what the endpoint does even in the "malformed"
   case that a padding oracle needs.)
2. **Explain the attack it enables.** In 2–3 sentences: which two responses form the padding
   oracle, and why does adding the `422` "malformed message" branch make the leak *worse*, not
   better?
3. **Produce the corrected version yourself.** Rewrite the endpoint so it is *not* a padding
   oracle. State the single most important change (hint: the real fix is not "hide the error
   codes" — it is to make the ciphertext *unforgeable in the first place*; say what primitive you
   would switch to and why that removes the question the oracle asks).

> Disclose your AI use (if any, beyond this provided artifact) in the Part 1 table. This task
> counts toward your Defense + Reflection score.

---

## 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** Explain a **padding oracle** to a teammate who knows what
AES is (a block cipher that turns 16 bytes + a key into 16 scrambled bytes) but has **never heard
of CBC chaining or PKCS#7 padding**. In 3–5 sentences: what is padding and why does encryption
need it; what single yes/no question is the server accidentally answering for the attacker; and
why does answering that question thousands of times let the attacker read the message *without the
key*? Avoid jargon-dropping — don't just say "CBC" and "Merkle" at them; explain the *mechanism*
in terms of "the attacker changes one byte of the input and watches whether the server says the
padding is OK."

**B. Prompt Problem.** Write a **single prompt** that asks an AI to *implement a secure
`decrypt()` endpoint for an encrypted message service, resistant to padding-oracle attacks.* Run
it, then critique the AI's answer against these checks:
- Does it reach for an **AEAD** cipher (AES-GCM / ChaCha20-Poly1305), or does it hand you raw
  CBC + a hand-rolled padding check (the trap)?
- If it stays with CBC, does it use **encrypt-then-MAC** and verify the MAC (constant-time)
  *before* touching the plaintext — or does it "fix" the oracle by merely returning the same HTTP
  code while still branching internally (a **timing** oracle remains)?
- Does it hallucinate a false reassurance — e.g. "returning a generic 500 error makes CBC safe,"
  or "PKCS#7 padding is itself authenticated," or a wrong claim that AES-GCM "still needs padding"?

Submit the **final prompt + the AI's answer + your critique** (3–5 sentences covering the three
bullets above). A strong prompt names the threat model ("must resist an attacker who can submit
chosen ciphertexts and observe responses") so the AI can't wriggle out with a toy example.

---

## 🎤 Viva spot-check (instructor use — 3 questions)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "In your attack, point to the byte in `forged_prev` you were varying to recover the **last**
   byte of a block, and tell me: when the server first said `200`, what were the *two* possible
   plaintext-padding situations, and how did your exploit tell them apart?"
2. "The `/decrypt` on `:8098` never returns the plaintext — only `200` or `403`. In one sentence,
   why is that *still* enough to fully decrypt the secret, and what would you have to remove from
   the endpoint to close the hole *without* changing the cipher?"
3. "Switching to AES-GCM killed the oracle. Name one *different* bug that would put a decryption
   oracle right back even though you're now 'using AEAD' — and say whether your {{ slot_label }} fixed app
   has it."

---

## Grading rubric (100)

| Criterion | Points |
|---|---|
| Part 2 — Conventional written questions (Q1–Q8) | 25 |
| Part 3 — Lab tasks 0–5 (evidence: block count, one manual oracle `curl`, GCM "no signal") | 30 |
| Evidence & Integrity (flag capture + own-words explanation) | 10 |
| Audit the AI (oracle-via-error-codes flaw found + corrected AEAD design) | 20 |
| Comprehension & Prompt (EiPE + Prompt Problem) | 15 |

*Viva spot-checks are pass/fail gates on the Lab + Audit-the-AI scores, not separately scored —
an instructor who isn't convinced you did the work yourself may re-score those sections down.*
