# Worksheet 12 — Secure Transport (TLS): Certificate-Validation-Bypass MITM

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** RFC 8446 (TLS 1.3), RFC 5280 (X.509 PKI), RFC 6125 (hostname verification) ·
> CWE-295 (Improper Certificate Validation), CWE-300 (Channel Accessible by Non-Endpoint)
> **Kind:** Hybrid — a runnable cert-bypass MITM demo (Part 2a) alongside conceptual content that
> stays theoretical this week (the wider Web PKI trust model, Part 2c).

## Part 0 — Student Information
| Name | Student ID | Date | Group |
|---|---|---|---|

*Disclose any AI assistance used anywhere in this worksheet here (tool + what you asked it).*

---

## Part 1 — Conventional Arm: Essay Questions

Answer each in your own words (roughly 150–250 words per answer — enough to show you understand
the mechanism, not so much that you're padding). These are the conventional written task; no AI
layer applies to Part 1.

**Q1. Evolution SSL → TLS.** SSL was retired and replaced by TLS, culminating in TLS 1.3. Explain
why the SSL family failed — cover both concrete *security* weaknesses and *design* problems — and
describe how TLS 1.3 specifically addresses those weaknesses.

**Q2. Security role of the TLS handshake.** Explain how the TLS handshake prevents a
man-in-the-middle attack. Describe the roles of (a) key exchange, (b) server authentication, and
(c) the `CertificateVerify` message, and explain what an attacker could do if any *one* of those
three components were missing.

**Q3. Forward secrecy in TLS 1.3.** Explain what forward secrecy is and how TLS 1.3 provides it.
Contrast this with legacy static-RSA key exchange (removed in TLS 1.3) and explain the security
impact of that older design. Use a real example (e.g. Heartbleed) to illustrate why forward
secrecy matters.

**Q4. 0-RTT (early data) trade-off.** TLS 1.3 adds a 0-RTT "early data" mode. Explain the
performance benefit and the security cost. Why is 0-RTT data *replayable* by an attacker, and why
should it therefore be restricted to idempotent operations?

**Q5. Web PKI trust model.** Trust on the web rests on Certificate Authorities. Explain the risk
posed by a *misbehaving or compromised* CA. Then compare three mitigations — **certificate
pinning**, **revocation** (CRL / OCSP / OCSP stapling), and **Certificate Transparency** — and say
which you would choose for a mobile banking app, and why.

**Q6. TLS vs. the Noise Protocol Framework.** Compare TLS and Noise across: flexibility,
runtime/negotiation complexity, upgradeability, and security assumptions. Argue whether Noise is
more suitable than TLS when *both* endpoints are under your control (e.g. IoT devices or internal
microservices), and say what you would give up by choosing it.

---

## Part 2 — AIR-Sec Arm: Hands-On Lab, Audit-the-AI, EiPE, Prompt Problem, Viva

AI is a power tool you must **distrust** — several parts below are graded on your *critique*, not
on how well you can prompt an AI. Full run instructions: [`README.md`](README.md).

### Part 2a — Lab steps + evidence artifact (required)

**Setup.** `gen_certs.py` generates, into a shared volume, a demo CA, Bob's CA-signed cert
(`CN=bob`), and a **self-signed impostor** cert that *also* claims `CN=bob`. `mitm.py` presents
the impostor cert; `bob.py` presents the real one. Alice is configured to dial `mitm`, never `bob`
directly — that is the premise: an active attacker controls the network path.

1. Run **vulnerable mode**:
   ```bash
   cd {{ labpath }}
   docker compose -f docker-compose.vulnerable.yml up --build
   ```
   Capture the full log output. Your required evidence line is:
   ```
   MITM INTERCEPTED: the vault code is 7731
   ```
   **This is your personalized/attributable artifact for this HYBRID week, in place of a CTF
   flag.** The message text itself is fixed for every student (`SECRET_MESSAGE` is a lab constant,
   not per-student), so what makes your submission *yours* is not the string — it's the same
   identity-proof mechanism as every other week: your terminal screenshot must show your `whoami`
   / login and a timestamp alongside the captured log, per the Evidence & Integrity section below.
   Note in one line: Alice logs that the TLS handshake **succeeded** — so the channel really is
   encrypted. Why did encryption not protect the secret?
2. Tear down: `Ctrl-C`, then `docker compose -f docker-compose.vulnerable.yml down -v`.
3. Run **fixed mode**:
   ```bash
   docker compose -f docker-compose.fixed.yml up --build
   ```
   Capture the full log output. Your required abort evidence is:
   ```
   CERT VERIFICATION FAILED - ABORTING
   ```
   from `alice` (with the reason line `ALICE: (reason: self-signed certificate)`), and the
   **absence** of any `MITM INTERCEPTED` line. Confirm the absence explicitly:
   ```bash
   docker compose -f docker-compose.fixed.yml logs | grep -c "MITM INTERCEPTED"
   ```
   and record that it prints `0`.
4. Tear down: `Ctrl-C`, then `docker compose -f docker-compose.fixed.yml down -v`.
5. **Write the fix yourself.** Every other task this week (and most weeks in this course) has you
   confirm a pre-built fix, not write one — this is the exception. Open `alice_student.py`: it is
   identical to `alice.py` except `build_client_context()` is a stub that raises
   `NotImplementedError`. Replace the stub with real code that trusts only the demo CA, verifies
   the chain, and verifies the hostname (see the file's docstring for the exact requirements — you
   do not need to hand-roll chain/hostname validation, one standard-library call does both
   correctly). Then:
   ```bash
   docker compose -f docker-compose.student-task.yml up --build
   ```
   You're done when you see `CERT VERIFICATION FAILED - ABORTING` (not a Python traceback, and not
   `TLS handshake succeeded`). Tear down: `docker compose -f docker-compose.student-task.yml down -v`.

**Submit:** both captured logs from steps 1 and 3 (with identity proof visible), your one-line note
from step 1, the `grep -c` output from step 3, **and your completed `alice_student.py`** (paste the
diff or the full `build_client_context()` function) with a 2–3 sentence explanation of what each
line does and why it's necessary — you may be asked to explain it live in the viva.

### Part 2b — 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

A teammate asked an AI assistant, *"write me a Python function that fetches JSON from our internal
HTTPS API — it kept throwing SSL errors so make it just work."* Here is what the AI produced. It
runs, the SSL errors go away, and it looks reassuringly tidy. It is also exactly the bug you just
watched intercept a secret.

> **AI's answer — "a robust HTTPS client":**
>
> ```python
> import requests
> import urllib3
> urllib3.disable_warnings()  # silence the noisy SSL warnings
>
> def fetch(url, token):
>     """Fetch JSON from our internal API. Uses TLS, so the connection is encrypted
>     and secure end-to-end."""
>     resp = requests.get(
>         url,
>         headers={"Authorization": f"Bearer {token}"},
>         verify=False,          # our internal cert isn't in the public trust store,
>                                # so we disable verification to avoid errors
>         timeout=10,
>     )
>     resp.raise_for_status()
>     return resp.json()
> ```
>
> "This is secure: `requests` uses HTTPS, so all traffic — including the bearer token — is
> encrypted in transit with TLS and cannot be read by anyone on the network. Setting
> `verify=False` just tells it to accept our internal certificate; it does not weaken the
> encryption. I also silenced the warnings so the logs stay clean."
>
> — end of AI answer —

1. **Find what's wrong.** Quote the exact line(s). (Hint: the crypto *is* real — the connection
   genuinely is TLS-encrypted, so don't waste your critique claiming "it's not encrypted." Look at
   what `verify=False` turns off, and map it directly onto what you saw `alice.py` do in
   vulnerable mode.)
2. **Explain the attack it enables.** In 2–3 sentences: with `verify=False`, what stops an
   attacker on the network path from doing to *this* client exactly what `mitm.py` did to Alice?
   Be specific about *what the bearer token would leak to* and why "it's encrypted" is true but
   irrelevant.
3. **Name the false reassurance.** The AI makes a specific claim that is *true but misleading*.
   Quote it and explain in one sentence why encryption-to-the-wrong-endpoint is worthless.
4. **Produce the corrected version yourself.** Rewrite `fetch` so it validates the internal cert
   properly. State the single most important change — and, since the reason the teammate reached
   for `verify=False` was a real problem (the internal cert isn't in the public trust store), say
   what the *correct* fix for that root cause is (hint: it is not "disable verification"; it is to
   tell the client which CA to trust — the same move `alice.py` makes in fixed mode with
   `VERIFY=1`).

> Disclose any additional AI use in the Part 0 table. This task counts toward your Defense +
> Reflection score.

### Part 2c — Explain in Plain English (EiPE): why a CA signature matters (required)

The lab's fixed mode rejected the impostor cert because it was **self-signed** — not signed by a
trusted CA — even though it claimed the exact same name (`CN=bob`, `SAN=DNS:bob`) as the real
server. This section is the conceptual half of this HYBRID week: source Q5 asked you to reason
about the Web PKI trust model formally; here, explain it **in plain English to a non-technical
friend** (no "X.509," "chain," "root store," or "CA" used without first explaining what you mean
in ordinary words). In 4–6 sentences, cover:
- What a certificate is *claiming* (roughly: "I am bob"), and why anyone — including an attacker —
  can *make* a certificate that says that (as the impostor did).
- What a **Certificate Authority's signature** adds: why a signature from a party your computer
  already trusts turns an unverifiable claim into a checkable one (use an everyday analogy —
  a notary, a passport office, a referral from someone you already trust).
- Why the self-signed impostor failed the check even though its *name* was correct — i.e. the
  computer isn't checking "does this say bob?", it's checking "did someone I trust vouch that this
  is bob?".
- One sentence on the limit of this trust model: what happens to the whole scheme if the trusted
  authority itself is dishonest or gets hacked (this connects back to Q5's compromised-CA risk —
  the demo does *not* cover this case, and you should say so).

### Part 2d — Prompt Problem (required)

Write a **single prompt** asking an AI to *implement a secure HTTPS client in Python that connects
to a service using a private/internal certificate authority, resistant to man-in-the-middle
attacks.* Run it, paste its full response, then critique it against these checks:
- Does it **keep certificate verification on** (a proper `verify=<ca-bundle>` / `cafile=` /
  `SSLContext` with the internal CA loaded) — or does it take the lazy exit and hand you
  `verify=False` / `CERT_NONE` (the trap this week is all about)?
- Does it distinguish *encryption* from *authentication* — i.e. does it note that TLS being "on"
  is not enough, the peer's cert must be **validated against a trust anchor** — or does it assert
  "it uses HTTPS so it's secure" and stop there?
- Does it get the trust bootstrap right: that "trust the internal CA" means *distributing that CA
  certificate to the client in advance by a secure channel*, and that the whole scheme is only as
  trustworthy as that CA — or does it hand-wave where the trust comes from?
- Does it hallucinate a mechanism (a made-up `requests` argument, a nonexistent flag, or a wrong
  claim like "pinning is built into `requests` by default")?

**Submit:** your exact prompt, the AI's full response, and a bullet-by-bullet critique quoting the
specific sentence(s) that are correct, hand-waved, or wrong. A strong prompt names the threat model
("must resist an attacker who controls the network path and can present their own certificate") so
the AI can't wriggle out with a toy example.

### Part 2e — Viva Spot-Check (instructor-run, live)

Be ready to answer these live, in your own words, with no notes:

1. In vulnerable mode, Alice's own log says the TLS handshake **succeeded** and the channel is
   encrypted — yet the MITM printed the secret in cleartext. Reconcile those two facts: if the
   encryption really worked, how did the attacker read the message?
2. In fixed mode, `mitm.py` runs the **exact same code** — it still presents the same self-signed
   impostor cert. Nothing about the attacker changed. So what, precisely, changed on Alice's side
   that made the attack fail, and at what point in the exchange did it fail (before or after Alice
   sent the secret)?
3. The impostor cert claims `CN=bob` and `SAN=DNS:bob` — the *same* name as the real Bob. So the
   fixed client's rejection reason is `self-signed certificate`, not a name mismatch. Why is that
   distinction the entire point of the lab — what *one* property of the real cert does the
   impostor lack, and who is supposed to provide it?

---

## Grading rubric (100)

| Criterion | Points |
|---|---|
| Conventional arm — 6 essay questions (Part 1) | 36 |
| Lab evidence — both modes captured, evidence lines present/absent as required (Part 2a) | 18 |
| Audit the AI — `verify=False` flaw found + corrected, false-reassurance named (Part 2b) | 20 |
| EiPE — why a CA signature matters, in plain English (Part 2c) | 12 |
| Prompt Problem (Part 2d) | 8 |
| Viva spot-check (Part 2e, instructor-run) | 6 |

See the instructor answer key *(instructor use only, not in this file)* for model answers to all 6
essay questions and the detailed lab/audit/viva grading notes.

---

## Evidence & Integrity (required)

- **Identity proof:** every screenshot/log capture must show your **`whoami` / login email /
  student ID** and a **timestamp**. Generic or borrowed evidence is not accepted.
- **Personalized/attributable artifact:** the `MITM INTERCEPTED: the vault code is 7731` line from
  Part 2a, submitted **together with** your identity-proof screenshot — the identity proof is what
  makes it yours, not the message text (see Part 2a for why). Submitting someone else's captured
  log without your own identity proof is a violation.
- **Explain in your own words** *(graded on your reasoning, not copied text)*:
  1. What did the attack do, and **why did it work** against a client that skipped certificate
     validation — given that the channel really was TLS-encrypted?
  2. **Why does loading the CA and keeping hostname checking on actually stop it** — and what is
     the one thing that would still defeat this check even in fixed mode (hint: think about Q5's
     compromised-CA scenario — what could an attacker present then that *would* chain to a trusted
     CA)?
