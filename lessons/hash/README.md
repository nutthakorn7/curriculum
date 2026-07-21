# {{ slot_label }} — Hash Functions: Cracking a Leaked Password Database

**Kind:** LAB
**Concepts:** cryptographic hash functions, preimage/collision resistance, password storage,
salting, slow KDFs (bcrypt/argon2/scrypt), dictionary & rainbow-table attacks
**Analogous CWE:** CWE-916 (Use of Password Hash With Insufficient Computational Effort),
CWE-327 (Use of a Broken or Risky Cryptographic Algorithm), CWE-759/CWE-760 (Use of a One-Way
Hash Without a Salt / With a Predictable Salt)

## ✅ This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security`);
   skim the course intro on what a cryptographic hash is (one-way, fixed-size digest).
2. **Lecture (120 min)** — hash security properties (preimage / second-preimage / collision
   resistance); why MD5 and SHA-1 are broken and where that matters; why a *fast* hash is the
   wrong tool for passwords; salts, peppers, and slow KDFs. Slides: `{{ slides }}`
   *(not yet written — see course-plan-19weeks.md)*.
3. **Lab (180 min)** — play the cracking game below, capture your flag, then complete
   **Worksheet 2** (`worksheet.md`, Part 2 Conventional essays + Part 3 AIR-Sec lab, Audit-the-AI,
   EiPE/Prompt). Kickoff: `docker compose up`.
4. **Submit** — worksheet PDF + flag → Classroom · exploit code → GitHub. (How: [SUBMISSION.md](../../SUBMISSION.md).)

## Objectives
- State the three hash security properties (preimage, second-preimage, collision resistance) and
  name an attack each one prevents.
- Explain why an **unsalted, fast** hash (MD5/SHA-256) is a poor way to store passwords, and
  crack one in practice with an offline dictionary attack.
- Explain what a **per-user salt** defeats (precomputed rainbow tables, shared-hash correlation)
  and why it need not be secret.
- Explain what a slow KDF's **work factor / cost** controls, and verify empirically that the
  fast dictionary technique that broke the MD5 store finds nothing against a bcrypt store.

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
```bash
cd {{ labpath }}
docker compose up -d          # vulnerable_app.py on :8094, fixed_app.py on :8095
python exploit.py             # PASS on :8094 (flag), PASS on :8095 (fast technique finds nothing); exit 0
```
`exploit.py` needs only `requests` on the host (its bcrypt-store check uses `hashlib` + a string
compare — no bcrypt needed to *run the exploit*; bcrypt is only needed inside the fixed
container).

Per-student flag: `python3 ../../instructor/seed_flags.py env <STUDENT_ID> > .env` before
`docker compose up` (once this course's `instructor/seed_flags.py` exists — see
`course-plan-19weeks.md` open decision #4; until then `FLAG_HASH` defaults to
`FLAG{hash_crack_me}`).

**Verified:** `docker compose up -d` followed by `python exploit.py` was run against live
containers on this machine — the admin MD5 was cracked from the 101-word wordlist in ~0.1 ms to
`sunshine2021`, the cracked login was accepted and `GET /admin` returned the flag (PASS on
`:8094`), and the md5-precompute technique matched `0/8` bcrypt rows (PASS on `:8095`); the
script exited `0`. The `FLAG_HASH` env-var override was confirmed to change the captured flag
(re-ran with `FLAG_HASH=FLAG{hash_test_9z}` and that exact value came back). Negative controls
confirmed: `/admin` with no session → `403`; a wrong password → `403` on both apps. A manual
`curl` login+/admin against the **fixed** app on `:8095` with the real cracked password returned
the flag, confirming the fixed app's endpoints work (bcrypt only *raises the cost* of guessing,
it doesn't reject the correct password).

## Deliverable
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
