# Worksheet 10 — Asymmetric & Hybrid Encryption

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** NIST SP 800-56A (key establishment), SP 800-38D (GCM) · OWASP Cryptographic Storage Cheat Sheet
> **Kind:** Conceptual — no Docker target, no flag this week. Grading is rubric-based (see below).

## 100-minute class and assigned worksheet version

**In class:** 10 min retrieval quiz + 10 min brief explanation + 60 min practice/analysis + 15 min debrief + 5 min evidence capture = 100 min.

**Shared core — every student:** Trace the hybrid-encryption protocol and key roles; compare correct nonce discipline with a repeated-nonce case. Provide a repeatable diagram, state table or two-message XOR derivation. No Docker target, flag or standalone code submission is required for the shared core.

**Preparation and extensions:** Prepare the public-key/AEAD reading and Python environment if using the AIR-Sec task. Complete the assigned version's full essays or code audit, proof and corrected code outside the core block as needed.

**Assessment:** everyone completes the shared core (60 points) plus **one assigned version** (40 points): Conventional written analysis, or AIR-Sec Audit-the-AI 20 + EiPE 10 + Prompt Problem 10. Both versions total 100. All questions remain available; complete the assigned version's full questions, using out-of-class time for extended responses. The other version is ungraded reference practice, not an additional requirement. Viva/micro-demo questions are formative checks of the submitted explanation, with no separate points or automatic pass/fail score gate.

**Evidence:** record reproducible observations or reasoning and your name/student ID. Where the local target prints a shared placeholder flag, record it as observed; a personalized flag or live CTFd account is not a prerequisite. Follow SUBMISSION.md for the announced hand-in channel.

## Part 1 — Student Information
| Name | Student ID | Date | Group |
|---|---|---|---|
| | | | |

*Disclose any AI assistance used anywhere in this worksheet here (tool + what you asked it).*

## Part 2 — Conventional Arm: Essay Questions

Answer each in your own words. These are conceptual questions with no single "correct" sentence
to copy — you are graded on the accuracy and completeness of your reasoning, not length.

**Q1.** Explain why asymmetric encryption is not suitable for encrypting large files such as
videos or PDFs. Mention both performance and message size limitations.

**Q2.** Describe the complete process of hybrid encryption when Bob sends a message to Alice —
what keys are generated, what is encrypted with which key, what is sent, how Alice decrypts.

**Q3.** In a public-key system, Alice publishes her public key. Explain how Bob can send Alice a
secret message using this key, and why only Alice can read the message.

**Q4.** Explain how asymmetric encryption can be used for key exchange. Describe how a shared
secret is created and why an attacker cannot learn it.

**Q5.** ECIES is a hybrid encryption scheme based on elliptic-curve Diffie-Hellman. Explain how
ECIES allows Alice and Bob to encrypt and decrypt a message without ever sending the symmetric
key directly.

*(120–200 words per answer is a reasonable target — enough to show you understand the
mechanism, not so much that you're padding.)*

## Part 3 — Assigned AIR-Sec Arm: Audit the AI

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's
answer. Full task instructions: [`audit_the_ai/README.md`](audit_the_ai/README.md).

**Setup.** `audit_the_ai/broken_hybrid_encrypt.py` is a plausible, AI-generated implementation
of Bob-to-Alice hybrid encryption (RSA-OAEP wraps a fresh AES-256 session key; AES-GCM encrypts
each message). It runs. It round-trips correctly. It has exactly one planted bug.

**Task.**
1. Read the code. Confirm for yourself that RSA-OAEP usage, AES-256 key generation, and GCM's
   authentication-tag handling are all correct — they are, and checking only those is exactly
   the trap.
2. Find the one bug. Quote the exact line(s).
3. Write a short proof script demonstrating the concrete attack the bug enables against two
   messages sent in the same session. Include its output.
4. Explain in your own words (3–5 sentences): what the vulnerability is, what an eavesdropper
   who records two or more of Bob's messages can actually do, and why.
5. Submit `fixed_hybrid_encrypt.py` — the smallest correct fix — and state explicitly why the
   RSA/OAEP portion of the file did not need to change.

**Submit:** the quoted buggy line(s), your proof script + output, your explanation, and
`fixed_hybrid_encrypt.py`.

## Part 4 — Assigned AIR-Sec Comprehension & Prompt

**A. Explain in Plain English (EiPE).** A non-technical stakeholder on your team asks: *"Why not
just use RSA for everything? Why bother mixing in AES at all?"* In 3–5 sentences, with no
jargon (no "OAEP," "GCM," "asymptotic complexity" — explain the *idea*, not the acronyms),
explain why real systems use hybrid encryption instead of pure asymmetric encryption. A good
answer should make sense to someone who has never taken a cryptography course.

**B. Prompt Problem.** Write a single prompt asking an AI assistant to **implement ECIES**
(Elliptic-Curve Integrated Encryption Scheme) correctly in Python. Run it, then critique the
result:
- Did it choose a real, standard curve (e.g. P-256/secp256r1 or X25519) rather than inventing
  parameters, or silently picking something inappropriate?
- Did it derive the symmetric key via a proper KDF (e.g. HKDF) from the ECDH shared secret,
  rather than using the raw shared secret directly as an AES key?
- Did it use authenticated encryption (AES-GCM or ChaCha20-Poly1305) for the payload, or
  something unauthenticated?
- Did it handle the nonce correctly (this week's Part 3 bug, watch for it recurring here), and
  transmit the ephemeral public key + nonce alongside the ciphertext?
- Did it hand-wave, skip, or get wrong anything else — e.g. point validation on the received
  public key, constant-time comparison, or error messages that leak whether decryption failed
  at the KDF/tag stage (a padding-oracle-style leak)?

**Submit:** your exact prompt, the AI's full response, and a bullet-by-bullet critique against
the checklist above (mark each item correct / incorrect / hand-waved, with the specific line
you're pointing at).

## Part 5 — Formative Viva Spot-Check (no separate points)

Be ready to answer these live, in your own words, with no notes:

1. Why does the bug in `broken_hybrid_encrypt.py` not show up when you only send one message
   per session?
2. If a program only ever sends exactly one message per `HybridEncryptor` session and then
   discards it, is the code in `broken_hybrid_encrypt.py` secure? Is it still bad practice?
3. Suppose the nonce were derived from the current wall-clock time in seconds instead of being
   a fixed constant. Would that fix the bug? Why or why not?

## Grading rubric (100)

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| Shared protocol/analysis core: correct key roles and hybrid flow | 20 | 20 |
| Shared secure-construction analysis: nonce discipline, trust assumptions and limitations | 20 | 20 |
| Shared reproducible reasoning: diagram/state trace or two-message derivation, with sources and attribution | 20 | 20 |
| Assigned Conventional written questions | 40 | — |
| Assigned AIR-Sec Audit-the-AI | — | 20 |
| Assigned AIR-Sec Explain-in-Plain-English | — | 10 |
| Assigned AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

**Deadline and late work:** hand in before the start of the next week's class session (KOSEN rule).
Late work loses 10% of this worksheet's score for each day late (a part day counts as a day), down to 0.

Viva/micro-demo checks are formative: no separate points and no automatic score gate. The 60 shared points apply to both versions; do not add the unassigned version's 40 points.

See [`instructor` answer key] *(instructor use only, not in this file)* for the detailed
Audit-the-AI rubric bands (full/partial/no credit) and expected-answer notes for the viva.

---

## Evidence & Integrity (required)

- **Identity proof:** put your name/student ID and the date on every file you submit (Part 1).
- **No personalized flag this week** — this is a Conceptual week, graded entirely on your
  shared protocol reasoning and the assigned version's written or code-analysis evidence. See `audit_the_ai/README.md` for why a
  CTF-style wrapper isn't used here.
- **Explain in your own words** *(graded on your reasoning, not copied text)*: for the
  Audit-the-AI task specifically, re-state in 1–2 sentences why the fix you chose is correct
  and what would happen if you had instead only changed something else (e.g. the RSA key size).
