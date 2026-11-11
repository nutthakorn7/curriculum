# Worksheet 1 — Security Mindset & Threat-Modeling a Cryptographic System

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** NIST FIPS 140-3 · OWASP Cryptographic Storage Cheat Sheet · CWE-320, CWE-330
> **Kind:** Conceptual — no Docker target, no flag this week. Grading is rubric-based (see below).

## How to use this worksheet

- Everyone does **Part A (60 points)**. It is the same for both forms.
- Then do **only your form (40 points)**. The last digit of your student ID decides:
  **odd = Conventional (Part 2)**, **even = AIR-Sec (Parts 3–4)**. Write your form in the Group field.
- You may answer in Thai or English. Short, clear answers are fine.
- **Use the answer sheet.** In Classroom → Week 01, open the file for your form
  (`Wk01_Answer_Sheet_Conventional_odd_ID` or `Wk01_Answer_Sheet_AIR-Sec_even_ID`), type your
  answers in the grey boxes, add your picture and screenshot, then File → Download → PDF.
- No Docker and no flag this week. Hand in one PDF, `Wk01_<StudentID>.pdf`, at `learn.zcr.ai/submit`.
- Already started the earlier version of this worksheet? That work also gets full credit.
- This is a **warm-up week**: both 40-point forms are short. The older, harder questions are
  kept at the end of Part 2 as optional reading (no marks).

| Part A | Points | What you hand in |
|---|---:|---|
| A1 — Who sees what | 20 | The filled-in component table and a simple picture with two trust boundaries marked |
| A2 — Risks and controls | 20 | Two rows of the risk table |
| A3 — Hands-on: crack a weak key | 20 | A screenshot from the simulation and three short answers |

## Part A — Common work (both forms, 60 points)

**The case** (a teaching scenario, not a real service): a small web app lets signed-in users
store private notes.

- The browser talks to the app server over HTTPS (TLS).
- The app server reads the notes so it can show them.
- The note database is encrypted with a key that the app manages.
- Encrypted backups go to an operations (ops) team, which also keeps a way to recover the key.

### A1 — Who sees what? (20 points)

Fill in the table with **Yes** or **No**, plus a short reason where it helps.

| Component | Can it see the plaintext notes? | Can it see or use the key? |
|---|---|---|
| User's browser | | |
| App server | | |
| Note database (on disk) | | |
| Key store | | |
| Backup / ops team | | |

Then draw a simple box-and-arrow picture of these five parts and mark **two trust boundaries**
(places where data or a key passes to someone with different control). A photo of a hand drawing
is fine.

*Hint:* encrypting the database does **not** hide the notes from the app server. Why not?

### A2 — Risks and controls (20 points)

Row 1 is done for you. Write **two more rows**.

| Risk (what goes wrong) | Control (what we do) | Assumption (what must stay true) | Still left (what it does not fix) |
|---|---|---|---|
| Backups and the key both go to the ops team, so one leak exposes every note | Keep the key in a separate key store; ops get the backups but not the key | Access to the key store is limited and logged | If the key is lost, the backups cannot be restored |
| *your row* | | | |
| *your row* | | | |

*Hint for one row:* an attacker breaks into the app server. What can they read?

### A3 — Hands-on: crack a key that was never really random (20 points)

1. Open **<https://learn.zcr.ai/sim/seed-crack>** on a phone or laptop.
2. Pick a target (TLS host key, session token or password-reset link) and press
   **Run the brute force**.
3. Take a **screenshot** that shows **KEY RECOVERED** and how long it took.

Answer each in 1–2 sentences:

- **a.** How many candidates did your browser try, and how long did it take?
- **b.** The design assumed 2^128 possible keys. Why did the attacker only need to try so few?
- **c.** What went wrong here: the algorithm, the key length, or the randomness? Explain.

*Real case:* the Debian OpenSSL bug (2008) left only about 32,768 possible keys.

## Part 1 — Student Information

| Name | Student ID | Date | Group (your form: Conventional or AIR-Sec) |
|---|---|---|---|
| | | | |

*Disclose any AI assistance used anywhere in this worksheet here (tool + what you asked it).*

## Part 2 — Conventional form (40 points; only if Conventional is your assigned form): Warm-up questions

Answer in your own words, in Thai or English. Two to four sentences each is enough; this week's
slides cover everything you need.

**Q1 (10).** What are **plaintext**, **ciphertext** and a **key**? Then explain Kerckhoffs'
principle in one or two sentences: why is it fine for the algorithm to be public?

**Q2 (10).** Give one difference between **symmetric** and **asymmetric** encryption, and one
example algorithm of each. Why does HTTPS use both?

**Q3 (10).** Pick the right tool for each job — **encryption**, **hash**, **MAC**, **digital
signature** or **slow password KDF** — and give a one-line reason:

- a. Keep a file secret on a laptop.
- b. Check that a downloaded file was not corrupted.
- c. Prove an API request came from our own server, which shares a secret key with us.
- d. Prove a software update really came from the vendor.
- e. Store users' passwords in a database.

**Q4 (10).** A developer says: *"The data is encrypted, so nobody can change it."* What is
wrong with this claim? Which tool would let you **detect** a change?

### Going further (optional — no marks)

- What exactly does "cryptographically secure" promise, and what does it *not* promise about the
  system around it?
- Find a real incident where a sound primitive was used and the system still failed (cite your
  source).
- Name three places in a web app where key material crosses a trust boundary, and what can go
  wrong at each.
- Pick two later weeks from this week's README table and guess what real-system mistake each
  will show.

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

**Task.** Answer in Thai or English.

1. **(5)** Name **two** things the AI answer gets right.
2. **(10)** The question was "why does textbook-secure crypto fail in real systems?" Name **at
   least one** big area of real-world failure that the answer never mentions, and give **one**
   real or realistic example of it.
3. **(5)** Rewrite the answer's **final paragraph only** (the "In summary" paragraph) in 2–3
   sentences so that it is complete.

**Submit:** your answers to 1–3 in your worksheet PDF.

## Part 4 — Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE).** A non-technical manager asks you: *"We use AES-256 and
RSA-4096 everywhere — the biggest, strongest algorithms available. Doesn't that mean we're
safe?"* In 3–5 sentences, with no jargon (no "nonce," "side channel," "AEAD" — explain the
*idea*, not the vocabulary), explain why algorithm strength alone doesn't answer the question,
and what else determines whether the system is actually safe. A good answer should make sense
to someone who has never taken a cryptography course.

**B. Prompt Problem (10).** Write **one prompt** that asks an AI assistant for a checklist a
team could use to review a system's cryptography *beyond* algorithm and key-length choice. Run it,
paste the AI's answer, then mark **Yes** or **No** for whether the answer covers each of these:

- key management (where keys live, rotation, recovery)
- randomness (where keys and nonces come from)
- protocol misuse (wrong mode, reused nonce, encryption without integrity)
- side channels (timing, error messages)

Finish with **one** thing the AI missed or explained too vaguely.

**Submit:** your prompt, the AI's answer, your Yes/No marks and your one comment.

## Part 5 — Viva Spot-Check (formative/authenticity check; no separate points)

Be ready to answer these live, in your own words, with no notes:

1. If a system uses AES-256 and RSA-4096 (both far beyond any known practical attack) and is
   still compromised, what does that tell you about where security actually lives in a
   cryptographic system?
2. Give one example — from this worksheet or from your own reasoning — of a security failure
   that a bigger key size would do **nothing** to prevent. Why not?

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| Part A1 — Who sees what (core analysis) | 20 | 20 |
| Part A2 — Risks and controls (controls and limitations) | 20 | 20 |
| Part A3 — Hands-on evidence and reasoning | 20 | 20 |
| Conventional warm-up questions (Q1–Q4, 10 each) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

**Deadline and late work:** hand in by 23:59 Thai time (ICT) on the Sunday before the next week's
class (KOSEN rule); the exact date is in your codes email and in the week's Classroom post.
Late work loses 10% of this worksheet's score for each day late (a part day counts as a day), down to 0.
Uploading or replacing a file after the deadline makes the whole hand-in late.

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
