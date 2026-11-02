# {{ slot_label }} — Hash Functions: Cracking a Leaked Password Database

**Kind:** LAB
**Concepts:** cryptographic hash functions, preimage/collision resistance, password storage,
salting, slow KDFs (bcrypt/argon2/scrypt), dictionary & rainbow-table attacks
**Analogous CWE:** CWE-916 (Use of Password Hash With Insufficient Computational Effort),
CWE-327 (Use of a Broken or Risky Cryptographic Algorithm), CWE-759/CWE-760 (Use of a One-Way
Hash Without a Salt / With a Predictable Salt)

## This week — 100-minute class and assigned assessment

1. **Before class** — install **Docker** and run `docker compose up -d` once at home (the first run
   downloads an image and installs packages). The lab scripts run *inside* the containers, so you
   do **not** need Python on your own laptop. Read the Week 1 recap.
2. **In class (100 minutes)** — 10-minute Week 1 quiz + short brief + guided lab (crack the leaked
   file, capture the flag, show the fix) + debrief + evidence capture. Slides: `{{ slides }}`.
3. **Common work (60 points)** — crack the leaked MD5 store with `crack.py`, log in as `admin` and
   capture the flag with `login.py`, then run `exploit.py` to show the same attack finds nothing
   against the bcrypt store. Explain why.
4. **Assigned format (40 points)** — complete **either** the Conventional written questions
   **or** AIR-Sec (Audit the AI 20 + EiPE 10 + Prompt Problem 10). Both versions total 100.
   Viva checks support feedback/authenticity within the criteria; they add no separate marks.
5. **After class** — finish detailed calculations, explanations and the assigned format;
   retain all original questions as assigned work or study extensions. Submit the worksheet
   PDF and required evidence according to [SUBMISSION.md](../../SUBMISSION.md). This week
   has no separate code-fix/GitHub submission.

## Objectives
- Say what a hash function gives you (fixed-size, one-way, deterministic) and why we store the
  hash of a password, not the password.
- Explain why an **unsalted, fast** hash (MD5/SHA-256) is a poor way to store passwords, and
  crack one in practice with an offline dictionary attack.
- Explain what a **per-user salt** defeats and why it need not be secret.
- Explain what a slow password hash's **cost** controls, and verify by running that the fast
  attack that broke the MD5 store finds nothing against a bcrypt store.

## 🔓 Cracking game — "Crack the Leaked DB"
A user database leaked. Two versions of the same store, same usernames and passwords, different
hashing:

| Service | Port | Password store | Crackable by fast offline dictionary? |
|---|---|---|---|
| `vulnerable_app.py` | `:8094` | unsalted **MD5** (`users_vulnerable.csv`) | **Yes** — milliseconds |
| `fixed_app.py` | `:8095` | **bcrypt**, per-user salt + cost (`users_fixed.csv`) | **No** (to this technique) |

**Why it's exciting:** instant feedback — the password either cracks or it doesn't — then you
watch the exact same attack bounce harmlessly off bcrypt.

Both apps expose the same endpoints:
- `POST /login {username, password}` → if the password's hash matches the stored hash, the
  server marks your **session** logged-in as that user.
- `GET /admin` → if your session is logged in as `admin`, returns JSON `{"flag": ...}`; else `403`.

1. **Exfil:** you have the leaked `users_vulnerable.csv` (rows of `username,md5hex`). You never
   needed to log in to get it — it's a database dump.
2. **Crack:** hash each word in `wordlist.txt` with MD5 and match it against the stored `admin`
   hash → recover the admin's plaintext password. Because MD5 is fast and **unsalted**, one
   precomputed table cracks the whole file and the admin falls in milliseconds.
3. **Log in & cash in:** `POST /login` the recovered password to `:8094`, then `GET /admin` **on
   the same session** → the flag.
4. **Confirm the fix:** run the *same* md5-precompute-over-the-wordlist technique against
   `users_fixed.csv` (bcrypt). It matches **nothing** — the stored hashes are salted `$2b$…`
   bcrypt strings, not MD5 hex. That is the empirical proof that salting + a slow KDF defeats the
   fast-dictionary / rainbow-table attack.

**Important framing (don't overclaim):** the fixed store resists *this fast technique*, not all
attacks. The admin's password (`sunshine2021`) is a weak, in-wordlist password, so a *slow
per-hash bcrypt dictionary* would still recover it — just at orders of magnitude higher cost per
guess. bcrypt buys you **work factor**, not invincibility; pair it with a strong-password policy.
This is exactly the cost/work-factor argument in worksheet Q3.

## Run it

Run the scripts **inside** the container, so no Python is needed on your laptop:

```bash
cd {{ labpath }}
docker compose up -d                              # :8094 vulnerable, :8095 fixed
docker compose logs vulnerable | grep "Running on"  # wait until the server is up
docker compose exec vulnerable python crack.py       # recover every password from the MD5 file
docker compose exec vulnerable python login.py sunshine2021   # log in as admin -> flag
docker compose exec vulnerable python exploit.py     # PASS :8094 (flag) + PASS :8095 (0 matches)
```

(You can also run `python exploit.py` on the host if you have Python 3 with `requests`; running
inside the container avoids any host-Python setup.)

Flag configuration: the shared demo flag is fine — record the value from your own run with your
own evidence and explanation; no personal flag is required this week.

**Verified (2026-11-02):** `docker compose up -d`, then `crack.py`, `login.py sunshine2021` and
`exploit.py` were all run inside live containers on this machine. `crack.py` recovered all 8
passwords (admin → `sunshine2021`) in ~0.09 ms; `login.py` showed `/login` → 200, `/admin` with
the session → the flag, and `/admin` with no cookie → 403; `exploit.py` printed both `PASS` lines
and exited 0 (md5 technique matched 0/8 bcrypt rows). A wrong password → 403 on both apps.

## Deliverable

Submit the common evidence and reasoning (60) plus only the assigned Conventional (40)
or AIR-Sec (40) format. The details below describe the common artifact; the worksheet
identifies the alternative sections.
The captured flag + the recovered admin password + a short note stating (a) exactly why the MD5
store fell in milliseconds (fast + unsalted), and (b) which single property of the bcrypt store
defeats the md5-precompute technique — and why bcrypt still isn't a substitute for a
strong-password policy. Full tasks: `worksheet.md`.

## References
- NIST SP 800-63B — *Digital Identity Guidelines* (memorized-secret / password storage guidance).
- OWASP *Password Storage Cheat Sheet* — argon2id / bcrypt / scrypt, salting, peppering.
- Boneh & Shoup, *A Graduate Course in Applied Cryptography*, ch. 8 (collision-resistant hashing)
  — free online.
- https://en.wikipedia.org/wiki/Rainbow_table
- Provos & Mazières, *A Future-Adaptable Password Scheme* (the bcrypt paper), USENIX 1999.
