# Worksheet 1 — Security Mindset & Threat-Modeling a Cryptographic System

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** NIST FIPS 140-3 · OWASP Cryptographic Storage Cheat Sheet · CWE-320, CWE-330
> **Kind:** Conceptual, step by step. No Docker, no Terminal, no flag this week. You think about a small system, draw it, and run one short simulation in your browser. Grading is rubric-based (see below).

> **Ethics note:** The simulation runs only in your own browser and only on made-up keys. The lesson is "who can see what, and what can go wrong". Never try to break into a real system that is not yours and without permission.

## Read this first

**What you will do today:** A system can use the strongest algorithms in the world and still be unsafe. Today you look at a small notes app and ask four questions: **who can read the notes, who can see the key, what could go wrong, and what do our protections not fix?** Then you run a short simulation that cracks a key that was "never really random", to see one real reason why strong algorithms are not enough.

**Every step is written the same way:**

| Heading | Meaning |
|---|---|
| **What to do** | Says what this step asks you to do |
| **You should see** | What the screen or your own answer should roughly look like (only where there is something to see) |
| **Means** | What the result means |
| **Write in the answer sheet** | What to type, draw or paste in your answer sheet |

**Marks**

- Everyone does **Part A (60 marks)**, which is the same for both forms.
- Then do **only your own form (40 marks)**. Look at the last digit of your student ID: **odd = Conventional (Part 2)**, **even = AIR-Sec (Parts 3–4)** (0 counts as even). Write your form in the Group box.
- You may answer in English or Thai. Short and clear is enough.
- **Answer sheet:** in Classroom → Week 01, open the file for your form (`Wk01_Answer_Sheet_Conventional` or `Wk01_Answer_Sheet_AIR-Sec`), choose Open with → Google Docs, type in the grey boxes, add your picture and screenshot, then choose File → Download → PDF.
- No Docker and no flag this week. Submit one file named with your student ID, for example `Wk01_66990000.pdf` (do not type the `<` `>` signs), at `learn.zcr.ai/submit` with your Week 1 submission code from your KMITL email, by **Sunday 8 Nov 2026, 23:59**.
- Already started the earlier version of this worksheet? That work also gets full credit.
- This is a **warm-up week**: both 40-mark forms are short. The older, harder questions are kept at the end of Part 2 as optional reading (no marks).

| Part A | Marks | Steps to write in the answer sheet |
|---|---:|---|
| A1 — Who sees what | 20 | Steps 2, 3, 4 (the table 10 + the picture 10; Step 2 has no separate marks) |
| A2 — Risks and controls | 20 | Steps 6, 7 (10 each) |
| A3 — Hands-on: crack a weak key | 20 | Steps 9, 10 (screenshot 8 + three short answers 4 each) |

**Words you need to know**

| Word | Simple meaning |
|---|---|
| plaintext | The readable data you want to protect |
| ciphertext | The scrambled version of the data. It is useless without the right key |
| key | The secret value that locks and unlocks the data |
| trust boundary | A place where data or a key passes to someone who has different control over it (for example from your browser to a server) |
| control | Something we do to reduce a risk (for example "keep the key in a separate store") |
| assumption | Something that must stay true for the control to work (for example "only two people can open the key store") |
| seed | The starting number that a program uses to make a "random" key. If the seed is easy to guess, the key is easy to find |
| brute force | Trying every possible candidate, one after another, until one works |
| commitment | A short fingerprint of a secret. It lets you check a guess without seeing the secret |

**Questions people often ask**

- *Do I need to be good at maths?* No. There is no maths this week.
- *Do I need to install anything or write programs?* No. You only need Google Docs and a browser.
- *Can I draw by hand?* Yes. A photo of a hand drawing is fine. You can also use any drawing tool.
- *Can I use my phone for the simulation?* Yes. A phone or a laptop both work.
- *My number of candidates and time are not the same as my friend's. Is that wrong?* No. The secret seed is random every time. Only the shape of the result must be the same.
- *How do I copy a screenshot into the answer sheet?* Take the screenshot, then in Google Docs choose Insert → Image and pick the picture (on a phone you can use the Docs app and Insert → Image).

**If you see a message or a problem like this**

| What you see | Cause | Fix |
|---|---|---|
| The simulation page is empty or the buttons do nothing | The page did not finish loading | Reload the page. If it still fails, try a laptop or another browser |
| There is no `KEY RECOVERED` line after you press the button | The search range was moved below the hidden seed | Move the search range back to the full range (the default) and press **Run the brute force** again |
| You cannot find where to paste the picture | You are not in Google Docs | In Classroom choose Open with → Google Docs, then Insert → Image |

If you still cannot do it, ask a friend or your instructor.

---

## Before you start: get ready (at home, once)

You do not need to install anything this week. The three steps below take about five minutes.

#### Prep step 1 — Open your answer sheet

**What to do:** In Classroom open **Week 01** and click the answer sheet for **your form** (`Wk01_Answer_Sheet_Conventional` if your student ID ends in an odd digit, `Wk01_Answer_Sheet_AIR-Sec` if it ends in an even digit or 0). Choose **Open with → Google Docs**.

**You should see:** a document called **Worksheet 1 — Answer sheet** with grey boxes to type in. Nothing to write yet.

#### Prep step 2 — Check that the simulation opens

**What to do:** On your phone or laptop, open <https://learn.zcr.ai/sim/seed-crack>. Do not press anything yet.

**You should see:** the title **Crack the key that was never really random**, three buttons called **TLS host key**, **Session token** and **Password-reset link**, and a button called **Run the brute force**.

#### Prep step 3 — Get something to draw with

**What to do:** Take a blank sheet of paper and a pen (or open any drawing tool). In Step 4 you draw five boxes and some arrows. A photo of your drawing is fine.

---

## Part A — Common work (both forms, 60 marks)

Work from top to bottom, **one step at a time, and do not skip steps.** Keep two windows open side by side: this worksheet (or the answer sheet) and a blank page for notes. Every step has the same parts: **What to do → What you should see → Write in the answer sheet**.

**The case** (a teaching scenario, not a real service): a small web app lets signed-in users store private notes.

- The browser talks to the app server over HTTPS (TLS).
- The app server reads the notes so it can show them.
- The note database is encrypted with a key that the app manages.
- Encrypted backups go to an operations (ops) team, which also keeps a way to recover the key.

### A1 — Who sees what? (20 marks)

#### Step 1 — Read: the case

**What to do:** Just read. You do not need to write anything.

Read **The case** above once more, slowly. Notice five parts: the **user's browser**, the **app server**, the **note database** (the file on disk), the **key store** (where the key is kept) and the **backup / ops team**. In the next steps you decide, for each part, whether it can see the plaintext notes and whether it can see or use the key.

#### Step 2 — Think: why does encrypting the database not hide the notes from the app server?

**What to do:** Read the question and answer it in 1–2 sentences. This step has no separate marks; it helps you with Step 3.

> *Hint:* encrypting the database does **not** hide the notes from the app server. Why not? Think about how the app server can show a note on the screen.

**Write in the answer sheet (Step 2):** one or two sentences. Start with: *The app server can still read the notes because ...*

#### Step 3 — Fill in the table (10 marks)

**What to do:** For each of the five parts, write **Yes** or **No** in each of the two columns, with a short reason where it helps.

| Component | Can it see the plaintext notes? | Can it see or use the key? |
|---|---|---|
| User's browser | | |
| App server | | |
| Note database (on disk) | | |
| Key store | | |
| Backup / ops team | | |

**You should see:** a table with five rows and two columns that you have filled in completely. Do the **Backup / ops team** row last: remember that ops also keeps a way to recover the key.

**Write in the answer sheet (Step 3):** the filled-in table (type Yes or No and a few words of reason in each box).

#### Step 4 — Draw the picture with two trust boundaries (10 marks)

**What to do:** Draw a simple box-and-arrow picture of the same five parts. Put an arrow for each place where data or a key moves. Then mark **two trust boundaries** (places where data or a key passes to someone with different control), for example with a dashed line and the words *trust boundary*.

**You should see:** five boxes, arrows that show which way the notes or the key move, and two clearly marked trust boundaries. A neat picture is not required; the boundaries and the arrow directions must be easy to read.

**Write in the answer sheet (Step 4):** your picture (a photo of your drawing is fine: Insert → Image).

### A2 — Risks and controls (20 marks)

#### Step 5 — Read: how to read the risk table

**What to do:** Just read. You do not need to write anything.

The risk table has four columns. **Risk** says what goes wrong. **Control** says what we do about it. **Assumption** says what must stay true for the control to work. **Still left** says what the control does not fix. Row 1 is done for you:

| Risk (what goes wrong) | Control (what we do) | Assumption (what must stay true) | Still left (what it does not fix) |
|---|---|---|---|
| Backups and the key both go to the ops team, so one leak exposes every note | Keep the key in a separate key store; ops get the backups but not the key | Access to the key store is limited and logged | If the key is lost, the backups cannot be restored |

#### Step 6 — Write your first row (10 marks)

**What to do:** An attacker breaks into the **app server**. What can they read? Write one row of the table for this risk, filling in all four columns.

**You should see:** one row with four non-empty boxes. The **Still left** box must name a real limit or cost, not "nothing".

**Write in the answer sheet (Step 6):** your four boxes for row 2 of the table.

#### Step 7 — Write your second row (10 marks)

**What to do:** Choose a **different** risk and write one more row with all four columns. A row that repeats row 1 earns no marks. Ideas: someone on the ops team misuses the key-recovery path; someone listens to traffic on public Wi-Fi.

**You should see:** one more complete row that is clearly about a different risk.

**Write in the answer sheet (Step 7):** your four boxes for row 3 of the table.

### A3 — Hands-on: crack a key that was never really random (20 marks)

#### Step 8 — Open the simulation and choose a target

**What to do:**

1. On your phone or laptop open <https://learn.zcr.ai/sim/seed-crack>.
2. Choose one target: **TLS host key**, **Session token** or **Password-reset link**.
3. Look at the line that starts with `seed source =`. It tells you where the "random" seed came from.
4. Leave the search range at its default (the full range of that target).

**You should see:** the target's name, a line such as `seed source = process ID (PID)  (real range: 32,768 possible values)` (the source and the range depend on the target), and the number of candidates it will try. Nothing to write yet.

#### Step 9 — Run the brute force and take a screenshot (8 marks)

**What to do:** Press **Run the brute force**. Wait a moment. Then take a **screenshot** that shows both the line `✓ KEY RECOVERED` and the line that starts with `tried`.

**You should see:** lines like these (the numbers change every time):

```
tried 5,643 candidates in 0.6 ms (~5,643,000 candidates/sec, this browser tab, no special hardware)
✓ KEY RECOVERED — seed 5642 reproduces the exact published commitment.
```

**Means:** the browser found the exact key by trying only a few thousand candidates, although the design assumed 2^128 possible keys.

**Write in the answer sheet (Step 9):** your screenshot (Insert → Image), then type the number of candidates and the time from **your own** screenshot.

#### Step 10 — Answer three short questions (4 marks each)

**What to do:** Answer each in 1–2 sentences, in your own words.

- **a.** How many candidates did your browser try, and how long did it take? (Copy the numbers from your own screenshot.)
- **b.** The design assumed 2^128 possible keys. Why did the attacker only need to try so few?
- **c.** What went wrong here: the algorithm, the key length, or the randomness? Explain.

*Real case:* the Debian OpenSSL bug (2008) left only about 32,768 possible keys.

**Write in the answer sheet (Step 10):** three answers, one box each (a, b, c).

#### Step 11 — Check your answer sheet before you go on

**What to do:** Look at your answer sheet and check that you have something in every box for Steps 2, 3, 4 (A1), Steps 6, 7 (A2) and Steps 9, 10 (A3). Then do the part for your own form: odd IDs do Part 2; even IDs do Parts 3 and 4.

---

## Part 1 — Student Information

| Name | Student ID | Date | Group (your form) | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

*Disclose any AI assistance used anywhere in this worksheet here (tool + what you asked it).*

---

## Part 2 — Conventional form (40 marks; only if Conventional is your assigned form): Warm-up questions

Answer in your own words, in Thai or English. Two to four sentences each is enough; this week's slides cover everything you need.

**Q1 (10). The basic words.** Answer both of these (1–2 sentences each):

- What are **plaintext**, **ciphertext** and a **key**?
- Explain Kerckhoffs' principle in one or two sentences: why is it fine for the algorithm to be public?

**Q2 (10). Symmetric and asymmetric.** Answer all three of these (1–2 sentences each):

- Give one difference between **symmetric** and **asymmetric** encryption.
- Give one example algorithm of each.
- Why does HTTPS use both?

**Q3 (10). The right tool for each job.** Pick the right tool for each job — **encryption**, **hash**, **MAC**, **digital signature** or **slow password KDF** — and give a one-line reason:

- a. Keep a file secret on a laptop.
- b. Check that a downloaded file was not corrupted.
- c. Prove an API request came from our own server, which shares a secret key with us.
- d. Prove a software update really came from the vendor.
- e. Store users' passwords in a database.

**Q4 (10). "Encrypted means nobody can change it".** A developer says: *"The data is encrypted, so nobody can change it."* Answer both of these (1–2 sentences each):

- What is wrong with this claim?
- Which tool would let you **detect** a change?

### Going further (optional — no marks)

- What exactly does "cryptographically secure" promise, and what does it *not* promise about the system around it?
- Find a real incident where a sound primitive was used and the system still failed (cite your source).
- Name three places in a web app where key material crosses a trust boundary, and what can go wrong at each.
- Pick two later weeks from this week's README table and guess what real-system mistake each will show.

## Part 3 — AIR-Sec form: Audit the AI (AIR-Sec only, 20 marks)

AI is a power tool you must **distrust** — you are graded on your *critique*, not on agreeing or disagreeing wholesale with the AI. This week's Audit-the-AI target is not code (no primitive has been introduced yet); it is a piece of confident, professionally-worded **prose** that has exactly one systematic, load-bearing gap.

**Setup.** Below is a real answer an AI assistant gave when asked: *"Why does textbook-secure cryptography fail in real systems?"* It is well-written, uses correct terminology throughout, and every individual factual claim in it is true. Read it carefully before you react to it.

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
2. **(10)** The question was "why does textbook-secure crypto fail in real systems?" Name **at least one** big area of real-world failure that the answer never mentions, and give **one** real or realistic example of it.
3. **(5)** Rewrite the answer's **final paragraph only** (the "In summary" paragraph) in 2–3 sentences so that it is complete.

**Submit:** your answers to 1–3 in your answer sheet PDF.

---

## Part 4 — Comprehension & Prompt (AIR-Sec only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** A non-technical manager asks you: *"We use AES-256 and RSA-4096 everywhere — the biggest, strongest algorithms available. Doesn't that mean we're safe?"* In 3–5 sentences, with no jargon (no "nonce," "side channel," "AEAD" — explain the *idea*, not the vocabulary), explain why algorithm strength alone doesn't answer the question, and what else determines whether the system is actually safe. A good answer should make sense to someone who has never taken a cryptography course.

**B. Prompt Problem (10).** Write **one prompt** that asks an AI assistant for a checklist a team could use to review a system's cryptography *beyond* algorithm and key-length choice. Run it, paste the AI's answer, then mark **Yes** or **No** for whether the answer covers each of these:

- key management (where keys live, rotation, recovery)
- randomness (where keys and nonces come from)
- protocol misuse (wrong mode, reused nonce, encryption without integrity)
- side channels (timing, error messages)

Finish with **one** thing the AI missed or explained too vaguely.

**Submit:** your prompt, the AI's answer, your Yes/No marks and your one comment.

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

Be ready to answer these live, in your own words, with no notes:

1. If a system uses AES-256 and RSA-4096 (both far beyond any known practical attack) and is still compromised, what does that tell you about where security actually lives in a cryptographic system?
2. Give one example — from this worksheet or from your own reasoning — of a security failure that a bigger key size would do **nothing** to prevent. Why not?

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — Who sees what (core analysis) | 20 | 20 |
| A2 — Risks and controls (controls and limitations) | 20 | 20 |
| A3 — Hands-on evidence and reasoning | 20 | 20 |
| Conventional warm-up questions (Q1–Q4, 10 each) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- **Identity proof:** put your name/student ID and the date on every file you submit (Part 1).
- **No personalized flag this week** — this is a Conceptual week, graded on the shared threat-model analysis and the assigned assessment format. Viva is formative feedback. See the README for why a CTF-style wrapper isn't
  used for {{ slot_label }}.
- **Explain in your own words** (marks are given for the reasoning): the picture, the table and the written answers must be your own work. The numbers in your simulation screenshot are random and will differ from a friend's; that is normal. Do not submit a friend's screenshot as your own.

**Deadline and late submission:** Submit by 23:59 (Thai time) on **Sunday 8 Nov 2026** (KOSEN rule: before the next class). Late uploads close on Wednesday 18 Nov 2026, 23:59. Late work loses 10% of this worksheet's marks for each day late (a part day counts as a day), down to 0. Uploading or replacing a file after the deadline counts the whole submission as late. Submit the common 60 marks and **one** form of your own only; doing both forms gives no extra marks. The viva checks your understanding and has no separate marks or automatic-zero rule. Grade the demonstrated work against the published criteria.
