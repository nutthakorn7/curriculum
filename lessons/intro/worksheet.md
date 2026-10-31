# Worksheet 1 — Security Mindset & Threat-Modeling a Cryptographic System

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** NIST FIPS 140-3 · OWASP Cryptographic Storage Cheat Sheet · CWE-320, CWE-330
> **Kind:** Conceptual — no Docker target, no flag this week. Grading is rubric-based (see below).

## How to use this worksheet — 100-minute class, two versions

Everyone completes the **same common activity (60 points)**. Complete only the
**Conventional written assessment (40)** or the **AIR-Sec assessment (40)** assigned
by the instructor. AIR-Sec's 40 points are Audit the AI 20, EiPE 10 and Prompt Problem 10.
Each version totals **100**, and neither version requires the other format for marks.

| Common criterion | Points | This week's evidence |
|---|---:|---|
| Core activity / analysis | 20 | Threat-model the supplied small web application: identify assets, actors, data/key flows and trust boundaries. |
| Control comparison and limitations | 20 | Choose controls for two risks, state the trust assumptions, and explain a residual risk or limitation. |
| Evidence and causal reasoning | 20 | Submit a labelled diagram, a risk/control table and an explanation linking each conclusion to the stated case. |

**Before class:** complete the stated reading and any environment setup; software
installation and first image downloads are preparation, not extra contact minutes.
**In class (100 minutes):** 10 quiz/review + 10 brief + 60 shared practice/analysis +
15 debrief + 5 evidence capture. In Week 1 the opening block is orientation/review,
not a quiz on material not yet taught. The detailed tasks below are a checklist, not
additional timed class blocks: work through the core observations in the guided practice,
draft the explanation in the debrief, then finish detailed calculations/write-up and the
assigned 40-point format before the published deadline. Keep every original question;
unassigned-format questions and the labelled appendix are study extensions.

## Shared common activity — threat model (both versions, 60 points)

**Case for analysis (a teaching scenario, not a claim about a real service):** a small
web application lets signed-in users store private notes. A browser talks to an application
server over TLS. The server can read notes to display them, encrypts the note database with
an application-managed key, and sends encrypted database backups to an operations team.
The team must also keep a recovery path for the key. Do not assume that encrypting the
database hides notes from the application server.

1. Draw the browser, application, note database, key store and backup/recovery roles. Label
   where plaintext and keys are visible and where control/trust changes.
2. Identify the assets, an attacker and **two** concrete failure paths. For each path, name
   one control, the assumption it relies on, and one remaining risk or availability cost.
3. Submit your diagram and a table `risk -> control -> assumption -> residual limitation`,
   then explain why the controls address your selected paths. This is the common evidence;
   no Docker target, flag or invented runtime output is required.

## Part 1 — Student Information

| Name | Student ID | Date | Group |
|---|---|---|---|
| | | | |

*Disclose any AI assistance used anywhere in this worksheet here (tool + what you asked it).*

## Part 2 — Conventional assessment (assigned version, 40 points): Short-Answer Questions

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

## Part 3 — AIR-Sec Arm: Audit the AI (AIR-Sec version only, 20 points)

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

## Part 4 — Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

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

## Part 5 — Viva Spot-Check (formative/authenticity check; no separate points)

Be ready to answer these live, in your own words, with no notes:

1. If a system uses AES-256 and RSA-4096 (both far beyond any known practical attack) and is
   still compromised, what does that tell you about where security actually lives in a
   cryptographic system?
2. Give one example — from this worksheet or from your own reasoning — of a security failure
   that a bigger key size would do **nothing** to prevent. Why not?
3. This week's Exhibit answer was not wrong about anything it said. Why is "everything it said
   is true" not the same as "the answer is complete and safe to act on"?

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

**Deadline and late work:** hand in before the start of the next week's class session (KOSEN rule).
Late work loses 10% of this worksheet's score for each day late (a part day counts as a day), down to 0.

Submit the common work plus **one** assigned assessment format; do not add the two
format columns or complete both formats for extra marks. The original questions remain
available for study. A viva is a formative/authenticity check within the relevant criteria,
with feedback or a request to clarify/reproduce evidence; it has no separate points and
no automatic-zero rule. Grade the demonstrated work against the published criteria.


## Evidence & Integrity (required)

- **Identity proof:** put your name/student ID and the date on every file you submit (Part 1).
- **No personalized flag this week** — this is a Conceptual week, graded on the shared
  threat-model analysis and the assigned assessment format. Viva is formative feedback. See the README for why a CTF-style wrapper isn't
  used for {{ slot_label }}.
- **Explain in your own words** *(graded on your reasoning, not copied text)*: for the
  AIR-Sec Audit-the-AI task, when assigned, specifically, restate in 1–2 sentences why the Exhibit's gap matters in
  practice — i.e. what a team that internalized only the Exhibit's advice would still be
  exposed to.
