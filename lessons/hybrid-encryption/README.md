# {{ slot_label }} — Asymmetric & Hybrid Encryption

**Kind:** Conceptual (no Docker target, no flag — same precedent as this course's {{ ref('intro') }} and
`software-security`'s Weeks 1, 12–13: honestly flag-less, rubric-graded content).
**References:** NIST SP 800-56A (key establishment), SP 800-38D (GCM) · OWASP Cryptographic
Storage Cheat Sheet

## This week — what to do
1. **Before class** — skim last week's recap (Key Exchanges). No environment setup needed —
   this week is Python-only, standard library + `cryptography` (already used in earlier weeks).
2. **Lecture (120 min)** — weekly quiz first (~10 min), then the lecture. Slides:
   `{{ slides }}` *(not yet written — see `course-plan-19weeks.md`)*.
3. **Lab (180 min)** — complete **Worksheet 10** (`worksheet.md`, Parts 1–5, including the
   *Audit-the-AI* task in `audit_the_ai/`, plus EiPE + Prompt Problem).
4. **Submit** — worksheet PDF → Classroom · code (`audit_the_ai/fixed_hybrid_encrypt.py`,
   your proof script) → GitHub · weekly quiz → Google Form.
5. **Project** — if your term project sends data between two parties that don't already share a
   secret, this week's pattern (RSA-OAEP wraps an AES session key) is directly applicable.

## Objectives
- Explain why asymmetric encryption alone is unsuitable for bulk data (performance + message
  size limits), and why hybrid encryption exists to solve that.
- Trace the complete hybrid-encryption flow end to end: key generation, key wrapping, symmetric
  encryption, transmission, unwrapping, decryption.
- Explain how a public key lets anyone encrypt to a recipient, while only the holder of the
  matching private key can decrypt.
- Explain asymmetric key exchange (how two parties derive a shared secret an eavesdropper
  cannot compute) and connect it to ECIES as a concrete hybrid scheme built on ECDH.
- Audit an AI-generated cryptographic implementation for a subtle-but-catastrophic correctness
  bug that a surface-level review would miss.

## 🔬 Signature game — "Nonce Detective"
You're handed a hybrid-encryption implementation that looks textbook-correct — proper RSA-OAEP,
proper AES-GCM, nothing obviously wrong at a skim. Find the one planted bug, then prove it's real
by actually recovering leaked plaintext from two intercepted messages, not just pointing at a
line of code.

**Why it's exciting:** the code passes every "did they use the right primitives" checklist — the
only way to catch it is to actually think like an attacker, and the payoff is a genuine "aha"
the moment the recovered plaintext prints.

## Why no lab target this week

Nothing here is a "break into a running service" exploit — it's protocol design and
correctness analysis, same category as `software-security`'s threat-modeling and supply-chain
weeks. Rather than force an artificial CTF wrapper onto that, this week's hands-on core is an
**Audit-the-AI** exercise: a plausible, AI-generated-looking hybrid-encryption implementation
that passes a shallow review and fails a careful one. See `audit_the_ai/README.md`.

## Deliverable
- Worksheet 10 (Parts 1–5, all sections including Audit-the-AI + EiPE + Prompt Problem).
- From `audit_the_ai/`: the exact buggy line(s) quoted, your proof-of-attack script + output,
  your explanation, and `fixed_hybrid_encrypt.py`.
- No flag this week — grading is rubric-based (see worksheet.md's grading table).

## References
- NIST SP 800-56A Rev. 3, *Recommendation for Pair-Wise Key-Establishment Schemes Using
  Discrete Logarithm Cryptography*.
- NIST SP 800-38D, *Recommendation for Block Cipher Modes of Operation: GCM and GMAC*.
- https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- SEC 1: Elliptic Curve Cryptography, §5.1 (ECIES) — Standards for Efficient Cryptography Group.
- Joux, *Authentication Failures in NIST version of GCM* (2006).
