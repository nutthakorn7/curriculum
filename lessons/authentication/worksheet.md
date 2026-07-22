# Worksheet 14 — User Authentication: The Server Sees Your Password (Unless It Can't)

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** NIST SP 800-63B · OWASP Authentication / Credential Stuffing Cheat Sheets ·
> CWE-522 (Insufficiently Protected Credentials), CWE-319 (Cleartext Transmission — to the
> endpoint), CWE-532 (Sensitive Info in Log File)
> **Kind:** Hybrid — a runnable password-sent-vs-never-sent demo (Part 2a) alongside conceptual
> content that stays theoretical this week (TOTP/FIDO2/SSO comparison, Part 1 + Part 2c EiPE).

## Part 0 — Student Information
| Name | Student ID | Date | Group |
|---|---|---|---|

*Disclose any AI assistance used anywhere in this worksheet here (tool + what you asked it).*

---

## Part 1 — Conventional Arm: Essay Questions

Answer each in your own words (roughly 120–200 words per answer — enough to show you understand the
mechanism, not so much that you're padding).

**Q1.** Why is sending a password to the server — **even over TLS** — a risk? Name at least three
distinct ways the server-side plaintext password can be exposed.

**Q2.** What is the difference between the three authentication factors (something you *know* /
something you *have* / something you *are*)? Give one concrete example of each, and state one
weakness of each.

**Q3.** What does a challenge-response protocol achieve that plain password submission does not?
Explain what actually travels on the wire in each case.

**Q4.** What is a PAKE (e.g. SRP, OPAQUE)? Name the **two** properties a real PAKE provides *beyond*
"the password is not sent" (hint: offline-dictionary resistance on the stored verifier; mutual
authentication), and explain what each one protects against.

**Q5.** How does TOTP (an authenticator app) work? Why is a TOTP code **phishable** while a
FIDO2/WebAuthn credential is **not**? (Consider what the user types vs. what the authenticator does,
and what each is bound to.)

**Q6.** What is credential stuffing? Which single control most reduces its blast radius, and why
does that control help even when the leaked passwords are genuinely correct for some accounts?

**Q7.** Password-storage recap (ties to {{ ref('hash') }}): why should the server's stored verifier use
bcrypt/argon2 **with a per-user salt**, rather than a plain fast hash? What does the salt stop, and
what does the slow/memory-hard work factor stop?

**Q8.** SSO / OAuth: what does "delegated authentication" buy you (for users and for the relying
application)? What new single-point-of-failure risk does introducing an identity provider create?

---

## Part 2 — AIR-Sec Arm: Hands-On Lab, Audit-the-AI, EiPE, Prompt Problem, Viva

AI is a power tool you must **distrust** — several parts below are graded on your *critique*, not on
how well you can prompt an AI. Full run instructions: [`README.md`](README.md).

### Part 2a — Lab steps + evidence artifact (required)

**Setup.** `server.py` is a Flask auth server whose behaviour is set by the `PAKE` env var (baked
into each compose file). `client.py` runs the matching login flow. The demo account is `alice` with
password `correct-horse-battery`.

1. Run **vulnerable mode** (plain password login):
   ```bash
   cd {{ labpath }}
   docker compose -f docker-compose.vulnerable.yml up --build --abort-on-container-exit
   ```
   Capture the full log output. Your required evidence line is:
   ```
   SERVER SAW PASSWORD: correct-horse-battery
   ```
   plus `LOGIN OK` from the client. **This `SERVER SAW PASSWORD` line is your
   personalized/attributable artifact for this HYBRID week, in place of a CTF flag.** The password
   string is a lab constant (the same for every student), so what makes your submission *yours* is
   the identity proof you attach: your terminal screenshot must show your `whoami` / login email /
   student ID and a timestamp alongside the captured log, per the Evidence & Integrity section
   below. In one line, note **which service printed the password and why** — i.e. what does the
   server having your plaintext in a request handler let a malicious operator do that TLS did not
   prevent?
2. Tear down: `docker compose -f docker-compose.vulnerable.yml down`.
3. Run **fixed mode** (challenge-response):
   ```bash
   docker compose -f docker-compose.fixed.yml up --build --abort-on-container-exit
   ```
   Capture the full log output. Your required evidence is **all** of:
   - a `SERVER SAW: nonce=... proof=...` line (the server logged what it *did* receive),
   - `LOGIN OK` from the client (authentication still succeeded), and
   - the **absence** of any `SERVER SAW PASSWORD` line and of the password string itself.
   Confirm the absence explicitly and record the outputs:
   ```bash
   docker compose -f docker-compose.fixed.yml logs | grep -c "correct-horse-battery"   # record: should be 0
   docker compose -f docker-compose.fixed.yml logs | grep -c "SERVER SAW PASSWORD"      # record: should be 0
   ```
4. Tear down: `docker compose -f docker-compose.fixed.yml down`.

**Submit:** both captured logs (with identity proof visible), your one-line note from step 1, and
the two `grep -c` outputs from step 3.

**One-line reflection to include with your logs** *(graded on reasoning, not copied text)*: in the
fixed mode the client still proves it knows `correct-horse-battery`, yet the server never sees it.
In your own words: what does the client send *instead* of the password, and why can't an attacker
who records that (the nonce and the proof) reuse it to log in later?

### Part 2b — Audit-the-AI (required)

A teammate asked an AI assistant to "write a Flask login handler with good logging for debugging."
The AI produced the handler below. It runs, it authenticates correctly, and the logging "looks
professional." **Find the security flaw, name it, and say exactly which line leaks what to whom.**

```python
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("auth")

@app.post("/login")
def login():
    body = request.get_json(force=True)
    # Log the full request so we can debug failed logins in production.
    log.info("login attempt: %s", body)           # <-- (A)
    user = users.get(body["username"])
    if user and bcrypt.checkpw(body["password"].encode(), user.pw_hash):
        log.info("login OK for %s", body["username"])
        return {"status": "ok"}
    log.warning("login FAILED for %s (pw=%s)", body["username"], body["password"])  # <-- (B)
    return {"status": "denied"}, 401
```

Answer, in your own words:
1. **What is the flaw?** Name the vulnerability class (and the CWE if you can) — note that the
   password *storage* here (`bcrypt.checkpw` against `pw_hash`) is actually *correct*; the flaw is
   elsewhere.
2. **Which line(s), and what exactly leaks?** Point to `(A)` and `(B)` specifically. What ends up in
   the logs? Who can read production logs (think: log-aggregation services, on-call engineers,
   anyone who breaches the log store)?
3. **Why does this partly defeat the point of hashing the stored password?** (Even though
   `pw_hash` is a proper bcrypt hash, what has the log now captured in *plaintext*?)
4. **Fix it.** Rewrite the two logging lines so the handler is still debuggable (you can tell *that*
   a login failed and *for which username*) without ever logging the password or the raw body.
5. **Tie-back:** how does this planted flaw relate to what you observed in Part 2a's **vulnerable**
   mode? (Both are the same underlying mistake — the credential reaching a place it should never
   reach. Name that place in each case.)

### Part 2c — Explain in Plain English (EiPE): proving you know a secret without revealing it (required)

The lab's fixed mode lets the client prove it knows the password **without sending it**. This
section is the conceptual half of this HYBRID week: explain the idea **in plain English to someone
who has never taken a crypto course** (no "HMAC," "KDF," or "nonce" used without first explaining
what you mean in ordinary words). In 4–6 sentences, cover:
- The everyday intuition: how can you convince a doorman you know the day's password *without
  saying the password out loud* where someone could overhear and reuse it? (Hint: the doorman
  shouts a fresh random word each time and you have to combine it with the secret in an agreed
  way.)
- Why the server can check your answer even though it deliberately **never stored your password** —
  only a scrambled "verifier" derived from it.
- Why an eavesdropper who records one exchange (the random challenge and your answer) **cannot**
  reuse it tomorrow.
- The honest limit (see README's honest-scope box): this demo proves *only* that the password is
  never sent. Name **one** thing a real PAKE also protects against that this demo does **not**.

### Part 2d — Prompt Problem (required)

Ask an AI assistant a single prompt along the lines of: *"How should I securely handle user login
so the server never learns the user's password?"* Paste its full response, then critique it. At
minimum, check whether the AI's answer:
- Distinguishes *protecting the password on the wire* (TLS) from *keeping the password away from the
  server endpoint* (challenge-response / PAKE) — a weak answer says "just use HTTPS" and stops
  there, missing that the server still sees the plaintext.
- Names a real mechanism correctly (SRP, OPAQUE, WebAuthn) rather than hand-waving "use a secure
  library" — and doesn't **hallucinate** a made-up protocol or misattribute an RFC.
- If it recommends a PAKE, does it correctly state the **two** extra properties (offline-dictionary
  resistance on the stored verifier; mutual authentication) — or does it overclaim a simple
  "hash-the-password-client-side" scheme as equivalent to a PAKE? (Client-side hashing alone does
  **not** give you either extra property — the hash just *becomes* the password.)
- Mentions verifier storage correctly (a slow, salted KDF such as bcrypt/argon2) and does **not**
  suggest storing anything reversible.

**Submit:** your exact prompt, the AI's full response, and a bullet-by-bullet critique quoting the
specific sentence(s) that are correct, hand-waved, or wrong.

### Part 2e — Viva Spot-Check (instructor-run, live)

Be ready to answer these live, in your own words, with no notes:

1. In **vulnerable** mode the server prints `SERVER SAW PASSWORD: correct-horse-battery`. If the
   whole connection had been wrapped in TLS, would that line still appear in the server's log? Why
   or why not — what does TLS actually protect, and what does it not?
2. In **fixed** mode the client still proves it knows the password, but the server only logs a
   `nonce` and a `proof`. Walk through how the server decides the login is valid **without** ever
   having the password. What does the server compare against?
3. The README is explicit that this fixed demo is **not** a full PAKE. Name the two properties it is
   missing, and give a concrete scenario where each missing property would bite you (e.g. the
   server database leaks; or the client is tricked into talking to a fake server).

---

## Grading rubric (100)

| Criterion | Points |
|---|---|
| Conventional arm — 8 essay questions (Part 1) | 40 |
| Lab evidence — both modes captured, evidence line present (vuln) / absent + `grep -c 0` (fixed) (Part 2a) | 20 |
| Audit-the-AI — flaw named, both leaking lines identified, working fix (Part 2b) | 15 |
| EiPE — proving knowledge without revealing, in plain English + honest limit (Part 2c) | 10 |
| Prompt Problem (Part 2d) | 10 |
| Viva spot-check (Part 2e, instructor-run) | 5 |

See the instructor answer key *(instructor use only, not in this file)* for model answers to all 8
essay questions, the Audit-the-AI fix, and the detailed lab/viva grading notes.

---

## Evidence & Integrity (required)

- **Identity proof:** every screenshot/log capture must show your **`whoami` / login email /
  student ID** and a **timestamp**. Generic or borrowed evidence is not accepted.
- **Personalized/attributable artifact:** the `SERVER SAW PASSWORD: correct-horse-battery` line from
  Part 2a vulnerable mode, submitted **together with** your identity-proof screenshot — the identity
  proof is what makes it yours, not the password text (which is a lab constant). For fixed mode, the
  artifact is the *absence* of that line plus your two `grep -c` outputs showing `0`. Submitting
  someone else's captured log without your own identity proof is a violation.
- **Explain in your own words** *(graded on your reasoning, not copied text)*:
  1. In vulnerable mode, **who** ended up with the plaintext password and **why did TLS not
     prevent it**?
  2. In fixed mode, **what did the client send instead of the password**, and **why can't a
     recorded challenge+proof be replayed** to log in again later?
