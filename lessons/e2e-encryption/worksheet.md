# Worksheet 13 — End-to-End Encryption: TLS Is Not Enough

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** CWE-311 (Missing Encryption of Sensitive Data), CWE-319 (Cleartext handling of
> sensitive data on the relay, even with encrypted transport)
> **Kind:** Hybrid — a runnable TLS-only-vs-E2EE demo (Part 2a) alongside conceptual content that
> stays theoretical this week (the root-of-trust / key-distribution problem, Part 2c).

> **Ethics note:** Only run and observe the local containers this lab spins up (`server.py`,
> `alice.py`, `bob.py`). The lesson is about reading a *provider's own logs* to see what it could
> store. Reading, intercepting, or logging other people's messages on systems you don't own is
> illegal. Keep everything inside this lab environment.

## Part 0 — Student Information
| Name | Student ID | Date | Group |
|---|---|---|---|

*Disclose any AI assistance used anywhere in this worksheet here (tool + what you asked it).*

---

## Part 1 — Conventional Arm: Essay Questions

Answer each in your own words (roughly 150–250 words per answer — enough to show you understand
the mechanism, not so much that you're padding). This is a normal written/essay task — **no
AI-resilience layer applies to this part; answer it yourself.** These five questions are the
conventional-arm assessment for {{ slot_label }}.

**Q1. Why TLS is not enough.** Explain why using TLS/HTTPS everywhere still does **not** stop the
server operator from reading your messages. Cover the role of servers (they terminate TLS and hold
plaintext), middleboxes / TLS termination, and why end-to-end encryption is necessary *despite*
TLS being nearly universal.

**Q2. The root-of-trust problem.** Public-key crypto lets Alice encrypt to Bob's public key — but
how does Alice *know* a given public key is really Bob's and not an impostor's? Explain the
chicken-and-egg problem of public-key distribution, why cryptography alone cannot fully solve
*trust*, and give **two** concrete examples of a root of trust (e.g. a certificate authority, a
key server, a manually verified fingerprint / QR safety number, a preinstalled root store).

**Q3. Why encrypted email failed.** PGP and S/MIME have existed for decades yet never reached mass
adoption for everyday email. Explain the technical limits (key discovery — how do you get someone's
public key; metadata leakage — what stays visible even when the body is encrypted) and the
usability problems. Then give **your own opinion**: if you were to redesign email for E2EE today,
what would you change and why?

**Q4. How Signal improves on PGP.** Explain how the Signal protocol addresses PGP's weaknesses.
Cover **TOFU** (trust on first use), the **X3DH** handshake, and the **Double Ratchet** (which
provides *forward secrecy* — a key compromise today does not expose past messages — and
*post-compromise security* — the session heals after a compromise). Explain why these properties
work better for *real, non-expert users* than PGP's "manage your own long-term keyring" model.

**Q5. Open problems in E2EE.** Pick **one** of: (a) group-messaging fan-out, (b) multi-device key
sync, or (c) the limits of TOFU and how *Key Transparency* aims to fix them. State what the problem
is, why it is genuinely hard, and the **security-vs-usability trade-off** it forces on designers.

---

## Part 2 — AIR-Sec Arm: Hands-On Lab, Audit-the-AI, EiPE, Prompt Problem, Viva

AI is a power tool you must **distrust** — several parts below are graded on your *critique*, not
on how well you can prompt an AI. Full run instructions: [`README.md`](README.md).

### Part 2a — Lab steps + evidence artifact (required)

**Setup.** `server.py` is the provider and is **byte-for-byte the same in both modes** — it always
logs `SERVER SAW: <payload>`. What changes is what `alice.py` chooses to send. There is no host
port; you read the container logs.

1. Run **vulnerable mode** (TLS-only provider that can read everything):
   ```bash
   cd {{ labpath }}
   docker compose -f docker-compose.vulnerable.yml up --build
   ```
   Capture the full log output. Your required evidence line is:
   ```
   SERVER SAW: meet at pier 39 at midnight
   ```
   plus `BOB RECEIVED: meet at pier 39 at midnight`. **The `SERVER SAW: ...` plaintext line is your
   personalized/attributable artifact for this HYBRID week, in place of a CTF flag.** The message
   text is fixed for every student (`SECRET_MESSAGE` is a lab constant, not per-student), so what
   makes your submission *yours* is not the string — it's the same identity-proof mechanism as
   every other week: your terminal screenshot must show your `whoami` / login and a timestamp
   alongside the captured log, per the Evidence & Integrity section below. Note in one line: *who*
   could read the secret in this mode, and *why the fact that the connection could be HTTPS doesn't
   change that answer*.
2. Tear down: `Ctrl-C`, then `docker compose -f docker-compose.vulnerable.yml down`.
3. Run **fixed mode** (true end-to-end encryption):
   ```bash
   docker compose -f docker-compose.fixed.yml up --build
   ```
   Capture the full log output. Your required evidence is **both** of:
   - a `SERVER SAW:` line that is now **long base64 gibberish**, NOT the plaintext, and
   - `BOB DECRYPTED: meet at pier 39 at midnight` (bob still recovers the secret client-side).

   Then confirm the plaintext is **absent** from the server's log explicitly:
   ```bash
   docker compose -f docker-compose.fixed.yml logs server | grep -c "meet at pier 39 at midnight"
   ```
   and record that it prints `0` (run the same grep against the vulnerable-mode server log to see
   it print `1`, if you like the contrast).
4. Tear down: `Ctrl-C`, then `docker compose -f docker-compose.fixed.yml down`.

**Submit:** both captured logs (with identity proof visible), your one-line note from step 1, the
fixed-mode base64 `SERVER SAW:` line, the `BOB DECRYPTED` line, and the `grep -c` output from
step 3.

---

## 🤖 Audit the AI (Part 2b — required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

You asked an AI assistant: *"Write me a secure chat backend so nobody can read my users' messages."*
Below is what it produced. It *looks* secure — it mentions encryption, it uses `https`, it even
talks about protecting messages — but it is exactly the **vulnerable mode** of this lab dressed up
in reassuring language. Your job: find the flaw.

> **AI's answer — "a secure chat backend":**
>
> ```python
> # Secure chat server. All traffic is encrypted with TLS (https), so
> # messages are safe from eavesdroppers on the network.
> @app.post("/send")                       # served over https:// via our TLS proxy
> def send():
>     msg = request.json["message"]        # plaintext message from the sender
>     db.execute(
>         "INSERT INTO messages (sender, recipient, body) VALUES (?, ?, ?)",
>         (request.json["from"], request.json["to"], msg),
>     )
>     log.info("stored message from %s: %s", request.json["from"], msg)
>     return {"ok": True}
>
> @app.get("/inbox/<user>")                # also over https://
> def inbox(user):
>     rows = db.execute("SELECT sender, body FROM messages WHERE recipient=?", (user,))
>     return {"messages": [dict(sender=r[0], body=r[1]) for r in rows]}
> ```
>
> "This backend is secure: every request and response travels over **HTTPS/TLS**, so the messages
> are encrypted and no attacker on the network can read them. Messages are safely stored in the
> database and delivered only to the intended recipient's inbox. Because we use industry-standard
> TLS, this is end-to-end encrypted and privacy-preserving."
>
> — end of AI answer —

1. **Find what's wrong.** Quote the exact line(s). (Hint: the TLS claim in the transport layer may
   even be true — don't waste your critique arguing about `https`. Look at what the **server
   itself** does with `msg`: what does it `INSERT` into the database, and what does it write to
   `log.info`? Ask who, besides the network, can read the message here.)
2. **Explain the false claim.** In 2–3 sentences: why is the sentence *"Because we use
   industry-standard TLS, this is end-to-end encrypted"* **wrong**? Name the two different
   guarantees the AI has conflated (transport encryption vs. end-to-end encryption), and state
   precisely who can still read every message in the AI's design. Connect this to the **vulnerable
   mode** you ran in Part 2a — it is the same flaw.
3. **Produce the corrected design yourself.** Describe (code sketch or clear prose) how you would
   change this so the *server operator* cannot read the messages, mirroring the lab's fixed mode:
   where does encryption/decryption move to, whose key encrypts the message, and what does the
   server end up storing instead of plaintext? State the single most important change in one
   sentence (hint: it is **not** "add more TLS" — it is *move the encryption boundary to the
   endpoints*).

> Disclose any AI use (beyond this provided artifact) in the Part 0 table. This task counts toward
> your Defense + Reflection score.

---

## 🧠 Comprehension & Prompt (Parts 2c–2d — required)

**Part 2c — Explain in Plain English (EiPE).** A non-technical friend says: *"WhatsApp already uses
HTTPS — the little lock icon — so my messages are already private. Why does 'end-to-end encrypted'
even matter?"* Answer them in **4–6 sentences, in genuinely plain language** (no "TLS handshake,"
"asymmetric," "RSA," "public key" dropped without first explaining what you mean in ordinary
words). Cover:
- What the "lock icon" / HTTPS actually protects (the message while it's *travelling* between their
  phone and WhatsApp's computers) — and, crucially, what it does **not** protect (the message once
  it *arrives* at WhatsApp's computers, where it would sit readable if that were all they did).
- What **end-to-end** encryption adds: the message is scrambled on the sender's phone in a way that
  **only the recipient's phone can unscramble**, so even WhatsApp's own servers only ever hold
  gibberish — connect this to the two `SERVER SAW:` lines you captured (plaintext vs. base64).
- Why this matters in practice: name one concrete thing that becomes impossible for the provider
  when messages are E2EE (e.g. handing readable messages to whoever asks, scanning them for ads,
  or leaking them in a breach).

**Part 2d — Prompt Problem.** Ask an AI assistant a single prompt along the lines of: *"Explain the
difference between using HTTPS/TLS for a chat app and making it end-to-end encrypted."* Paste its
full response, then critique it. At minimum, check whether the AI's answer:
- Correctly locates *where the plaintext exists* in each case — TLS: readable on the server after
  the connection terminates; E2EE: only ever plaintext on the two endpoints, ciphertext on the
  server. An answer that just says "E2EE is more secure" without saying *who is newly excluded from
  reading* has dodged the question.
- Names the **threat model difference**: TLS defends against a *network eavesdropper*; E2EE
  additionally defends against the *provider itself* (and anyone who compromises or subpoenas it).
- Gets the **trust bootstrap** right (ties to Q2): E2EE only helps if you have the *right* public
  key for the recipient — an answer that hand-waves "the app just encrypts to the recipient"
  without noting that the app/provider distributing those keys must itself be trusted (or verified
  out-of-band, e.g. safety numbers) has hidden the hard part.
- Doesn't **hallucinate** a mechanism (e.g. claiming "HTTPS is already end-to-end," inventing a
  made-up protocol name, or asserting TLS "encrypts data at rest on the server" — it does not).

**Submit:** your exact prompt, the AI's full response, and a bullet-by-bullet critique quoting the
specific sentence(s) that are correct, hand-waved, or wrong.

---

## 🎤 Viva Spot-Check (Part 2e — instructor-run, live)

Be ready to answer these live, in your own words, with no notes:

1. In the fixed-mode logs, `server.py` is running the *exact same code* as in vulnerable mode — it
   still calls `print(f"SERVER SAW: {payload}")` on whatever it receives. So why does the plaintext
   `meet at pier 39 at midnight` appear in the server log in one mode but not the other? Where did
   the difference actually come from?
2. In fixed mode, bob generates his RSA keypair *inside the container at startup* and only ever
   publishes the **public** half. Walk me through what alice does with that public key, and explain
   why the server — which relayed the public key and stored the ciphertext — still cannot decrypt
   the message.
3. A classmate says: "Fixed mode proves alice was really talking to bob and nobody tampered with
   anything." Are they right? What does the lab actually prove, and what does it **not** prove —
   and which essay question (Q2) is about the gap?

---

## Grading rubric (100)

| Criterion | Points |
|---|---|
| Conventional arm — 5 essay questions (Part 1) | 40 |
| Lab evidence — both modes captured, `SERVER SAW` plaintext vs. base64, `BOB DECRYPTED`, `grep -c 0` (Part 2a) | 20 |
| Audit-the-AI — TLS≠E2EE flaw found, server-can-read named, corrected design (Part 2b) | 15 |
| EiPE (WhatsApp) + Prompt Problem (Parts 2c–2d) | 15 |
| Viva spot-check (Part 2e, instructor-run) | 10 |

See the instructor answer key *(instructor use only, not in this file)* for model answers to all 5
essay questions, the exact planted flaw in the Audit-the-AI snippet, and the detailed lab/viva
grading notes.

---

## Evidence & Integrity (required)

- **Identity proof:** every screenshot/log capture must show your **`whoami` / login email /
  student ID** and a **timestamp**. Generic or borrowed evidence is not accepted.
- **Personalized/attributable artifact:** the `SERVER SAW: meet at pier 39 at midnight` line from
  Part 2a vulnerable mode, submitted **together with** your identity-proof screenshot — the
  identity proof is what makes it yours, not the message text. Submitting someone else's captured
  log without your own identity proof is a violation.
- **Explain in your own words** *(graded on your reasoning, not copied text)*:
  1. In vulnerable mode, **who** could read the secret and **why** — and why "but it's over HTTPS"
     would not have saved you.
  2. In fixed mode, **why the server could not read the message** even though it stored and logged
     it — and what the lab still does **not** prove (tie this to the root-of-trust problem, Q2).
