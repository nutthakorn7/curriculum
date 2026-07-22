# Worksheet 5 — Key Exchanges: MITM Against Unauthenticated Diffie-Hellman

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** RFC 3526 (MODP groups) · CWE-322 (Key Exchange without Entity Authentication),
> CWE-300 (Channel Accessible by Non-Endpoint)
> **Kind:** Hybrid — a runnable MITM demo (Part 2) alongside conceptual content that stays
> theoretical this week (small-subgroup confinement, Part 2b).

## Part 0 — Student Information
| Name | Student ID | Date | Group |
|---|---|---|---|

*Disclose any AI assistance used anywhere in this worksheet here (tool + what you asked it).*

---

## Part 1 — Conventional Arm: Essay Questions

Answer each in your own words (roughly 120–200 words per answer — enough to show you understand
the mechanism, not so much that you're padding).

**Q1.** Why do Alice and Bob need a key exchange instead of simply sending a symmetric key
directly? Explain what risk the key exchange solves.

**Q2.** In an unauthenticated key exchange, how can an active MITM attacker impersonate both
sides? Describe the attacker's steps and why Alice/Bob cannot detect it.

**Q3.** Key exchanges protect against passive attackers but not active ones. Give one real-world
scenario where this distinction matters.

**Q4.** Why must DH choose a very large prime `p` and a generator `g`? What happens if `p` is
small or non-prime? Explain in terms of the discrete logarithm problem.

**Q5.** Explain why the discrete logarithm problem is "hard" and how this hardness enables DH to
work securely.

**Q6.** ECDH provides the same security as DH but with much smaller keys. Why is this important
for real protocols like TLS, SSH, or mobile apps? Discuss performance, storage, or bandwidth.

**Q7.** Why is it dangerous to use custom DH parameters or non-standard groups? (weak primes,
broken standards)

**Q8.** What security problem occurs if an implementation does not validate received public keys
during DH or ECDH? Explain the attack surface.

**Q9.** Explain the core idea of a small subgroup attack. Why does sending a malicious public key
allow an attacker to leak private-key bits?

**Q10.** Why do many modern systems choose X25519 instead of classic P-256 or classic DH?
Consider security design, simplicity, resistance to pitfalls.

---

## Part 2 — AIR-Sec Arm: Hands-On Lab, EiPE, Prompt Problem, Viva

AI is a power tool you must **distrust** — several parts below are graded on your *critique*,
not on how well you can prompt an AI. Full run instructions: [`README.md`](README.md).

### Part 2a — Lab steps + evidence artifact (required)

**Setup.** `common.py` gives all three services (`alice.py`, `bob.py`, `relay.py`) a shared
RFC3526 Group 14 (2048-bit) DH group. Alice is configured to dial `relay`, never `bob` directly —
that is the premise: an active attacker controls the network path.

1. Run **vulnerable mode**:
   ```bash
   cd {{ labpath }}
   docker compose -f docker-compose.vulnerable.yml up --build
   ```
   Capture the full log output. Your required evidence line is:
   ```
   RELAY INTERCEPTED: the launch code is 4471
   ```
   **This is your personalized/attributable artifact for this HYBRID week, in place of a CTF
   flag.** The message text itself is fixed for every student (`SECRET_MESSAGE` is a lab
   constant, not per-student), so what makes your submission *yours* is not the string — it's
   the same identity-proof mechanism as every other week: your terminal screenshot must show
   your `whoami` / login and a timestamp alongside the captured log, per the Evidence &
   Integrity section below. Note in one line: which two `RELAY: completed independent DH
   handshake...` lines appear *before* the interception, and why relay needed both before it
   could decrypt-and-relog.
2. Tear down: `Ctrl-C`, then `docker compose -f docker-compose.vulnerable.yml down`.
3. Run **fixed mode**:
   ```bash
   docker compose -f docker-compose.fixed.yml up --build
   ```
   Capture the full log output. Your required abort evidence is **both** of:
   ```
   AUTH FAILED - ABORTING
   ```
   (once from `alice`, once from `bob`) and the **absence** of any `RELAY INTERCEPTED` line.
   Confirm the absence explicitly, e.g.:
   ```bash
   docker compose -f docker-compose.fixed.yml logs | grep -c "RELAY INTERCEPTED"
   ```
   and record that it prints `0`.
4. Tear down: `Ctrl-C`, then `docker compose -f docker-compose.fixed.yml down`.

**Submit:** both captured logs (with identity proof visible), your one-line note from step 1,
and the `grep -c` output from step 3.

### Part 2b — Explain in Plain English (EiPE): small subgroup attacks (required)

The lab you just ran demonstrates a **key-substitution** MITM — it does **not** demonstrate a
small subgroup attack. This section is the conceptual half of this HYBRID week: source Q9 asked
you to explain the core idea formally; here, explain it **in plain English to someone who has
never heard of group theory** (no "subgroup," "order," or "discrete log" used without first
explaining what you mean in ordinary words). In 4–6 sentences, cover:
- What a malicious DH public key can make the "shared secret" collapse down to (hint: instead of
  one of a huge number of possible outcomes, only a handful).
- Why that lets an attacker who sees how Bob responds to several such malicious keys narrow down
  bits of Bob's private key, one guess-and-check round at a time.
- Why this is a *different* failure from the MITM you just ran (that one exploited a **missing
  identity check**; this one would exploit a **missing input-validation check** on the received
  public key — see source Q8).

### Part 2c — Prompt Problem (required)

Ask an AI assistant a single prompt along the lines of: *"Explain why authenticated
Diffie-Hellman prevents a man-in-the-middle attack."* Paste its full response, then critique it.
At minimum, check whether the AI's answer:
- Correctly distinguishes *confidentiality against eavesdroppers* (what plain DH already gives
  you) from *authentication of the peer's identity* (what plain DH does **not** give you).
- Explains authentication as binding the DH public key to a verified identity (signature,
  certificate, or pre-shared MAC key) — not just asserting "authenticated DH is secure" without
  saying what is actually being checked or against what.
- Gets the trust bootstrap right: authenticated DH is only as strong as however the
  authentication key/certificate itself was distributed — an AI answer that hand-waves "just use
  a certificate" without noting that the certificate's issuer must itself be trusted in advance
  has hidden the hard part.
- Doesn't quietly conflate "authenticated" with "still gives forward secrecy" — a good answer
  should note that authenticating the exchange does not turn it into "just send a symmetric key,"
  because the DH exponents are still fresh and ephemeral every session.
- Doesn't hallucinate a mechanism (e.g. inventing a made-up "DH-Auth handshake" or misattributing
  a specific RFC/algorithm it doesn't actually name correctly).

**Submit:** your exact prompt, the AI's full response, and a bullet-by-bullet critique quoting
the specific sentence(s) that are correct, hand-waved, or wrong.

### Part 2d — Viva Spot-Check (instructor-run, live)

Be ready to answer these live, in your own words, with no notes:

1. In the vulnerable-mode logs, `relay` completes **two** DH handshakes before it prints
   `RELAY INTERCEPTED`. Why two, and what would go wrong for the attacker with only one?
2. In fixed mode, `relay.py`'s `handle_mitm_signed` still runs — it still generates its own DH
   keypairs and still tries to substitute them into both handshakes. What exactly stops the
   attack from succeeding, given that `relay` is running almost the same code as in vulnerable
   mode?
3. `AUTH_KEY` is a value Alice and Bob share ahead of time. Doesn't that mean they could have
   just used `AUTH_KEY` itself as the encryption key and skipped DH entirely? Why or why not —
   what would be lost?

---

## Grading rubric (100)

| Criterion | Points |
|---|---|
| Conventional arm — 10 essay questions (Part 1) | 40 |
| Lab evidence — both modes captured, evidence lines present/absent as required (Part 2a) | 20 |
| EiPE — small subgroup attack in plain English (Part 2b) | 15 |
| Prompt Problem (Part 2c) | 15 |
| Viva spot-check (Part 2d, instructor-run) | 10 |

See the instructor answer key *(instructor use only, not in this file)* for model answers to all
10 essay questions and the detailed lab/viva grading notes.

---

## Evidence & Integrity (required)

- **Identity proof:** every screenshot/log capture must show your **`whoami` / login email /
  student ID** and a **timestamp**. Generic or borrowed evidence is not accepted.
- **Personalized/attributable artifact:** the `RELAY INTERCEPTED: the launch code is 4471` line
  from Part 2a, submitted **together with** your identity-proof screenshot — the identity proof
  is what makes it yours, not the message text (see Part 2a for why). Submitting someone else's
  captured log without your own identity proof is a violation.
- **Explain in your own words** *(graded on your reasoning, not copied text)*:
  1. What did the attack do, and **why did it work** against unauthenticated DH?
  2. **Why does the HMAC fix actually stop it** — and what would still break it (e.g. if `relay`
     somehow obtained `AUTH_KEY`)?
