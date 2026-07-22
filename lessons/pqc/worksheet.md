# Worksheet 15 — Post-Quantum Cryptography: Lamport One-Time Signatures (3 hrs)

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Topic:** Post-quantum cryptography — the quantum threat, the four PQC families, and
> hash-based one-time signatures. (Written fresh for this course; no prior question bank.)
> **Signature game:** "Forge the Admin Signature" (Lamport one-time-key **reuse** → full
> private-key recovery → signature forgery).

> **Ethics note:** Attack only the two local containers this lab spins up
> (`vulnerable_app.py` / `fixed_app.py`, ports 8100/8101). Forging signatures or authentication
> tokens against systems you don't own and aren't authorized to test is illegal. Keep your
> `FLAG_PQC` inside this lab environment.

## Part 1 — Student Information
| Name | Student ID | Date | Group | AI tools used (if any) |
|---|---|---|---|---|

---

## Part 2 — Conventional Arm: Written Questions

Answer each in your own words (4–8 sentences, more where the question asks for a design or a
comparison). **This is a normal written/essay task — no AI-resilience layer applies to this
part; answer it yourself.**

**Q1. The quantum threat to public-key crypto.** Why does a large-scale quantum computer
threaten **RSA and ECC specifically**? Name the algorithm responsible and state exactly what
mathematical problem it solves that makes those two schemes breakable.

**Q2. Grover vs. Shor.** Does **Grover's algorithm** break symmetric crypto (AES) the same way
**Shor's** breaks RSA? Quantify Grover's speedup, explain why it does *not* amount to a break,
and state the practical mitigation.

**Q3. Harvest now, decrypt later.** What is the "**harvest now, decrypt later**" threat, and why
does it make PQC migration urgent **today**, before any large quantum computer exists? Give one
concrete category of data for which this threat is real right now.

**Q4. The four PQC families.** Name the **four families** of post-quantum cryptography (lattice,
hash-based, code-based, multivariate) and give **one example scheme** for each. Note which
family this week's lab (Lamport) belongs to.

**Q5. Hash-based signatures.** What is a **hash-based signature** (Lamport / SPHINCS+), on what
single assumption does its security rest, and what is its **main practical limitation** compared
to RSA/ECDSA signatures? (Consider signature size and/or the one-time-key constraint.)

**Q6. Why reusing a Lamport key is catastrophic.** Explain precisely why reusing a Lamport
**one-time key** across **two** messages is catastrophic. Walk through what a signature reveals
about the private key, and why signing a message *and its bitwise complement* hands an attacker
the entire private key. (This is the exact vulnerability you will exploit in Part 3.)

**Q7. ML-KEM and ML-DSA.** NIST standardized **ML-KEM** (from Kyber) and **ML-DSA** (from
Dilithium). What is **each one for**? Be specific about the difference between a **KEM** (key
encapsulation) and a **signature** scheme, and name a protocol (e.g. TLS) where each would slot
in.

**Q8. Crypto-agility.** What is "**crypto-agility**," and why is it — rather than any single
algorithm choice — the real engineering lesson of the PQC transition? Give two concrete design
practices that make a system crypto-agile.

---

## Part 3 — AIR-Sec Arm: Hands-on Lab (180 min)

**Learning goals:** exploit a **reused Lamport one-time key** to recover a full private key and
forge a signature, then verify that **one-time enforcement** — an *operational* control, not a
new algorithm — closes the gap. The *practical* twin of Part 2's Q5/Q6.
**Prerequisites:** Docker; Python 3.12 (or the `requests` package) on the host to run
`exploit.py`.

**Environment setup**
```bash
cd {{ labpath }}
docker compose up -d        # vulnerable_app.py on :8100, fixed_app.py on :8101
curl localhost:8100/        # confirm it's up
curl localhost:8100/pubkey  # inspect the public key + admin message (0xA5A5C3C3)
```

**Task 0 — Onboarding (15 min).** *Goal:* see the Lamport construction and the bug. *Steps:*
read `vulnerable_app.py`'s `sign`, `verify`, and `sign_endpoint`. Identify (a) the line that
generates the private key as *two preimages per bit*, (b) the line that reuses the one keypair
on every call, and (c) the shared baseline line that refuses to sign the admin message directly.
*Deliverable:* quote lines (a)–(c) and state, in one sentence, why (c) is necessary for the lab
to have any challenge at all.

**Task 1 — Understand what one signature reveals (20 min).** *Goal:* build the intuition before
running anything. *Steps:* `POST /sign {"message_hex":"00000000"}` against `:8100`; you get 32
preimages. `GET /pubkey`; for bit position 0, verify by hand (in Python or by pasting into a
`sha256`) that `SHA256(sig[0]) == pk[0][0]` (the *bit-value-0* entry, because message bit 0 is
`0`), and confirm `SHA256(sig[0]) != pk[0][1]` — i.e. this one signature reveals the `0`-preimage
for that position but **not** the `1`-preimage. *Deliverable:* the two hash comparisons for bit
0, and one sentence: "with only this signature, which half of the key for bit 0 is still
secret?"

**Task 2 — Recover the whole key with two signatures (30 min).** *Goal:* the core attack.
*Steps:* `POST /sign {"message_hex":"ffffffff"}` (the complement). Now for **every** bit you
have both the `0`-preimage (from the `00000000` signature) and the `1`-preimage (from the
`ffffffff` signature). Read `exploit.py`'s `recover_and_forge`: note the self-check that every
recovered preimage hashes to the published public key. *Deliverable:* for **one** bit position
of your choice, print both recovered preimages and show both `SHA256(...)` values matching
`pk[i][0]` and `pk[i][1]`.

**Task 3 — Forge and cash in the flag (20 min).** *Goal:* forge a signature on the admin message
you were **refused** permission to sign. *Steps:* run `python exploit.py`; note the flag. Then
reproduce the forgery step manually: the admin message is `0xA5A5C3C3` — for each bit, select
the recovered preimage matching that bit's value, and `POST /admin {sig}` with `curl` to convince
yourself the script isn't hiding anything. *Deliverable:* the flag + your `curl` command and its
output. Explain in one sentence why the server accepts a signature on a message it *refused to
sign for you*.

**Task 4 — Confirm one-time enforcement defeats the attack (20 min).** *Goal:* prove the fix
works, not just claim it. *Steps:* run the same attack against `:8101` (`exploit.py` already
does this). Observe that the **second** `/sign` (the complement) returns `403` "one-time key
already used" — in fact *any* second `/sign` is refused, because the key signs exactly once. Read
`fixed_app.py`'s `sign_endpoint` and identify the **one block** that differs from
`vulnerable_app.py`. *Deliverable:* the rejection evidence + the diff (in words) between the two
`sign_endpoint` functions, and one sentence on why the attacker, given only ONE signature, cannot
forge the admin signature.

**Task 5 — Explain why, precisely (25 min).** *Goal:* connect exploit to theory. *Steps:* answer
in your own words: (a) Why does a *single* Lamport signature leak only half the private key,
while a message and its complement leak all of it? (b) The fix adds no new cryptography — it just
refuses the second signature. What does that tell you about the difference between a *scheme
being secure* and a *scheme being used securely*? (c) SPHINCS+ is "stateless" yet built from
one-time signatures — how can it possibly avoid the reuse trap without tracking which keys it has
used? (Hint: a huge tree + pseudorandom key selection so that reuse is *cryptographically
negligible*.) *Deliverable:* 3 short paragraphs, one per sub-question.

---

## Evidence & Integrity (required)

- **Identity proof:** your terminal/screenshot evidence for Tasks 1–4 must show your
  `whoami` / login email / student ID and a timestamp.
- **Personalized flag:** ____________________
  *Flags are unique per student (via `FLAG_PQC` env override — see README) — submitting another
  student's flag is a violation.*
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the forgery work** on `:8100`?
  2. **Why does one-time enforcement actually stop it** on `:8101`? The fixed app refuses *every*
     second `/sign` — even for the same message. Why is "one signature, period" the right rule,
     and why can a client that needs to retry a dropped response NOT simply re-request a signature
     from the same key (what must it do instead)?

---

## 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's code.

A teammate asked an AI assistant to "write a helper that signs each outgoing message with our
Lamport key." The AI produced the snippet below. It runs, it type-checks, and it produces
signatures that verify. It also contains a **catastrophic, subtly-hidden flaw** of exactly the
kind this week is about.

> **AI's answer — `lamport_signer.py`:**
> ```python
> import hashlib, os
>
> N = 256
>
> class LamportSigner:
>     """Signs messages with a Lamport one-time signature. Reuse the instance for all your
>     outgoing messages so you only pay key-generation cost once."""
>     def __init__(self):
>         # Generate the keypair ONCE at startup, then reuse it for the lifetime of the process.
>         self.sk = [(os.urandom(32), os.urandom(32)) for _ in range(N)]
>         self.pk = [(self._h(a), self._h(b)) for (a, b) in self.sk]
>
>     @staticmethod
>     def _h(x): return hashlib.sha256(x).digest()
>
>     def _bits(self, msg: bytes):
>         digest = hashlib.sha256(msg).digest()   # hash the message to 256 bits, then sign
>         return [(digest[i // 8] >> (i % 8)) & 1 for i in range(N)]
>
>     def sign(self, msg: bytes):
>         bits = self._bits(msg)
>         return [self.sk[i][bits[i]] for i in range(N)]   # reveal one preimage per bit
>
> # Usage: one signer, many messages.
> signer = LamportSigner()
> for m in outgoing_messages:          # <-- signs EVERY message with the SAME key
>     send(m, signer.sign(m))
> ```
> — end of AI answer —

1. **Find the catastrophic flaw.** Quote the exact line(s) and name the vulnerability. Explain,
   in terms of *preimages per bit*, what an attacker who collects a handful of these signatures
   can eventually do — and why the docstring's advice ("reuse the instance … so you only pay
   key-generation cost once") is precisely backwards for this primitive.
2. **Note a mitigating detail — and why it does NOT save the design.** Unlike the lab, this
   snippet *hashes the message before signing* (`self._bits` hashes `msg`). Does hashing-first
   prevent the `M` / `~M` complement trick? Explain what it *does* change (the attacker can no
   longer freely choose which key bits to reveal by choosing the message) and what it does
   **not** change (enough *distinct* messages still eventually reveal both preimages for enough
   positions to forge — hashing controls *which* bits leak, not *whether* reuse leaks). Roughly
   how many signatures before forging an arbitrary target becomes feasible?
3. **Produce the corrected version yourself.** Rewrite the design so it is safe. State clearly
   which control you added (one-time enforcement, or a stateful/stateless many-time scheme like
   XMSS/SPHINCS+) and why a `raise` on the second `sign()` call is the *minimum* correct fix.

> Disclose your AI use (if any, beyond this provided artifact) in the Part 1 table. This task
> counts toward your Defense + Reflection score.

---

## 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** Explain to a junior developer — who knows what "hashing"
is but has never heard "one-time signature" — **why a Lamport key must never sign two different
messages.** In 2–4 sentences: describe the private key as "two secret tokens per bit, and a
signature hands over one token per bit," and explain why signing a second, different message
hands over enough *extra* tokens that a stranger could assemble a signature for a message you
never approved. Avoid jargon ("Merkle tree", "preimage resistance") — explain the *mechanism*.

**B. Prompt Problem.** Write a **single prompt** that asks an AI to explain *why post-quantum
migration is urgent even though large quantum computers don't exist yet*. Run it, then critique
the AI's answer:
- Does it correctly center **"harvest now, decrypt later"** (adversaries recording ciphertext
  today to decrypt once quantum computers arrive) rather than just "quantum computers are
  coming"?
- Does it correctly distinguish **Shor** (breaks RSA/ECC — a real break) from **Grover** (only
  square-roots symmetric/hash security — mitigated by longer keys), instead of implying quantum
  "breaks all crypto"?
- Does it **hallucinate** anything — e.g. a wrong NIST FIPS number (ML-KEM is **FIPS 203**,
  ML-DSA is **FIPS 204**, SLH-DSA/SPHINCS+ is **FIPS 205**), a claim that AES-256 is "broken" by
  quantum, or that any deployed system is already using a quantum computer to break crypto?

Submit the **final prompt + the AI's answer + your critique** (3–5 sentences covering the three
bullet points above).

---

## 🎤 Viva spot-check (instructor use — 3 questions)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "Show me, for one bit position on your printed output, the **two** preimages you recovered and
   the **two** public-key hashes they match. Then tell me: if you had signed only `0x00000000`
   and never its complement, which of those two preimages would you be *missing*, and could you
   still forge the admin signature?"
2. "The admin message is `0xA5A5C3C3` and the server **refused** to sign it when you asked
   directly. Explain how your forged signature on that exact message is nonetheless accepted —
   what did the server never do, and what did you do instead?"
3. "Point to the one block that differs between `vulnerable_app.py`'s and `fixed_app.py`'s
   `sign_endpoint`, and explain in one sentence why that block — which adds *no new
   cryptography* — is what defeats the whole attack. Then: the fixed app refuses *every* second
   `/sign`, even for the same message — why is 'one signature, period' the correct rule rather
   than 'one distinct message'?"

---

## Grading rubric (100)

| Criterion | Points |
|---|---|
| Part 2 — Conventional written questions (Q1–Q8) | 25 |
| Part 3 — Lab tasks 0–5 (evidence: hash comparisons, recovered preimages, curl output) | 30 |
| Evidence & Integrity (flag capture + own-words explanation) | 10 |
| Audit the AI (catastrophic flaw found + hashing-first nuance + corrected design) | 20 |
| Comprehension & Prompt (EiPE + Prompt Problem) | 15 |

*Viva spot-checks are pass/fail gates on the Lab + Audit-the-AI scores, not separately scored —
an instructor who isn't convinced you did the work yourself may re-score those sections down.*
