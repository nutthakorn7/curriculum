# Worksheet 3 — MACs: Hash-Only Cookies and Length-Extension (100-minute class + preparation/extension)

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Topic source:** `Week3_MACs Questions.docx` (KOSEN68) — 10 essay questions, ported below:
> Q1/Q4/Q5/Q6 as this week's written task (Part 2), Q2/Q3/Q7/Q8/Q9/Q10 as an appendix /
> future exam-bank material (Part 5).
> **Signature game:** "Forge the Admin Cookie" (SHA-256 length-extension against a secret-prefix
> cookie MAC)

> **Ethics note:** Attack only the two local containers this lab spins up
> (`vulnerable_app.py` / `fixed_app.py`, ports 8092/8093). Forging authentication tokens against
> systems you don't own and aren't authorized to test is illegal. Keep your `MAC_SECRET` and
> flag inside this lab environment.

## How to use this worksheet — 100-minute class, two versions

Everyone completes the **same common activity (60 points)**. Complete only the
**Conventional written assessment (40)** or the **AIR-Sec assessment (40)** assigned
by the instructor. AIR-Sec's 40 points are Audit the AI 20, EiPE 10 and Prompt Problem 10.
Each version totals **100**, and neither version requires the other format for marks.

| Common criterion | Points | This week's evidence |
|---|---:|---|
| Core activity / analysis | 20 | Capture a guest cookie, calculate glue padding and demonstrate the intended SHA-256 length-extension forgery. |
| Control comparison and limitations | 20 | Run the same technique against HMAC; distinguish a failed forgery from unrelated timing/replay limitations. |
| Evidence and causal reasoning | 20 | Record original/forged data and tags, the padding calculation, manual replay and fixed rejection, with a causal explanation. |

**Before class:** complete the stated reading and any environment setup; software
installation and first image downloads are preparation, not extra contact minutes.
**In class (100 minutes):** 10 quiz/review + 10 brief + 60 shared practice/analysis +
15 debrief + 5 evidence capture. In Week 1 the opening block is orientation/review,
not a quiz on material not yet taught. The detailed tasks below are a checklist, not
additional timed class blocks: work through the core observations in the guided practice,
draft the explanation in the debrief, then finish detailed calculations/write-up and the
assigned 40-point format before the published deadline. Keep every original question;
unassigned-format questions and the labelled appendix are study extensions.

## Part 1 — Student Information
| Name | Student ID | Date | Group |
|---|---|---|---|

---

## Part 2 — Conventional assessment (assigned version, 40 points): Written Questions (ported from KOSEN68, Q1/Q4/Q5/Q6)

Answer each in your own words (4–8 sentences, more where the question asks for a design).
This is a normal written/essay task — no AI-resilience layer applies to this part; answer it
yourself.

**Q1. Weak Stateless Cookie Design (Hash-only Cookie).** A web server stores:
`cookie = username || SHA-3(username)`. Analyze why this design fails to provide authenticity
and integrity. If an attacker modifies `username=bob` to `username=admin`, explain why the
server cannot detect tampering.

**Q4. Timing Attack on Tag Verification.** A server verifies a MAC with:
```python
if received_tag == computed_tag:
    accept()
else:
    reject()
```
Explain why this is vulnerable to timing attacks, how an attacker recovers the tag byte-by-byte
via response times, and why constant-time comparison is required.

**Q5. SHA-256 Length-Extension Attack.** `MAC = SHA-256(key || message)`,
`message = "user=bob"`. An attacker wants to append `&admin=true`. Explain how the attacker
computes a valid new MAC without knowing the key, why SHA-256's Merkle-Damgard design enables
this, and why HMAC is not vulnerable.

**Q6. Designing a Secure Cookie Using MAC.** Design a secure cookie system preventing tampering
and replay. Your answer must state: the fields stored, how the MAC is computed, how
verification works, a replay-prevention mechanism, and why this is safer than hashing
`key || message`.

---

## Part 3 — Shared common practice (both versions, 60 points)

**Learning goals:** exploit a secret-prefix hash MAC via length-extension, then verify HMAC
closes the gap — the *practical* twin of Part 2's Q5.
**Prerequisites:** Docker; Python 3 with the `requests` package on the host to run
`exploit.py`.

**Environment setup**
```bash
cd {{ labpath }}
docker compose up -d        # vulnerable_app.py on :8092, fixed_app.py on :8093
curl localhost:8092/        # confirm it's up
```

**Task 0 — Onboarding.** *Goal:* see the vulnerable construction. *Steps:* read
`vulnerable_app.py`'s `make_cookie`/`admin` functions; identify exactly which line computes the
signature and confirm it is `SHA256(MAC_SECRET + data)`, not HMAC. *Deliverable:* quote the
line and state which of Q1/Q5's failure mode it matches.

**Task 1 — Capture a legitimate cookie.** *Goal:* get a real `(data, sig)` pair.
*Steps:* `curl -i "localhost:8092/login?user=guest"`; record the `data` and `sig` cookies.
*Deliverable:* the two cookie values + the decoded (from-hex) plaintext of `data`.

**Task 2 — Run the length-extension forgery.** *Goal:* understand *and* reproduce the
attack, not just run a script. *Steps:* read `exploit.py`'s `sha256_padding` and
`length_extend` functions; on paper (or in your write-up), compute the glue-padding length for
`len(MAC_SECRET) + len(data) = 16 + 22 = 38` bytes by hand using the SHA-256 padding rule
(append `0x80`, then zero bytes until length ≡ 56 mod 64, then an 8-byte big-endian bit-length).
Then run `python exploit.py` and confirm your hand-computed padding length matches the glue
bytes it printed. *Deliverable:* your hand computation + the script's forged `data`/`sig`.

**Task 3 — Cash in the flag.** *Goal:* confirm the forged cookie is accepted.
*Steps:* `exploit.py` already does this (`GET /admin` on `:8092` with the forged cookie); note
the flag it printed. Also manually reproduce it with `curl` (`--cookie "data=...;sig=..."`) to
convince yourself the script isn't doing anything hidden. *Deliverable:* the flag + your `curl`
command and its output.

**Task 4 — Confirm HMAC rejects the same trick.** *Goal:* prove the fix works, not
just claim it. *Steps:* `exploit.py` repeats the identical forgery technique against `:8093`
(`fixed_app.py`, HMAC); confirm it printed `403`/rejected. Read `fixed_app.py`'s `make_cookie`
and identify the one-line change from `vulnerable_app.py`. *Deliverable:* the rejection
evidence + the diff (in words) between the two `make_cookie` functions.

**Task 5 — Explain why, precisely.** *Goal:* connect the exploit to the theory.
*Steps:* answer in your own words: (a) What internal SHA-256 state does `sig` actually expose
to the attacker? (b) Why does resuming compression from that state let the attacker compute
`H(secret || data || glue || extra)` without `secret`? (c) Although the final outer SHA-256 digest can itself be resumed, why does that extension
not produce a valid HMAC for an extended message? Distinguish the exposed outer digest from
the hidden inner digest and HMAC's fixed outer-input format. *Deliverable:*
3 short paragraphs, one per sub-question.

---

## Evidence & Integrity (required)

- **Evidence attribution (the same for both versions):** put your name/student ID and
  date on the worksheet, and capture your own commands and results. Make clear which run
  each observation came from. A terminal timestamp or identity stamp is optional context,
  not an extra scored personal artifact. If evidence is unclear, the instructor may request
  clarification within the common evidence/reasoning criterion.
- **Runtime flag (where this lab returns one):** record the value from your own run. Use a
  personalised configuration only if the instructor supplies it; otherwise the shared demo
  flag is acceptable with your own evidence and reasoning. No automatic roster/flag validation
  is assumed. Do not submit a classmate's capture as your own.
- Optional context stamp: `printf '%s | %s | ' "$(whoami)" '<YOUR-STUDENT-ID>'; date '+%F %T %Z'`.
  You may include this with a terminal/browser capture if useful. A separate terminal or
  whole-screen identity capture is not required; legible own commands/results and the
  worksheet name/student ID are sufficient. All common evidence is within the common 60.
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the forgery work**?
  2. **Why does the HMAC fix actually stop it** — and what could still break it (e.g. is the
     `!=` comparison in `fixed_app.py`'s `/admin` still a timing-attack risk)?

---

## 🤖 Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's
answer.

Below is an AI assistant's answer to **Q6** (design a secure cookie using a MAC). It looks
professional and uses correct terminology, but it has **at least one subtly serious flaw**.
Your job: find it.

> **AI's answer to Q6:**
>
> "Design: the cookie stores three fields, joined with `|`: `user_id`, `issued_at` (Unix
> timestamp), and `role`. The server computes
> `tag = HMAC-SHA256(server_key, f"{user_id}|{issued_at}|{role}")` and sends the client
> `cookie = f"{user_id}|{issued_at}|{role}|{tag}"`.
>
> Verification: on each request, the server splits the cookie on `|`, recomputes
> `HMAC-SHA256(server_key, f"{user_id}|{issued_at}|{role}")`, and compares it to the received
> `tag` using Python's `==` operator. If they match, the request is accepted as authentic and
> the timestamp is logged for audit purposes.
>
> Replay prevention: because `issued_at` is embedded in the MAC'd data, any attempt to change
> it invalidates the tag, so an attacker cannot forge a *new* timestamp. This closes the replay
> window described in Q3, since old cookies are cryptographically bound to their original
> issue time.
>
> Why this is safer than hashing `key || message`: HMAC's nested construction means the
> internal hash state is never directly exposed to the attacker the way a naive
> `SHA256(key || message)` construction is, so length-extension does not apply. Additionally,
> since `issued_at` is part of the signed data, the server can always tell precisely when a
> cookie was issued."
>
> — end of AI answer —

1. **Find what's wrong or risky in it.** Quote the exact sentence(s). (Hint: HMAC does resist message-extension forgery. Distinguish that fact from claiming
   that the final outer SHA-256 digest cannot itself be extended. The intended design flaws
   concern what "replay prevention" actually *guarantees* versus what the
   server *does* with `issued_at`, and separately at the comparison operator used in
   verification.)
2. **Produce the correct, verified version yourself.** Rewrite the two flawed parts of the
   design (not the whole answer) and explain in 2–3 sentences why the AI's version was
   insufficient even though the cookie *would pass its own described verification step*.

> Disclose your AI use (if any, beyond this provided artifact) in the Part 1 table. This task
> counts toward the **Audit the AI** row of the grading rubric.

---

## 🧠 Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE).** Explain SHA-256 length-extension to a junior developer
who has never heard the term "Merkle-Damgard" and does not have a cryptography background. In
2–4 sentences: what can the attacker do, and *why* does hashing a secret and a message together
(with the secret first) not protect the message the way the developer probably assumed it
would? Avoid restating jargon (don't just say "Merkle-Damgard" back at them) — explain the
*mechanism* in terms of "the hash function processes data in chunks and remembers where it left
off."

**B. Prompt Problem.** Write a **single prompt** that asks an AI to explain *why HMAC resists
length-extension attacks while a bare `SHA256(key||message)` does not*. Run it, then critique
the AI's answer:
- Does it correctly distinguish the *inner* hash from the *outer* hash in HMAC's construction?
- Does it distinguish extending the *outer SHA-256 hash* (possible from its final digest)
  from forging HMAC (not achieved by that extension)? The extended outer input would be
  `key⊕opad || inner_digest || glue || extra`, while a valid HMAC outer input contains only
  the key-derived prefix and one fixed-size inner digest. The inner digest needed to extend
  the message and a new valid outer tag are not exposed by the HMAC tag.
- Does it hallucinate anything (a wrong RFC number, a wrong claim about SHA-3/Keccak also being
  vulnerable to the same attack — SHA-3's sponge construction is *not* vulnerable to classic
  length-extension, unlike SHA-256)?

Submit the **final prompt + the AI's answer + your critique** (3–5 sentences covering the three
bullet points above).

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "Your forged `data` field is longer than the original — show me on your printed hex dump
   exactly which bytes are the SHA-256 glue padding, and explain why the byte right after
   `admin=false` is always `0x80`."
2. "If I doubled `MAC_SECRET`'s length but didn't tell you, what in your exploit would you have
   to change, and what would happen if you got that number wrong?"
3. "Point to the one line that differs between `vulnerable_app.py`'s and `fixed_app.py`'s
   `make_cookie` function, and explain in one sentence why that line alone defeats
   length-extension."

---

## Part 5 — Appendix / Future Exam-Bank Material (KOSEN68 Q2, Q3, Q7–Q10)

Not assigned this week; kept here for a future exam item bank per the course's exam-bank
convention (see `course-plan-19weeks.md`).

**Q2. Short Authentication Tag in IoT (64-bit MAC).** Using the birthday bound, estimate how
many MAC outputs an attacker needs to find a collision; evaluate whether a 64-bit MAC is secure
against forgery; explain the risks of a short tag in critical infrastructure (e.g. grid
controllers).

**Q3. Replay Attack in a MAC-Only System.** `tag = MAC(k, message)`, no counter/timestamp/nonce.
An attacker replays an intercepted "Transfer 1000 THB" message+tag later. Explain why MACs
alone do not prevent replay attacks and describe a secure defense.

**Q7. Choosing Between HMAC and KMAC** for: a legacy SHA-2 system; a system needing inherent
length-extension immunity; variable-length MAC output; constrained IoT devices.

**Q8. Key Rotation Strategy.** Analyze rotating every 1 hour / every 1000 messages / near
counter overflow (2^64) / never — impact on security, performance, complexity.

**Q9. Designing a Secure Messaging Protocol Using MAC (A→B).** Cover integrity, authenticity,
replay protection, multi-device support, offline queue handling — show message structure +
verification flow.

**Q10. Using MACs for Hash Table Integrity.** How a MAC alongside stored values protects
against tampering; whether hash collisions can bypass MAC checks; integrity vs. structural
security.

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| Common core activity / analysis | 20 | 20 |
| Common control comparison and limitations | 20 | 20 |
| Common evidence and causal reasoning | 20 | 20 |
| Conventional written questions | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

**Deadline and late work:** hand in by 23:59 Thai time (ICT) on the Sunday before the next week's
class (KOSEN rule); the exact date is on `learn.zcr.ai/submit`.
Late work loses 10% of this worksheet's score for each day late (a part day counts as a day), down to 0.

Submit the common work plus **one** assigned assessment format; do not add the two
format columns or complete both formats for extra marks. The original questions remain
available for study. A viva is a formative/authenticity check within the relevant criteria,
with feedback or a request to clarify/reproduce evidence; it has no separate points and
no automatic-zero rule. Grade the demonstrated work against the published criteria.
