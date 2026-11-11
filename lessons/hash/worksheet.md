# Worksheet 2 — Hash Functions: Cracking a Leaked Password Database

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Kind:** Docker lab. You crack a leaked (sandbox) password file, capture a flag, then watch the
> same attack fail against a properly stored file.

> **Ethics note:** Crack only the hashes shipped in this lab (`users_vulnerable.csv`,
> `wordlist.txt`) on the two local containers it starts (ports 8094/8095). Cracking password
> hashes for accounts or systems you don't own and aren't authorized to test is illegal. Keep
> recovered passwords and your flag inside this lab.

## How to use this worksheet

- Everyone does **Part A (60 points)** — the guided lab. It is the same for both forms.
- Then do **only your form (40 points)**. The last digit of your student ID decides:
  **odd = Conventional (Part 2)**, **even = AIR-Sec (Parts 3–4)**. Write your form in the Group field.
- You may answer in Thai or English. Short, clear answers are fine.
- **Use the answer sheet.** In Classroom → Week 02, open the file for your form
  (`Wk02_Answer_Sheet_Conventional_odd_ID` or `Wk02_Answer_Sheet_AIR-Sec_even_ID`), type your
  answers in the grey boxes, paste your screenshots, then File → Download → PDF.
- Hand in one PDF, `Wk02_<StudentID>.pdf`, at `learn.zcr.ai/submit` by **Sun 15 Nov 23:59** (ICT).
- The core tasks are short and everyone can finish them in class. The questions marked
  *optional* are extra reading and carry no marks.

| Part A | Points | What you hand in |
|---|---:|---|
| A1 — Crack the leaked file | 20 | The `crack.py` output showing the recovered passwords |
| A2 — Log in and get the flag | 20 | Your `login.py` output (flag + the 403 with no cookie) |
| A3 — Show the fix works | 20 | The `exploit.py` output, and one or two sentences on why bcrypt stopped the attack |

## Before class (do this at home once)

You need **Docker** on your laptop. Nothing else — the scripts run *inside* the containers, so
you do **not** need Python installed on your own machine.

```bash
cd {{ labpath }}
docker compose up -d
```

The first run downloads an image and installs packages — that can take a few minutes. Wait until
the log says the servers are up:

```bash
docker compose logs vulnerable | grep "Running on"
# -> * Running on http://127.0.0.1:8094
```

If you cannot get Docker working in time, there is a **no-install fallback** in A1.

---

## Part A — The lab (both forms, 60 points)

A user database leaked. There are two copies of the same login service, with the **same** users
and passwords but **different** password storage:

| Service | Port | Stores passwords as | Should fall to a fast wordlist? |
|---|---|---|---|
| `vulnerable_app.py` | `:8094` | **MD5, no salt** (`users_vulnerable.csv`) | **Yes** |
| `fixed_app.py` | `:8095` | **bcrypt** — per-user salt + slow (`users_fixed.csv`) | **No** |

### A1 — Crack the leaked file (20 points)

The attacker already has the leaked file `users_vulnerable.csv` (rows of `username,md5hash`). They
never log in to get it — it is a stolen database dump. `crack.py` does the attack: it hashes every
word in `wordlist.txt` with MD5 and looks for a match.

Run it inside the container (no Python needed on your laptop):

```bash
docker compose exec vulnerable python crack.py
```

Expected output (your run should look like this):

```
Hashed 101 guesses with MD5 and checked 8 leaked rows in 0.09 ms
  admin  -> sunshine2021
  alice  -> password
  ...
Cracked 8 of 8 users with ONE list (no salt, so every row is checked at once)
```

**Deliverable:** paste your `crack.py` output. In one sentence, say why it was so fast — *fast
hash + no salt, so one list of hashed guesses checks every row at once.*

> **No-Docker fallback:** open **<https://learn.zcr.ai/sim/hash-crack>**, crack Store A, and
> screenshot the recovered password and the time. Use that screenshot in place of the output above.

### A2 — Log in as admin and get the flag (20 points)

Turn the cracked password into the flag. `login.py` logs in as `admin`, then asks the server for
the flag **on the same session**, and finally tries again with **no** session cookie:

```bash
docker compose exec vulnerable python login.py sunshine2021
```

Expected output:

```
1) POST /login as admin               -> 200 {'ok': True, 'user': 'admin'}
2) GET /admin, same session           -> 200 {'flag': 'FLAG{...}'}
3) GET /admin, new session, no cookie -> 403 {'error': 'forbidden -- log in as admin first'}
```

**Deliverable:** paste your output (the flag + the 403 line). In one sentence, say why the third
request was refused — *the flag needs the logged-in session cookie, which the fresh request didn't send.*

### A3 — Show the fix stops the same attack (20 points)

`exploit.py` runs the whole attack end to end against **both** services: it cracks the MD5 store
and grabs the flag, then runs the *same* fast technique against the **bcrypt** store.

```bash
docker compose exec vulnerable python exploit.py
```

Expected output ends with two `PASS` lines:

```
PASS: cracked admin login accepted by vulnerable app (:8094) -- flag = FLAG{...}
PASS: fixed store not crackable by the fast-dictionary technique (:8095) -- ... matched 0/8 bcrypt rows ...
```

**Deliverable:** paste the two `PASS` lines, then answer in 1–2 sentences each:

- **a.** Why did one list of hashed guesses crack the **whole** MD5 file at once?
- **b.** The same list matched **0** rows of the bcrypt file. Name the **two** things bcrypt adds
  (a per-user salt, and being slow) and say what each one does to the attacker.
- **c.** The admin's password `sunshine2021` is still in the wordlist. Could a patient attacker
  eventually recover it from the bcrypt file? What makes that expensive?

---

## Part 1 — Student Information
| Name | Student ID | Date | Group (your form) | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

## Part 2 — Conventional form (40 points; only if Conventional is your assigned form)

Answer in your own words (3–5 sentences each). This is a normal written task — **no AI-resilience
layer applies here; answer it yourself.**

**Q1 (10). What a hash promises.** Name three things a good hash function gives you (think:
fixed-size output, one-way, same input → same output, tiny change → very different output). Which
one is the reason we store the *hash* of a password instead of the password itself?

**Q2 (10). Why a fast hash is a poor way to store passwords.** An attacker steals a file of
`SHA-256(password)` values. They do **not** reverse the hash — explain what they do instead
("guess and hash"), and why a *fast* hash like MD5 or SHA-256 makes that cheap.

**Q3 (10). Salt.** What is a **salt**? Why does it have to be **different for each user**, and why
is it OK to store it right next to the hash (not secret)? What goes wrong if everyone shares the
same salt?

**Q4 (10). Slow password hash.** bcrypt / Argon2 are built to be **slow**, with a tunable *cost*.
Who does raising the cost hurt more — the real user logging in once, or the attacker making
billions of guesses? Explain why.

### Going further (optional — no marks)

- **Rainbow tables.** What is a rainbow table, and why does a per-user salt make a *precomputed*
  one useless?
- **Hash vs MAC vs encryption.** In one sentence each, what does a plain hash, a MAC, and
  encryption each give you?
- **Pepper.** What is a pepper, where is it kept (and how is that different from a salt), and what
  does it protect against that a salt does not?
- **Broken hashes.** MD5 and SHA-1 have practical *collision* attacks. Why does that matter a lot
  for digital signatures but barely at all for the password-cracking you did today?

---

## Part 3 — AIR-Sec Arm: Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

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
   and whether this is a *real* salt in the sense Q3 means. Also look hard at the sentence that
   treats "SHA-256 is fast" as a *benefit*.)
2. **Write the corrected version yourself.** Rewrite `store_password` / `verify_password` using a
   proper password hash (bcrypt or argon2id) with a **per-user random** salt, and explain in 2–3
   sentences why the AI's version was insufficient *even though it hashes and even though it has
   "a salt."*

> Disclose any other AI use in the Part 1 table. This task counts toward the **Audit the AI** row.

---

## Part 4 — Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** A web developer says: *"I don't store plaintext — I
store `SHA-256(password)`, and SHA-256 has never been broken. So I'm fine, right?"* In 2–4
sentences, and **without jargon**, explain why this isn't enough: what an attacker with the leaked
file actually does (they *guess and hash*, they don't "reverse" it), and what a slow, salted
password hash changes about that.

**B. Prompt Problem (10).** Write **one** prompt asking an AI *how to securely store user
passwords in a web app*. Run it, then check its answer against what you learned:
- Does it recommend a **password hash** (argon2id / bcrypt / scrypt) — or a bare SHA-256/MD5?
- Does it use a **per-user random salt** (and know the salt can sit next to the hash)?
- Does it mention a **cost / work factor** — and does it make anything up (a wrong function, a
  "SHA-256 with salt is fine" claim)?

Submit the **prompt + the AI's answer + your critique** (3–5 sentences).

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "You cracked `admin` in milliseconds. If every user got a **unique random salt** — same MD5,
   same wordlist — what would change about your attack, and would you still crack `admin`
   eventually? What changes is the *cost* — explain."
2. "Two users in `users_fixed.csv` might have chosen the same password. Can you tell from their
   stored bcrypt hashes? Why or why not?"
3. "Point to the one line that differs between `vulnerable_app.py` and `fixed_app.py` in the
   `/login` password check, and say in one sentence why that line defeats the *fast* attack but
   does **not** by itself make a weak password safe."

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — crack the leaked file | 20 | 20 |
| A2 — log in and get the flag | 20 | 20 |
| A3 — show the fix works + reasoning | 20 | 20 |
| Conventional written questions (Q1–Q4) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- Put your name/student ID and date on the worksheet, and capture your **own** commands and
  results. The shared demo flag is fine — no personal flag is needed this week. Don't submit a
  classmate's capture as your own.
- **Explain in your own words** (graded on your reasoning): why the MD5 store fell in
  milliseconds, and why the bcrypt store resisted the same attack.

**Deadline and late work:** hand in by 23:59 Thai time (ICT) on **Sun 15 Nov** (the Sunday before
the next class). Late work loses 10% of this worksheet's score per day (a part day counts as a
day), down to 0. Uploading or replacing a file after the deadline makes the whole hand-in late.
Submit the common work plus **one** assigned format; do not complete both for extra marks.
A viva is a formative/authenticity check with no separate points.
