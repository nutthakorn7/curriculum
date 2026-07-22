# {{ slot_label }} — Security Mindset & Threat-Modeling a Cryptographic System

**Kind:** Conceptual (no Docker target, no flag — same precedent as `software-security`'s Week 1
threat-modeling, and this course's own {{ ref('hybrid-encryption') }}: honestly flag-less, rubric-graded content).
**References:** NIST FIPS 140-3 (security requirements for cryptographic modules) · OWASP
Cryptographic Storage Cheat Sheet · CWE-320 (Key Management Errors) · CWE-330
(Use of Insufficiently Random Values)

## This week — what to do

1. **Before class** — no environment setup needed. This week is discussion- and
   writing-based; no Docker, no code. Skim the course README and
   `course-plan-19weeks.md` so you know what's coming.
2. **Lecture (120 min)** — weekly quiz first (~10 min), then the lecture. Slides:
   `{{ slides }}` *(not yet written — see `course-plan-19weeks.md`)*.
3. **Lab (180 min)** — complete **Worksheet 1** (`worksheet.md`, Parts 1–5, including the
   *Audit-the-AI* task, plus EiPE + Prompt Problem).
4. **Submit** — worksheet PDF (with your threat model + Audit-the-AI critique + prompt
   artifacts) → Classroom · weekly quiz → Google Form.
5. **Project** — start thinking about your term project's trust boundaries now (see
   `project/README.md`); {{ ref('aes-modes') }} formally kicks the project off (team + design doc), but the
   earlier you can name "what data crosses what boundary, encrypted with what," the better your
   {{ ref('aes-modes') }} design doc will be.

## Objectives

- Explain the **CIA triad — Confidentiality, Integrity, Availability — specifically as it
  applies to cryptography**, and why "we encrypted it" is a confidentiality claim only, not an
  integrity or availability guarantee.
- State precisely what "cryptographically secure" promises (a primitive resists a
  well-defined class of mathematical attack, under stated assumptions, at a stated security
  level) — and what it explicitly does **not** promise (that the *system* using it is secure).
- Distinguish a **textbook-secure primitive** from a **real-system failure**: the primitive's
  proof holds; the deployment breaks it anyway, through implementation bugs, side channels,
  bad randomness, protocol/mode misuse, or human/key-management failure.
- Apply **trust boundaries** and a lightweight threat-modeling process (assets, adversaries,
  attack surface) to a system that handles cryptographic keys.
- Preview the throughline of the entire course: every week that follows takes one
  mathematically sound primitive and shows a specific, real way it fails when misused —
  followed by the correct construction.

## 🐍 Signature game — "Snake Oil Bingo"
Everyone gets a bingo card of common crypto myths ("military-grade encryption," "unbreakable
256-bit security," "quantum-proof because the key is long enough"). As the week's AI-generated
exhibit is read aloud and picked apart, mark a square the moment its myth surfaces — but a square
only counts once your table can give the one-line *technical* reason it's wrong. First verified
BINGO wins.

**Why it's exciting:** spotting a plausible-sounding lie is oddly addictive, and "textbook-secure
primitive, real-system failure" is the one lens that transfers to literally every other week this
term.

## Why no lab target this week

There is nothing to exploit yet — no primitive has been introduced, so there is no misuse to
demonstrate a break against. This week is where the course's judgment is built before the
course's tools are handed out: a data-flow/trust-boundary analysis and a critical reading
exercise, not a CTF wrapper. The hands-on core is **Audit-the-AI**: you will critique a
plausible, professionally-worded AI answer to "why does textbook-secure crypto fail in real
systems" that has exactly one systematic gap. Finding that gap *is* this week's exploit — it
is a reasoning exploit instead of a code exploit, and it sets the pattern (distrust confident
AI output, verify against the primary literature) that recurs in every AIR-Sec week after this
one.

## The throughline: textbook-secure vs. real-system failure

A cryptographic primitive being "secure" is a claim about a mathematical object under stated
assumptions (e.g. "SHA-256 is collision-resistant," "AES-256 has no known attack better than
brute force," "the discrete-log problem is hard in this group"). None of that says anything
about whether the *program* calling the primitive is secure. Every remaining teaching week in
this course takes one sound primitive and shows a specific way real systems break it anyway:

| Wk | Primitive (textbook-secure) | Real-system failure mode |
|----|---|---|
| 2  | Cryptographic hash functions | Used for password storage unsalted / unstretched — GPU cracks a whole DB fast even though SHA-256 itself is uncracked |
| 3  | MACs (hash-based auth) | Hash-only "authentication" (no shared secret) is forgeable; naive constructions fall to length-extension |
| 4  | AES block cipher | CBC mode with no integrity check is malleable — an attacker flips ciphertext bits to control plaintext, undetected |
| 5  | Diffie–Hellman key exchange | Textbook DH has no authentication — a MITM completes two separate key exchanges and relays, undetected |
| 6  | AEAD / MAC + encryption composition | Wrong composition order (MAC-then-encrypt) or a verbose error path opens a padding oracle |
| 10 | Hybrid (asymmetric + symmetric) encryption | Correct RSA-OAEP, correct AES-GCM, one reused nonce — plaintext and even forgeries leak anyway |
| 11 | ECDSA digital signatures | Nonce reuse (or biased nonces) across two signatures algebraically recovers the private key |
| 12 | TLS / certificate-based transport | The cryptography is sound; a client that skips hostname/chain validation is MITM-able anyway |
| 13 | End-to-end encryption | "Encrypted in transit" (TLS-only) still lets the *server* read everything; only E2E design changes that trust boundary |
| 14 | Authentication protocols | Correct hashing/salting doesn't help if the password still crosses the wire in the clear, or sessions are predictable |
| 15 | Post-quantum signatures (Lamport OTS) | Provably secure **as a one-time scheme** — sign twice with the same key pair and the private key leaks |

Notice the pattern: in every single row, the primitive itself is not broken. What breaks is a
decision made *around* the primitive — a missing check, a reused value, a skipped
verification, an assumption ("this key is only used once") that the real system quietly
violates. Learning to ask "what assumption is this primitive relying on, and does this system
actually uphold it?" is the single most transferable skill in this course, and it starts today.

## CIA, specifically for cryptography

The CIA triad is usually taught in general terms. Applied to a system that uses cryptography,
each property maps to a specific mechanism — and, critically, to a specific *limit*:

- **Confidentiality** — what encryption provides, when done correctly (right primitive, right
  mode, right key management). It answers "can an adversary read this." It says **nothing**
  about whether an adversary can *tamper* with it undetected (see Integrity) or make it
  *unavailable* (see Availability). "It's encrypted" is not a complete security claim.
- **Integrity / Authenticity** — provided by MACs, signatures, and authenticated encryption
  (AEAD), not by encryption alone. This is the single most common conflation this course exists
  to correct: **encryption without a MAC/signature gives you confidentiality with no integrity
  guarantee**, and ciphertext can be tampered with in structured, exploitable ways ({{ ref('aes-modes') }}).
  Encrypt-then-MAC, or a proper AEAD mode, is what actually closes this gap ({{ ref('aead') }}).
- **Availability** — the property cryptography most often *works against* if misused. Key loss
  (no recovery path) makes data permanently unavailable to its rightful owner; certificate
  expiry breaks TLS availability; a poorly designed key-rotation scheme can lock out an entire
  fleet. Availability failures in cryptographic systems are usually **key-management**
  failures, not algorithm failures.

A trust boundary, applied to a system handling cryptographic keys, is any point where control
over — or visibility into — key material changes hands: client vs. server, application vs. OS
keystore/HSM, one microservice vs. another, a developer's laptop vs. production. Every time key
material crosses one of these boundaries (generated here, transmitted there, stored there,
backed up there), that crossing is where key-management failures concentrate — hardcoded keys
in source control, keys logged in plaintext, keys shared across environments, keys with no
rotation or revocation path. Most catastrophic real-world "crypto failures" are actually
trust-boundary failures around otherwise-sound primitives.

## Deliverable

- Worksheet 1 (Parts 1–5, all sections including the Conventional-arm essay questions,
  Audit-the-AI, EiPE, Prompt Problem).
- No flag this week — grading is rubric-based (see `worksheet.md`'s grading table).

## References

- NIST FIPS 140-3, *Security Requirements for Cryptographic Modules*.
- CWE-320 (Key Management Errors), CWE-330 (Use of Insufficiently Random Values) —
  https://cwe.mitre.org/
- https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
- fail0verflow, *Console Hacking 2010: PS3 Epic Fail* (27C3) — ECDSA nonce-reuse key
  recovery; foreshadows {{ ref('signatures-zkp') }}.
- Debian OpenSSL predictable-RNG advisory (CVE-2008-0166) — a sound primitive fed
  low-entropy input by a packaging bug.
