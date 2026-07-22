# Worksheet 1 — Security Mindset & Threat-Modeling a Cryptographic System

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** NIST FIPS 140-3 · OWASP Cryptographic Storage Cheat Sheet · CWE-320, CWE-330
> **Kind:** Conceptual — no Docker target, no flag this week. Grading is rubric-based (see below).

## Part 1 — Student Information

| Name | Student ID | Date | Group |
|---|---|---|---|
| | | | |

*Disclose any AI assistance used anywhere in this worksheet here (tool + what you asked it).*

## Part 2 — Conventional Arm: Short-Answer Questions

Answer each in your own words (4–8 sentences unless noted). These are conceptual questions —
you are graded on the accuracy and completeness of your reasoning, not on matching a specific
sentence.

**Q1.** "Cryptographically secure" is a specific, bounded claim. Explain what it actually
promises (be precise: about what class of attack, under what assumptions, at what security
level) — and then explain what it does **not** promise about the system that uses the
primitive. Give one sentence of each.

**Q2.** Describe one real incident in which a mathematically sound cryptographic primitive was
used correctly *in theory* but the system around it failed anyway (implementation bug, bad
randomness, protocol misuse, side channel, or key-management failure — pick one). Name the
primitive, name the specific misuse, and state what actually leaked or broke as a result. (You
may use an incident from the References list, or another one you can verify — cite your
source.)

**Q3.** Define *trust boundary*. Then apply it specifically to a system that handles
cryptographic keys: name three concrete points in a typical web application's architecture
where key material crosses a trust boundary, and for each, name one thing that commonly goes
wrong at that crossing.

**Q4.** Apply the CIA triad specifically to cryptography (not to security in general). For each
of Confidentiality, Integrity, and Availability: (a) name the cryptographic mechanism most
responsible for providing it, and (b) give one concrete example of that property failing *even
when the underlying primitive was mathematically sound*.

**Q5.** "We encrypted the data, so it's secure" is a common but incomplete claim. Explain
precisely what gap this claim leaves open, using the distinction between confidentiality and
integrity/authenticity. What specific kind of attack becomes possible when encryption is used
with no integrity mechanism?

**Q6.** This course covers eleven more primitive-focused teaching weeks, each pairing one
textbook-secure primitive with one way real systems break it (see this week's README table;
Week 16 is a capstone studio, not a new primitive, so it isn't in that table). Pick **two** weeks
from that table that you have not yet studied. For each, based only on the primitive's name and
your general knowledge (you are not expected to know the specific attack yet), write one
sentence hypothesizing what assumption a real system might violate that the primitive itself
doesn't defend against. (There's no single correct answer here — you'll find out how close your
intuition was later in the course. You're graded on making a specific, falsifiable guess, not
on being right.)

## Part 3 — AIR-Sec Arm: Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not on agreeing
or disagreeing wholesale with the AI. This week's Audit-the-AI target is not code (no primitive
has been introduced yet); it's a piece of confident, professionally-worded **prose** that has
exactly one systematic, load-bearing gap.

**Setup.** Below is a real answer an AI assistant gave when asked: *"Why does textbook-secure
cryptography fail in real systems?"* It is well-written, uses correct terminology throughout,
and every individual factual claim in it is true. Read it carefully before you react to it.

> **Exhibit — AI-generated answer, verbatim:**
>
> "Textbook-secure cryptography can still fail in real systems mainly because of insufficient
> key length and outdated algorithm choices. As computing power increases, keys that were once
> considered secure — such as 56-bit DES keys or 1024-bit RSA moduli — become feasible to break
> through brute-force or improved factoring techniques. This is why standards bodies like NIST
> periodically revise their minimum recommended key sizes and deprecate older algorithms such as
> SHA-1 and DES in favor of SHA-256/SHA-3 and AES.
>
> A well-designed system should therefore always use current, NIST-recommended key lengths and
> algorithms: AES-256 instead of AES-128 where very long-term secrecy is needed, RSA-3072 or
> higher instead of RSA-1024, and SHA-256 or better instead of SHA-1 or MD5. As long as an
> organization keeps its cryptographic library up to date and follows current key-length
> guidance, it can be confident that its use of cryptography is secure, since the underlying
> math has been extensively peer-reviewed and no practical attack against these primitives at
> current recommended sizes is known.
>
> In summary: cryptographic failures in practice are usually a symptom of organizations being
> slow to upgrade to modern key sizes and algorithms. Staying current with NIST and industry
> guidance on algorithm and key-length selection is the primary defense against real-world
> cryptographic failure."

**Task.**

1. Identify what the answer gets **right**. (It is not wrong about anything it says — this is
   the trap. Say specifically what's correct and why a shallow reviewer would accept the whole
   answer on this basis.)
2. Identify the **gap**: what category (or categories) of real-world cryptographic failure does
   this answer entirely omit, despite the question asking generally "why does textbook-secure
   crypto fail in real systems" (not "why do key lengths become insecure")? Be specific — name
   the missing categories, not just "it's incomplete."
3. For **each** missing category you name, give one concrete real or realistic example showing
   a system that used current, correctly-sized, unbroken primitives and still failed. (You may
   reuse your Q2 answer if it fits one of the categories, but you need at least two more
   distinct examples covering different categories.)
4. Rewrite the answer's **final paragraph only** (the "In summary" paragraph) so that it
   accurately reflects the full scope of why textbook-secure crypto fails in practice. Keep it
   to 3–5 sentences — the goal is a correct, complete summary, not a longer one.

**Submit:** your answers to 1–4, inline in this worksheet.

## Part 4 — Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** A non-technical manager asks you: *"We use AES-256 and
RSA-4096 everywhere — the biggest, strongest algorithms available. Doesn't that mean we're
safe?"* In 3–5 sentences, with no jargon (no "nonce," "side channel," "AEAD" — explain the
*idea*, not the vocabulary), explain why algorithm strength alone doesn't answer the question,
and what else determines whether the system is actually safe. A good answer should make sense
to someone who has never taken a cryptography course.

**B. Prompt Problem.** Write a **single prompt** that asks an AI assistant to produce a
checklist a development team could use to review a system's cryptography *beyond* algorithm and
key-length selection — i.e. a checklist that would have caught the gap you identified in Part 3.
Run it, then critique the result:

- Does it cover **key management** specifically (generation, storage, rotation, revocation,
  where keys live relative to the data they protect)?
- Does it cover **randomness/entropy sources** (not just "use a CSPRNG" as a slogan, but what
  can go wrong if the source is predictable or reused)?
- Does it cover **protocol/composition misuse** (using a sound primitive in the wrong mode, the
  wrong order, or without the complementary primitive it depends on — e.g. encryption without
  integrity)?
- Does it cover **side channels** (timing, error-message content, cache behavior) as a distinct
  category from "the algorithm is broken"?
- Does it hand-wave, over-generalize, or silently omit any of the above the way this week's
  Exhibit did?

**Submit:** your exact prompt, the AI's full response, and a bullet-by-bullet critique against
the checklist above (mark each item correct / incorrect / hand-waved, quoting the specific line
you're pointing at).

## Part 5 — Viva Spot-Check (instructor-run, live)

Be ready to answer these live, in your own words, with no notes:

1. If a system uses AES-256 and RSA-4096 (both far beyond any known practical attack) and is
   still compromised, what does that tell you about where security actually lives in a
   cryptographic system?
2. Give one example — from this worksheet or from your own reasoning — of a security failure
   that a bigger key size would do **nothing** to prevent. Why not?
3. This week's Exhibit answer was not wrong about anything it said. Why is "everything it said
   is true" not the same as "the answer is complete and safe to act on"?

## Grading rubric (100)

| Criterion | Points |
|---|---|
| Conventional arm — 6 short-answer questions (Part 2) | 30 |
| Audit-the-AI — what's right + the gap + examples + rewritten summary (Part 3) | 35 |
| EiPE (Part 4A) | 10 |
| Prompt Problem (Part 4B) | 15 |
| Viva spot-check (Part 5, instructor-run) | 10 |

See the instructor answer key (instructor use only, not in this file) for detailed Audit-the-AI
rubric bands (full/partial/no credit) and expected-answer notes for the viva.

---

## Evidence & Integrity (required)

- **Identity proof:** put your name/student ID and the date on every file you submit (Part 1).
- **No personalized flag this week** — this is a Conceptual week, graded entirely on your
  written reasoning and viva performance. See the README for why a CTF-style wrapper isn't
  used for {{ slot_label }}.
- **Explain in your own words** *(graded on your reasoning, not copied text)*: for the
  Audit-the-AI task specifically, restate in 1–2 sentences why the Exhibit's gap matters in
  practice — i.e. what a team that internalized only the Exhibit's advice would still be
  exposed to.
