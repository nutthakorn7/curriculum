# Worksheet 11 — Digital Signatures & Zero-Knowledge Proofs (3 hrs)

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Topic source:** `Week10_Signatures Questions.docx` (KOSEN68) — 5 essay questions, all ported
> below as this week's written task (Part 1).
> **Signature game:** "Double-Spend the Bank" (ECDSA `(r, n−s)` malleability against a bank that
> deduplicates transactions by signature hash — a MtGox-style double-spend).

> **Ethics note:** Attack only the two local containers this lab spins up
> (`vulnerable_app.py` / `fixed_app.py`, ports 8102/8103). Forging or replaying transactions
> against real payment systems, exchanges, or blockchains you don't own is illegal. Keep your
> `FLAG_SIG` inside this lab environment.

## Part 0 — Student Information
| Name | Student ID | Date | Group | AI tools used (declare) |
|---|---|---|---|---|

---

## Part 1 — Conventional Arm: Written Questions (ported from KOSEN68, Q1–Q5)

Answer each in your own words (4–8 sentences, more where the question asks for a design or a
comparison). **This is a normal written/essay task — no AI-resilience layer applies to this
part; answer it yourself.**

**Q1. Signatures vs. MACs.** Compare digital signatures and MACs on: (a) what key each uses to
*create* an authenticator and what key each uses to *verify* it, (b) *who* is able to verify, and
(c) typical use cases for each. Then answer directly: **why are digital signatures suitable for
public systems (PKI) while MACs are not?**

**Q2. Signatures as Zero-Knowledge Proofs.** Starting from the **Schnorr identification
protocol**, explain: (a) how Peggy proves to Victor that she *knows* a secret (her private key)
without revealing it; (b) why replacing the verifier's random *challenge* with a *hash* of the
commitment (and message) — the **Fiat–Shamir transform** — turns the interactive proof into a
**signature**; and (c) why a digital signature can therefore be viewed as a **non-interactive
zero-knowledge proof of knowledge** of the private key.

**Q3. RSA vs. ECDSA vs. EdDSA (Ed25519).** Compare the three on: (a) the hardness assumption each
relies on, (b) how easy each is to implement *correctly*, and (c) known pitfalls (e.g. RSA
padding choices; ECDSA's catastrophic dependence on a unique, unpredictable nonce `k`). Then:
**why is EdDSA (Ed25519) generally recommended for modern systems?**

**Q4. Substitution Attacks.** Explain how a signature can still verify **True** even when the
*public key* or the *message* is changed out from under a verifier (e.g. duplicate-signature key
selection / a maliciously chosen key that validates an existing signature on a *different*
message). Why do these attacks surprise developers who assume "verifies True" means "this exact
signer signed this exact message"? Why is this class of attack **not fully covered by the
EUF-CMA** security model?

**Q5. Signature Malleability.** (a) Define signature malleability in simple terms. (b) Explain how
it contributed to the **MtGox** collapse (transactions being "modified" so they appeared not to
have been processed, enabling double-withdrawal claims). (c) Explain why **SUF-CMA** (strong
existential unforgeability) is a *stronger* guarantee than **EUF-CMA**, and which one malleability
violates. (d) How should a protocol designer build a system *assuming* signatures are malleable
(name at least two concrete defenses)?

---

## Part 2 — AIR-Sec Arm: Hands-on Lab + Defense (180 min)

**Learning goals:** exploit ECDSA malleability to double-spend against a bank that dedups by
signature hash, then verify low-S / BIP-62 closes the gap — the *practical* twin of Part 1's Q5.
**Prerequisites:** Docker; `ecdsa` + `requests` (either on the host, or run `exploit.py` in a
throwaway container on the compose network, as the README shows).

**Environment setup**
```bash
cd {{ labpath }}
docker compose up -d        # vulnerable_app.py on :8102, fixed_app.py on :8103
curl localhost:8102/        # confirm it's up
```

**Task 0 — Onboarding (15 min).** *Goal:* see the vulnerable design decision. *Steps:* read
`vulnerable_app.py`'s `txid_of` and `withdraw` functions; identify the exact line that decides a
transaction's identity and confirm it hashes the *signature* (`sha256(str(r)+str(s))`), not the
`(message, pubkey)`. *Deliverable:* quote the line and state, in one sentence, why that choice is
what makes malleability exploitable here.

**Task 1 — Obtain a valid signature (15 min).** *Goal:* get a real `(r, s)`. *Steps:*
`curl localhost:8102/sign`; record `sig_r`, `sig_s`, and the fixed `message`. Also
`curl localhost:8102/pubkey`. *Deliverable:* the `(r, s)` pair and the pubkey hex.

**Task 2 — Do the malleation by hand (30 min).** *Goal:* understand the math, not just run a
script. *Steps:* with `n = 0xFFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C
D0364141` (the SECP256k1 group order), compute `s' = n − s` for your captured `s` (Python:
`n = ecdsa.SECP256k1.order`). Compute both `txid = sha256(str(r)+str(s))` and
`txid' = sha256(str(r)+str(s'))` and confirm they differ. State which of `s`, `s'` is **low-S**
(`≤ n//2`) — exactly one is. *Deliverable:* your `s'`, the two txids, and which one is low-S.

**Task 3 — Double-spend & capture the flag (20 min).** *Goal:* process one authorization twice.
*Steps:* run `python exploit.py` (or the container form in the README). It submits `(r, s)`
(accepted, `total_withdrawn=100`) then the twin `(r, n−s)` (accepted again, `total_withdrawn=200`
→ flag). *Also* reproduce the second `POST` by hand with `curl` to convince yourself the script
isn't doing anything hidden:
```bash
curl -s -X POST localhost:8102/withdraw -H 'Content-Type: application/json' \
  -d '{"message":"withdraw 100 to attacker","sig_r":"<r>","sig_s":"<n-s>"}'
```
*Deliverable:* the flag + your `curl` command and its JSON response (must show
`double_spend_detected` and `total_withdrawn:200`).

**Task 4 — Confirm the fix rejects the same trick (20 min).** *Goal:* prove the fix works, not
just claim it. *Steps:* `exploit.py` repeats the identical `(r, s)` then `(r, n−s)` sequence
against `:8103`. Confirm the **low-S first submission is accepted** (a legitimate single
withdrawal) and the **high-S twin is rejected (403)** with no flag. Read `fixed_app.py`'s
`is_low_s` and the guard in `withdraw`; identify the added check versus `vulnerable_app.py`.
*Deliverable:* the rejection evidence (`403` + body) + the one-line difference between the two
`withdraw` functions, in words.

**Task 5 — Explain why, precisely (25 min).** *Goal:* connect the exploit to the theory.
*Steps:* answer in your own words: (a) Why are `(r, s)` and `(r, n−s)` *both* valid signatures for
the same message and key — what step of ECDSA verification is unchanged when you negate `s` mod
`n`? (b) Why does deduplicating by **signature hash** let the twin through, while deduplicating by
**`(message, pubkey)`** would not? (c) Why does the low-S rule (`s ≤ n//2`) leave *exactly one*
canonical signature per `(message, key)`, so the twin has nowhere to hide? *Deliverable:* 3 short
paragraphs, one per sub-question.

---

## Evidence & Integrity (required)

- **Identity proof:** your terminal/screenshot evidence for Tasks 1–4 must show your
  `whoami` / login email / student ID and a timestamp.
- **Personalized flag:** ____________________
  *Flags are unique per student (via the `FLAG_SIG` env override — see README) — submitting
  another student's flag is a violation.*
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the double-spend work** (why did the bank see one
     authorization as two transactions)?
  2. **Why does the low-S fix actually stop it** — and what could still break a bank that used
     low-S but *also* still dedups by signature hash? (Hint: is low-S the *only* source of
     ECDSA/transaction malleability, or could other encodings — e.g. non-canonical DER,
     `scriptSig` mutations in the real Bitcoin case — still change the txid? What extra fix from
     Q5(d) closes that?)

---

## 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

Below is an AI assistant's answer to a developer who asked: *"Write me a function to verify an
incoming transaction and make sure I never process the same one twice."* It looks professional and
uses correct terminology, but it has **at least one subtly serious flaw** — the *same* flaw this
week's lab exploits.

> **AI's answer:**
>
> "Here's a robust pattern. Each transaction carries a message and an ECDSA signature `(r, s)`.
> To prevent processing a transaction twice, compute a unique transaction id from the signature
> and keep a set of ids you've already seen:
>
> ```python
> import hashlib
> seen = set()
>
> def process(tx):
>     # tx = {"message": bytes, "pubkey": VerifyingKey, "r": int, "s": int}
>     sig = encode_sig(tx["r"], tx["s"])
>     if not tx["pubkey"].verify(sig, tx["message"]):
>         raise ValueError("bad signature")          # reject forgeries
>     txid = hashlib.sha256(f'{tx["r"]}:{tx["s"]}'.encode()).hexdigest()
>     if txid in seen:
>         raise ValueError("duplicate transaction")   # idempotency: never process twice
>     seen.add(txid)
>     apply_transaction(tx)                            # move the money
>     return txid
> ```
>
> This is safe: the signature is cryptographically verified before anything happens, so no
> attacker can inject a transaction they didn't sign. And because the txid is derived from the
> signature itself, replaying the exact same request is caught by the `seen` set — you get
> idempotency for free. Deriving the id from the signature is actually *better* than hashing the
> message, because two different legitimate transactions could in theory share a message but will
> always have different signatures."
>
> — end of AI answer —

1. **Find what's wrong or risky in it.** Quote the exact sentence(s). (Hint: the signature
   *verification* is fine, and catching an *exact* replay is fine — don't waste your critique
   there. Look at the claim that deriving the txid *from the signature* gives idempotency, and at
   the final sentence arguing it is "better than hashing the message." What can an attacker who
   holds one valid `(r, s)` do to the *signature bytes* without invalidating the signature?)
2. **Produce the correct, verified version yourself.** Rewrite the two flawed parts (the txid
   derivation and the "better than hashing the message" justification). Your fix must (a) reject
   or canonicalize non-low-S signatures **and/or** (b) derive the txid from `(message, pubkey)`
   (or a chosen application-level nonce) rather than from the signature bytes. Explain in 2–3
   sentences why the AI's version processes the *same authorization twice* even though every
   signature it accepts is genuinely valid.

> Disclose your AI use (if any, beyond this provided artifact) in the Part 0 table. This task
> counts toward your Defense + Reflection score.

---

## 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE) — Zero-Knowledge Proof.** Explain to a junior developer who
has never heard the term "zero-knowledge proof": **how can you prove you know a password (or a
private key) without ever sending it, and without the verifier learning it?** In 3–5 sentences,
describe the *idea* of the Schnorr protocol in plain language — a commitment, a challenge, and a
response — and why an eavesdropper (or the verifier) who sees the exchange still cannot log in as
you afterward. Avoid just restating jargon ("it's zero-knowledge because it reveals zero
knowledge") — explain the *mechanism*: you answer a fresh unpredictable challenge in a way only
the secret-holder could, and a different challenge next time means a recording is useless. Then, in
one sentence, connect it to Part 1 Q2: *why is a signature basically this same proof, but with the
challenge replaced by a hash so no live verifier is needed?*

**B. Prompt Problem.** Write a **single prompt** that asks an AI to explain *why ECDSA signatures
are malleable (the `(r, n−s)` twin) while EdDSA/Ed25519 signatures are not*. Run it, then critique
the AI's answer:
- Does it correctly explain that ECDSA verification depends on `s` only through a value that is
  unchanged when `s → n − s` (so both are valid), i.e. malleability is inherent to the *scheme*,
  not a bug?
- Does it correctly state that **Ed25519 fixes this by construction** — the signature encoding is
  deterministic and the verification equation pins down a unique canonical `S` (via `S < L`
  checks in RFC 8032), so there is no valid twin?
- Does it **hallucinate** anything — e.g. claim EdDSA is "immune because it's newer," confuse
  malleability with a nonce-reuse attack (a *different*, key-recovery bug), or invent a wrong
  curve order / wrong BIP number for the low-S rule (it's **BIP-62 / BIP-146**)?

Submit the **final prompt + the AI's answer + your critique** (3–5 sentences covering the three
bullet points above).

---

## 🎤 Viva spot-check (instructor use — 3 questions)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "Here is your captured `s`. Without a script, tell me how you'd compute the malleated twin, and
   which of the two — `s` or `n − s` — the *fixed* bank would accept, and why exactly one of them
   passes the `s ≤ n/2` check."
2. "The vulnerable bank *does* reject an exact replay of the same `(r, s)` with `409`. So why does
   the `(r, n − s)` twin get through when it's 'the same transaction'? Point to the one line that
   decides transaction identity and explain what it hashes."
3. "Explain how a plain digital signature is a zero-knowledge proof of knowledge of the private
   key — what is the 'secret' being proven, and where did the interactive *challenge* from the
   Schnorr protocol go when it became a signature?"

---

## Grading rubric (100)

| Criterion | Points |
|---|---|
| Part 1 — Conventional written questions (Q1–Q5) | 25 |
| Part 2 — Lab tasks 0–5 (evidence: captured `(r,s)`/twin, txids, curl output, 403 on fixed) | 30 |
| Evidence & Integrity (flag capture + own-words explanation) | 10 |
| Audit the AI (flaw(s) found + corrected `process()` design) | 20 |
| Comprehension & Prompt (EiPE on ZKP + Prompt Problem) | 15 |

*Viva spot-checks are pass/fail gates on the Lab + Audit-the-AI scores, not separately scored — an
instructor who isn't convinced you did the work yourself may re-score those sections down.*
