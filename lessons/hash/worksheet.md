# Worksheet 2 — Hash Functions: Cracking a Leaked Password Database (100-minute class + preparation/extension)

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Cracking game:** "Crack the Leaked DB" (recover the admin password from a leaked, unsalted
> MD5 store, then show a bcrypt store resists the same fast attack)

> **Ethics note:** Crack only the hashes shipped in this lab (`users_vulnerable.csv`,
> `wordlist.txt`) on the two local containers this lab spins up (`vulnerable_app.py` /
> `fixed_app.py`, ports 8094/8095). Cracking password hashes for accounts or systems you don't
> own and aren't authorized to test is illegal. Keep recovered passwords and your flag inside
> this lab environment.

## How to use this worksheet — 100-minute class, two versions

Everyone completes the **same common activity (60 points)**. Complete only the
**Conventional written assessment (40)** or the **AIR-Sec assessment (40)** assigned
by the instructor. AIR-Sec's 40 points are Audit the AI 20, EiPE 10 and Prompt Problem 10.
Each version totals **100**, and neither version requires the other format for marks.

| Common criterion | Points | This week's evidence |
|---|---:|---|
| Core activity / analysis | 20 | Recover the admin password from the supplied MD5 store and demonstrate the login/session flow. |
| Control comparison and limitations | 20 | Compare the bcrypt store and verification code; explain salting, work factor and why a weak password remains guessable. |
| Evidence and causal reasoning | 20 | Record the crack, session/no-session controls, fixed-store comparison and your explanation of what those observations do and do not prove. |

**Before class:** complete the stated reading and any environment setup; software
installation and first image downloads are preparation, not extra contact minutes.
**In class (100 minutes):** 10 quiz/review + 10 brief + 60 shared practice/analysis +
15 debrief + 5 evidence capture. In Week 1 the opening block is orientation/review,
not a quiz on material not yet taught. The detailed tasks below are a checklist, not
additional timed class blocks: work through the core observations in the guided practice,
draft the explanation in the debrief, then finish detailed calculations/write-up and the
assigned 40-point format before the published deadline. Keep every original question;
unassigned-format questions and the labelled appendix are study extensions.

## Part 1 — Student Information
| Name | Student ID | Date | Group | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

## Part 2 — Conventional assessment (assigned version, 40 points): Written Questions

Answer each in your own words (4–8 sentences, more where the question asks for a design). This is
a normal written/essay task — **no AI-resilience layer applies to this part; answer it
yourself.** Cite a source where you make a factual claim (e.g. a broken-hash CVE or a NIST/OWASP
recommendation).

**Q1. Three resistance properties.** Distinguish **preimage resistance**, **second-preimage
resistance**, and **collision resistance**. For each, give one concrete attack it prevents.

**Q2. Broken hashes — and *where* it matters.** Why are MD5 and SHA-1 considered *broken*? Does
that brokenness matter *differently* for **password storage** vs. **digital signatures**?
Explain (hint: which property is broken, and which property does each use actually rely on).

**Q3. Fast hash vs. slow KDF.** Why is a fast hash like SHA-256 a *poor* choice for storing
passwords, and why is a slow KDF (bcrypt / argon2 / scrypt) better? What does the **cost / work
factor** control, and who does raising it hurt more — the defender or the attacker?

**Q4. Salt.** What is a **salt**? What specific attack does a *per-user random* salt defeat, and
why does the salt **not** need to be kept secret? (What breaks if the salt is reused across
users, or is a constant?)

**Q5. Rainbow tables.** What is a **rainbow table**, and why does per-user salting make a
*precomputed* rainbow table useless? (What would an attacker have to precompute *instead*, and
why is that infeasible at scale?)

**Q6. Unsalted SHA-256 leak.** A developer stores `SHA-256(password)` with no salt. An attacker
leaks the hash database. What can the attacker do, step by step? Roughly how long do *common*
passwords survive, and why does using SHA-256 instead of MD5 barely help here?

**Q7. Hash vs MAC vs encryption — one sentence each.** State the *one* security property that a
plain **hash**, a **MAC**, and **encryption** each provide. (Be precise: which gives integrity
only, which gives integrity + authenticity, which gives confidentiality?)

**Q8. Pepper.** What is a **pepper**, where is it stored (and how does that differ from a salt),
and what threat does a pepper address that a salt does **not**?

---

## Part 3 — Shared common practice (both versions, 60 points)

**Learning goals:** crack a leaked unsalted-MD5 password store with an offline dictionary
attack, capture the admin flag, then verify a bcrypt store resists the same fast technique — the
*practical* twin of Part 2's Q3/Q6.
**Prerequisites:** Docker; Python 3 with the `requests` package on the host to run
`exploit.py`.

**Environment setup**
```bash
cd {{ labpath }}
docker compose up -d        # vulnerable_app.py on :8094, fixed_app.py on :8095
curl localhost:8094/        # confirm it's up
```

**Task 0 — Onboarding.** *Goal:* see the vulnerable store. *Steps:* open
`users_vulnerable.csv` and `vulnerable_app.py`; find the exact line in `/login` that checks the
password and confirm it is `hashlib.md5(password.encode()).hexdigest() == stored` (fast, no
salt). *Deliverable:* quote that line and state which of Q3/Q6's failure modes it matches.

**Task 1 — Crack the admin hash by hand-ish.** *Goal:* recover the admin password
*yourself*, not just by running the script. *Steps:* read the `admin` row's md5 from
`users_vulnerable.csv`; then in a Python REPL, loop over `wordlist.txt` computing
`hashlib.md5(word.encode()).hexdigest()` until one equals the admin hash. (You may also confirm
with a tool: `hashcat -m 0` or `john --format=raw-md5` against a one-line hash file — either is
fine.) *Deliverable:* the recovered plaintext + the ~time it took + one line on *why* it was so
fast (fast primitive + unsalted, so a single precomputed table covers every row — CWE-916/759).

**Task 2 — Log in and capture the flag.** *Goal:* turn the cracked password into the
flag. *Steps:* `exploit.py` already does this, but reproduce it manually so you understand the
**session**: log in, *keeping the cookie jar*, then hit `/admin` with the same jar:
```bash
JAR=$(mktemp)
curl -s -c "$JAR" -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"<recovered>"}' localhost:8094/login
curl -s -b "$JAR" localhost:8094/admin      # -> {"flag": ...}
```
Now try `GET /admin` *without* `-b "$JAR"` and confirm you get `403`. *Deliverable:* the flag +
your two curl outputs (with-jar → flag, without-jar → 403), and one sentence on why the session
cookie is required (`exploit.py` uses a single `requests.Session()` for exactly this reason).

**Task 3 — Run the full exploit.** *Goal:* confirm the scripted end-to-end run.
*Steps:* `python exploit.py`; note the two `PASS` lines and exit code 0. *Deliverable:* the full
script output pasted into your write-up.

**Task 4 — Confirm bcrypt resists the fast technique.** *Goal:* prove the fix works,
not just claim it. *Steps:* open `users_fixed.csv` — note the stored hashes start with `$2b$`
(bcrypt), embed a per-user salt, and differ even for users who might share a password. In a REPL,
build the md5 table over `wordlist.txt` again and confirm it matches **none** of the bcrypt
strings (they aren't md5 hex). Read `fixed_app.py`'s `/login` and identify the one-line change
from `vulnerable_app.py` (`bcrypt.checkpw` vs. `md5(...) ==`). *Deliverable:* the "0 matches"
result + the one-line diff (in words) between the two `/login` password checks.

**Task 5 — Explain the cost, precisely.** *Goal:* connect the exploit to the theory —
and don't overclaim. *Steps:* answer in your own words: (a) Why did *one* precomputed md5 table
crack every row of the vulnerable store at once, while it cracks *zero* rows of the bcrypt store?
(b) The admin password `sunshine2021` **is** in the wordlist — so could a patient attacker still
recover it from the bcrypt store, and if so what stops that being cheap? (c) If bcrypt doesn't
make a weak password safe, what *second* control does (name it, and say what it changes about the
attacker's search)? *Deliverable:* 3 short paragraphs, one per sub-question.

---

## Evidence & Integrity (required)

- **Evidence attribution (the same for both versions):** put your name/student ID and
  date on the worksheet, and capture your own commands and results. Make clear which run
  each observation came from. A terminal timestamp or identity stamp is optional context,
  not an extra scored personal artifact. If evidence is unclear, the instructor may request
  clarification within the common evidence/reasoning criterion.
- **Runtime flag (where this lab returns one):** record the value from your own run. Use a
  personalised configuration only if the instructor supplies it; otherwise the shared demo
  flag is acceptable with your own evidence and reasoning. No automatic roster/flag validation
  is assumed. Do not submit a classmate's capture as your own.
- Optional context stamp: `printf '%s | %s | ' "$(whoami)" '<YOUR-STUDENT-ID>'; date '+%F %T %Z'`.
  You may include this with a terminal/browser capture if useful. A separate terminal or
  whole-screen identity capture is not required; legible own commands/results and the
  worksheet name/student ID are sufficient. All common evidence is within the common 60.
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the crack work** (why did the MD5 store fall in ms)?
  2. **Why does the bcrypt fix actually stop the fast attack** — and what could still break it
     (i.e. what is bcrypt *not* protecting you from)?

---

## 🤖 Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's
answer.

Below is an AI assistant's answer to *"Write a secure `store_password` / `verify_password` for a
web app."* It looks professional, imports a real crypto library, and even mentions salting — but
it has **at least one subtly serious flaw**. Your job: find it.

> **AI's answer:**
>
> "Here's a secure password storage helper. We use SHA-256 (a strong, modern cryptographic hash)
> together with a salt so that identical passwords don't produce identical hashes.
>
> ```python
> import hashlib
>
> # A random-looking salt so rainbow tables don't work.
> SALT = "s3cr3t_salt_v1"
>
> def store_password(password: str) -> str:
>     # SHA-256 is collision-resistant and fast, so verification is efficient.
>     return hashlib.sha256((SALT + password).encode()).hexdigest()
>
> def verify_password(password: str, stored: str) -> bool:
>     return store_password(password) == stored
> ```
>
> This is secure because SHA-256 is a cryptographically strong hash, the salt defeats rainbow
> tables, and because SHA-256 is fast, login checks stay quick even under heavy load. To make it
> even stronger you could switch to SHA-512."

1. **Find what's wrong or risky.** There is more than one problem — quote the exact line(s) for
   each. (Hints, so you don't waste the critique on the wrong thing: yes, *some* hash is used and
   *a* salt is present — the question is whether this is the *right kind* of hash for passwords,
   and whether this is a *real* salt in the sense Q4 means. Also look hard at the sentence that
   treats "SHA-256 is fast" as a *benefit*.)
2. **Produce the correct, verified version yourself.** Rewrite `store_password` /
   `verify_password` using a proper password KDF (bcrypt or argon2id) with a **per-user random**
   salt and a constant-time verify, and explain in 2–3 sentences why the AI's version was
   insufficient *even though it hashes and even though it has "a salt."*

> Disclose your AI use (if any, beyond this provided artifact) in the Part 1 table. This task
> counts toward the **Audit the AI** row of the grading rubric.

---

## 🧠 Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE).** A web developer says: *"I don't store plaintext — I store
`SHA-256(password)`, and SHA-256 has never been broken. So I'm fine, right?"* In 2–4 sentences,
explain to them why this is **not** enough — without leaning on jargon. Explain the *mechanism*:
what an attacker with the leaked hash file actually *does* (they don't "reverse" SHA-256 — they
*guess and hash*), why "SHA-256 isn't broken" is answering the wrong question, and what a slow,
salted KDF changes about the attacker's guessing.

**B. Prompt Problem.** Write a **single prompt** that asks an AI *how to securely store user
passwords in a web app*. Run it, then critique the AI's answer against what you now know:
- Does it recommend a **password KDF** (argon2id / bcrypt / scrypt) — or does it hand you a bare
  hash (SHA-256/SHA-512), or worse, MD5?
- Does it use a **per-user random salt** (and does it understand the salt can be stored
  alongside the hash, not kept secret)?
- Does it mention **work factor / cost tuning** and a **constant-time compare** — and does it
  *hallucinate* anything (a wrong API, a made-up "SHA-256 with salt is fine" claim, an invented
  function)?

Submit the **final prompt + the AI's answer + your critique** (3–5 sentences covering the three
bullet points above).

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "You cracked `admin` in milliseconds. If I added a **unique random salt per user** to the MD5
   store — same MD5, same wordlist — what *exactly* would change about your attack, and would you
   still crack `admin` eventually? What would change is the *cost* — explain."
2. "Show me two rows in `users_fixed.csv`. If two of those users happened to pick the *same*
   password, could you tell from the stored bcrypt hashes? Why or why not — and what property is
   that?"
3. "Point to the one line that differs between `vulnerable_app.py`'s and `fixed_app.py`'s
   `/login` password check, and explain in one sentence why that line alone defeats the
   *fast-dictionary* attack but does **not** by itself make a weak password safe."

---

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
