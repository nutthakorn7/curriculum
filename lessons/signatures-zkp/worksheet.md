# Worksheet 11 — Digital Signatures & Zero-Knowledge Proofs (100-minute core + preparation/extensions)

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Topic source:** `Week10_Signatures Questions.docx` (KOSEN68) — 5 essay questions, all ported
> below as this week's written task (Part 1).
> **Signature game:** "Double-Spend the Bank" (ECDSA `(r, n−s)` malleability against a bank that
> deduplicates transactions by signature hash — an illustrative bank-accounting double-processing bug).

> **Ethics note:** Attack only the two local containers this lab spins up
> (`vulnerable_app.py` / `fixed_app.py`, ports 8102/8103). Forging or replaying transactions
> against real payment systems, exchanges, or blockchains you don't own is illegal. Keep your
> `FLAG_SIG` inside this lab environment.

## 100-minute class and assigned worksheet version

**In class:** 10 min retrieval quiz + 10 min brief explanation + 70 min guided practice + 10 min evidence review/exit = 100 min.

**Shared core — every student:** Obtain a fresh signature in class; compute its twin and transaction identifiers; submit the original/twin to the vulnerable bank; verify a legitimate fixed-bank withdrawal succeeds and its high-S twin fails; explain the control's limits.

**Preparation and extensions:** Before class, prepare images/dependencies and read the topology only. Do not collect live signatures before class or reuse signatures across a restart. Complete the long signature/ZKP analysis and the assigned version-specific work outside the core block.

**70-minute practice:** fresh signature 10; twin calculation 15; two vulnerable withdrawals 15; fixed positive/negative controls 15; reasoning 15. Start the manual vulnerable withdrawals against fresh state before any automated exploit. Each bank has its own key: obtain a separate signature from the fixed bank. A restart invalidates previously captured signatures.


**Assessment:** everyone completes the shared core (60 points) plus **one assigned version** (40 points): Conventional written analysis, or AIR-Sec Audit-the-AI 20 + EiPE 10 + Prompt Problem 10. Both versions total 100. All questions remain available; complete the assigned version's full questions, using out-of-class time for extended responses. The other version is ungraded reference practice, not an additional requirement. Viva/micro-demo questions are formative checks of the submitted explanation, with no separate points or automatic pass/fail score gate.

**Evidence:** record reproducible observations or reasoning and your name/student ID. Where the local target prints a shared placeholder flag, record it as observed; a personalized flag or live CTFd account is not a prerequisite. Follow SUBMISSION.md for the announced hand-in channel.

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

**Q2. Schnorr Proofs and the Fiat–Shamir Connection.** Starting from the **Schnorr identification protocol**, explain: (a) how Peggy demonstrates knowledge of a secret without revealing it; (b) how replacing the verifier's random challenge with a hash binding the commitment, public statement and message yields a Schnorr-type non-interactive construction under stated assumptions; and (c) distinguish this specific proof-of-knowledge connection from a blanket claim that every digital signature, including ECDSA, is a zero-knowledge proof. See [RFC 8235](https://www.rfc-editor.org/rfc/rfc8235.html).

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
a changed transaction identifier could confuse exchange withdrawal tracking; distinguish **MtGox**'s historical claim from Decker and Wattenhofer's measured evidence rather than assuming that malleability caused the collapse ([paper](https://arxiv.org/abs/1403.6676)). (c) Explain why **SUF-CMA** (strong
existential unforgeability) is a *stronger* guarantee than **EUF-CMA**, and which one malleability
violates. (d) How should a protocol designer build a system *assuming* signatures are malleable
(name at least two concrete defenses)?

---

## Part 2 — Shared Practical Core + Defense (in the 100-minute session)

**Learning goals:** exploit ECDSA malleability to double-spend against a bank that dedups by
signature hash, then verify low-S rejects the particular high-S twin and explain the remaining transaction-identity limitation — the *practical* twin of Part 1's Q5.
**Prerequisites:** Docker; `ecdsa` + `requests` (either on the host, or run `exploit.py` in a
throwaway container on the compose network, as the README shows).

**Environment setup**
```bash
cd {{ labpath }}
docker compose up -d        # vulnerable_app.py on :8102, fixed_app.py on :8103
curl localhost:8102/        # confirm it's up
```

**Task 0 — Preparation: read the design (outside the live run).** *Goal:* see the vulnerable design decision. *Steps:* read
`vulnerable_app.py`'s `txid_of` and `withdraw` functions; identify the exact line that decides a
transaction's identity and confirm it hashes the *signature* (`sha256(str(r)+str(s))`), not the
`(message, pubkey)`. *Deliverable:* quote the line and state, in one sentence, why that choice is
what makes malleability exploitable here.

**Task 1 — Shared core: obtain a fresh signature in class (10 min).** *Goal:* get a real `(r, s)`. *Steps:*
`curl localhost:8102/sign`; record `sig_r`, `sig_s`, and the fixed `message`. Also
`curl localhost:8102/pubkey`. *Deliverable:* the `(r, s)` pair and the pubkey hex.

```sim
ecdsa-malleability
```

**Task 2 — Shared core: do the malleation by hand (15 min).** *Goal:* understand the math, not just run a
script. *Steps:* with `n = 0xFFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C
D0364141` (the SECP256k1 group order), compute `s' = n − s` for your captured `s` (Python:
`n = ecdsa.SECP256k1.order`). Compute both `txid = sha256(str(r)+str(s))` and
`txid' = sha256(str(r)+str(s'))` and confirm they differ. State which of `s`, `s'` is **low-S**
(`≤ n//2`) — exactly one is. *Deliverable:* your `s'`, the two txids, and which one is low-S.

**Task 3 — Shared core: demonstrate double processing (15 min).** *Goal:* process one authorization twice.
*Steps:* do the double-spend **by hand with `curl` first**, so its JSON response is your own
from-scratch proof — the bank's `_total_withdrawn` is global, in-memory state that never resets
between requests, so this must be the *first* withdrawal attempt against a freshly started
container (do not run `exploit.py` yet). Use the fresh `(r, s)` captured in Task 1 and the matching twin calculated in Task 2, without restarting the bank or obtaining a different pair between those tasks. If the bank restarted, repeat Tasks 1–2. Submit both signatures in order:
```bash
curl -s -X POST localhost:8102/withdraw -H 'Content-Type: application/json' \
  -d '{"message":"withdraw 100 to attacker","sig_r":"<r>","sig_s":"<s>"}'
curl -s -X POST localhost:8102/withdraw -H 'Content-Type: application/json' \
  -d '{"message":"withdraw 100 to attacker","sig_r":"<r>","sig_s":"<n-s>"}'
```
**Extension after the manual controls in Task 4:** run `python exploit.py` (or the container form in the README) as an automated confirmation of the same attack. Its own totals will now start above 100 since the bank's state
persists across requests — that's expected, not a bug; if you run `exploit.py` first instead,
the by-hand reproduction can no longer land on `total_withdrawn:200` (a repeat of the *same*
signature gets `409 replay`, and even a *fresh* one lands on 300/400 because the counter never
reset), so keep this order.
*Deliverable:* the flag + your two `curl` commands and the second one's JSON response (must show
`double_spend_detected` and `total_withdrawn:200`).

**Task 4 — Shared core: fixed positive/negative controls (15 min).** *Goal:* prove the fix works, not
just claim it. *Steps:* use a fresh fixed-bank run and obtain its own low-S signature from `curl localhost:8103/sign` (the two banks have different keys). Submit that low-S signature once to `:8103/withdraw` and confirm a successful legitimate withdrawal; submit its high-S twin `(r, n-s)` and confirm `403` with no flag. Capture both responses. Do not submit the vulnerable bank's signature to the fixed bank. Read `fixed_app.py`'s `is_low_s` and the guard in `withdraw`; identify the added check. The optional automated replay follows these manual controls, not the other way round.
*Deliverable:* the rejection evidence (`403` + body) + the one-line difference between the two
`withdraw` functions, in words.

**Task 5 — Shared core reasoning (15 min); full written analysis is an extension.** *Goal:* connect the exploit to the theory.
*Steps:* answer in your own words: (a) Why are `(r, s)` and `(r, n−s)` *both* valid signatures for
the same message and key — what step of ECDSA verification is unchanged when you negate `s` mod
`n`? (b) Why does deduplicating by **signature hash** let the twin through, while deduplicating by
**`(message, pubkey)`** would not? (c) Why does the low-S rule (`s ≤ n//2`) accept exactly one member of this **particular twin pair**? Why does that not imply a unique signature for the message/key when fresh ECDSA nonces can create other valid low-S signatures, and why is an application transaction ID still needed? *Deliverable:* 3 short
paragraphs, one per sub-question.

---

## Evidence & Integrity (required)

- **Attribution and reproducibility (both versions):** put your name/student ID on the submitted work and provide your own commands, observations and explanation. A screenshot or annotated transcript is acceptable; shared placeholder output is not per-student proof by itself.
- **Optional terminal-stamp example:** `printf '%s | %s | ' "$(whoami)" '<YOUR-STUDENT-ID>'; date '+%F %T %Z'`. This is one way to label a capture, not a separate requirement, point allocation or live-personalization prerequisite.
- **Observed flag (shared placeholder unless per-student seeding is announced):** ____________________
  Attach your own execution evidence; personalization is not a prerequisite for full marks.
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the double-spend work** (why did the bank see one
     authorization as two transactions)?
  2. **Why does the low-S fix actually stop it** — and what could still break a bank that used
     low-S but *also* still dedups by signature hash? (Hint: is low-S the *only* source of
     ECDSA/transaction malleability, or could other encodings — e.g. non-canonical DER,
     `scriptSig` mutations in the real Bitcoin case — still change the txid? What extra fix from
     Q5(d) closes that?)

---

## 🤖 Assigned AIR-Sec Audit the AI

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
> counts toward the **Audit the AI** row of the grading rubric.

---

## 🧠 Assigned AIR-Sec Comprehension & Prompt

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

## 🎤 Formative viva spot-check (no separate points; questions retained)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "Here is your captured `s`. Without a script, tell me how you'd compute the malleated twin, and
   which of the two — `s` or `n − s` — the *fixed* bank would accept, and why exactly one of them
   passes the `s ≤ n/2` check."
2. "The vulnerable bank *does* reject an exact replay of the same `(r, s)` with `409`. So why does
   the `(r, n − s)` twin get through when it's 'the same transaction'? Point to the one line that
   decides transaction identity and explain what it hashes."
3. "Explain the Schnorr identification / Fiat–Shamir connection and distinguish it from a blanket zero-knowledge guarantee for every signature scheme — what is the 'secret' being proven, and where did the interactive *challenge* from the
   Schnorr protocol go when it became a signature?"

---

## Grading rubric (100)

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| Shared practical core: complete the assigned run or coding steps | 20 | 20 |
| Shared control and limitations: compare the secure control and explain what it does and does not show | 20 | 20 |
| Shared reproducible evidence and reasoning: attributable observations, commands/results and explanation | 20 | 20 |
| Assigned Conventional written questions | 40 | — |
| Assigned AIR-Sec Audit-the-AI | — | 20 |
| Assigned AIR-Sec Explain-in-Plain-English | — | 10 |
| Assigned AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

**Deadline and late work:** hand in by 23:59 Thai time (ICT) on the Sunday before the next week's
class (KOSEN rule); the exact date is on `learn.zcr.ai/submit`.
Late work loses 10% of this worksheet's score for each day late (a part day counts as a day), down to 0.

Viva/micro-demo checks are formative: no separate points and no automatic score gate. The 60 shared points apply to both versions; do not add the unassigned version's 40 points.

Viva checks provide formative feedback and clarification within the published criteria; they carry no extra points or automatic score gate.
