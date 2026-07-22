# {{ slot_label }} — End-to-End Encryption: TLS Is Not Enough (the Server Still Reads Your Messages)

**Topic (KOSEN68 source):** `Week12_E2E Encryption Questions.docx` · **Kind:** HYBRID
**Concepts:** transport encryption (TLS/HTTPS) vs. end-to-end encryption (E2EE), the server as a
trusted third party, hybrid public-key encryption (RSA-OAEP key wrap + AES-GCM), root-of-trust /
key-distribution problem, Signal vs. PGP · **Analogous CWE:** CWE-311 (Missing Encryption of
Sensitive Data), CWE-319 (Cleartext Transmission of Sensitive Information — here, cleartext
*storage on the relay* even when transit is encrypted)

## This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security` and
   this course's earlier weeks); skim the {{ ref('secure-transport') }} recap on asymmetric/hybrid encryption ({{ slot_label }}
   is where it gets *deployed* into a real messaging shape).
2. **Lecture (120 min)** — weekly quiz first (~10 min), then the lecture: why "we use HTTPS"
   answers a different question than "can the provider read my messages," and how Signal-style
   E2EE closes that gap. Slides: `{{ slides }}` *(not yet written — see
   `course-plan-19weeks.md`)*.
3. **Lab (180 min)** — run the demo in both modes below, then complete **Worksheet 13**
   (`worksheet.md`, Part 1 — Conventional essays; Part 2 — AIR-Sec arm: lab evidence,
   Audit-the-AI, EiPE, Prompt Problem, viva prep).
4. **Submit** — worksheet PDF + captured log evidence → Classroom · code unchanged (this is a
   read/run/observe lab, not an exploit-and-fix-the-code lab) → GitHub. (How: [SUBMISSION.md](../../SUBMISSION.md).)

## Objectives
- Explain the difference between **transport encryption** (TLS/HTTPS — protects data *in transit*
  between client and server) and **end-to-end encryption** (protects data *from the server
  operator itself*), and why the first does not imply the second.
- **Execute and observe** the exact same messaging server relay a secret in two configurations,
  and read from its own logs whether it could see the plaintext or not.
- Trace a real E2EE message shape: recipient publishes a public key, sender fetches it and
  performs **hybrid encryption** (fresh AES-256-GCM key per message, RSA-OAEP-wrapped to the
  recipient) *client-side* before the message ever reaches the server.
- Explain why moving the encryption boundary to the endpoints makes the server *structurally*
  unable to read messages — the guarantee comes from the clients, not from trusting the provider.
- Recognize related ideas this week's code does *not* fully solve but that Q2–Q5 ask you to reason
  about: the root-of-trust / key-distribution problem (how does Alice know the public key is
  really Bob's?), why PGP failed to reach mass adoption, and how Signal (TOFU, X3DH, Double
  Ratchet) improves on it.

## 👀 Signature game — "Who's Reading Your Mail?"
Play the messaging provider: `tail` your own server's log while a "private" message passes
through, and watch it sitting there in plaintext, sender's name and all. Then flip the client
to encrypt client-side before it ever reaches you, and watch your own server log turn into
unreadable ciphertext while the recipient still decrypts it perfectly.

**Why it's exciting:** watching your own "private" message sit in cleartext in a log file you
control is the moment end-to-end encryption stops being an abstract slide and becomes personal.

## How this maps to the E2EE concept

One server, two client roles, one shared secret to protect (`meet at pier 39 at midnight`):

| Service | Role | What it does |
|---|---|---|
| `server.py` (Flask) | The provider | `POST /pubkey` (bob publishes his public key), `POST /send` (alice posts a message for bob), `GET /pubkey` / `GET /fetch` (retrieval). Whatever it stores, it **logs verbatim**: `SERVER SAW: <payload>`. It is **byte-for-byte the same code in both modes** — it has no idea whether E2EE is on. |
| `alice.py` | Sender | Sends a message for bob *through the server*. In vulnerable mode she sends the raw plaintext; in fixed mode she fetches bob's public key and encrypts the secret **client-side** before sending. |
| `bob.py` | Recipient | In vulnerable mode he just fetches and reads the plaintext. In fixed mode he generates an RSA keypair **in memory**, publishes the public half, then fetches the ciphertext and **decrypts client-side**, printing `BOB DECRYPTED: <secret>`. |

The whole lesson lives in one design choice: **the server always logs what it stores, and what it
stores is whatever Alice chose to hand it.** Nothing about the server changes between the two
modes. In vulnerable mode Alice hands it the plaintext, so its log leaks the secret. In fixed mode
Alice hands it opaque ciphertext, so its log leaks nothing useful — *even though it is running the
identical code and could log just as eagerly*. That is exactly what end-to-end encryption is: the
message is confidential **from the server operator**, not merely from a network eavesdropper.

This is the point people miss when they say "but it's encrypted, it uses HTTPS." HTTPS/TLS
encrypts the message *in transit* — on the wire between Alice's phone and the server, and again
between the server and Bob's phone. But the server **terminates** that TLS: it decrypts, holds the
plaintext, and re-encrypts to forward it. A provider using TLS-only is exactly the vulnerable mode
here — it can read, log, subpoena-respond-to, scan, or leak every message. E2EE moves the
encryption boundary all the way out to the two endpoints so the server only ever holds ciphertext.

**What this lab does *not* show:** the hard part — *how Alice knows the public key she fetched is
really Bob's and not one the server swapped in* (the root-of-trust / key-distribution problem, and
the whole reason Signal needs TOFU + safety numbers). Here Alice simply trusts the key the server
hands her, which a malicious server could substitute (a public-key MITM, the messaging cousin of
{{ ref('key-exchanges') }}'s Diffie-Hellman MITM). That stays conceptual this week (Worksheet Q2, and Part 2c EiPE) —
the running demo is specifically *TLS-only-vs-E2EE (can the server read it)*, not key
authentication. Do not claim this lab proves Alice is talking to the real Bob; it proves only that
the **server** cannot read an E2EE message.

## Run it

There is **no host port published** — the three services talk to each other on an internal Docker
network (`labnet`) on port `8080`. You never point a browser at this; you read the container logs.

Vulnerable mode — TLS-only provider that can read everything:
```bash
cd {{ labpath }}
docker compose -f docker-compose.vulnerable.yml up --build
```
Expected log lines (interleaving/ports/IPs vary run to run; the container names and message text
do not). Flask's own request-access lines are omitted here for clarity:
```
week13-server  | SERVER: listening on 0.0.0.0:8080 (E2E=False)
week13-alice   | ALICE: starting (E2E=False), server at http://server:8080
week13-alice   | ALICE: sending the raw plaintext (no E2EE)
week13-server  | SERVER SAW: meet at pier 39 at midnight
week13-alice   | ALICE: message sent
week13-bob     | BOB: waiting for a message (no E2EE)
week13-bob     | BOB RECEIVED: meet at pier 39 at midnight
```
`alice` and `bob` are one-shot and exit `0` once done; `server` is a long-running service — stop
the stack with `Ctrl-C` (or, if you started it with `-d`, `docker compose ... down`) then tear it
down:
```bash
docker compose -f docker-compose.vulnerable.yml down
```
The line `SERVER SAW: meet at pier 39 at midnight` is the whole point: the provider stored and
logged your plaintext. **This captured leak line is the personalized/attributable evidence
artifact for this HYBRID week (in place of a CTF flag)** — see the worksheet's Evidence &
Integrity section for how your identity proof makes it *yours*.

Fixed mode — true end-to-end encryption; the server sees only ciphertext:
```bash
docker compose -f docker-compose.fixed.yml up --build
```
Expected log lines:
```
week13-server  | SERVER: listening on 0.0.0.0:8080 (E2E=True)
week13-bob     | BOB: published my public key, waiting for a message
week13-alice   | ALICE: encrypted the secret to bob's public key (client-side)
week13-server  | SERVER SAW: eyJlbmNfa2V5IjogImdQY29aZVcrSUdOSVJt...  (long base64, truncated)
week13-alice   | ALICE: message sent
week13-bob     | BOB DECRYPTED: meet at pier 39 at midnight
```
Two evidence facts here, both required: (1) the `SERVER SAW:` line now contains only **base64
gibberish**, NOT the plaintext; and (2) `bob` still recovers the secret — `BOB DECRYPTED: meet at
pier 39 at midnight` — proving the message got through end-to-end while the server never saw it.
The plaintext string **never appears anywhere in this mode's server log** — that absence is your
evidence the E2EE worked. Confirm it explicitly:
```bash
docker compose -f docker-compose.fixed.yml logs server | grep -c "meet at pier 39 at midnight"
```
This prints `0` in fixed mode (versus `1` in vulnerable mode). Tear down the same way:
```bash
docker compose -f docker-compose.fixed.yml down
```

Which compose file you point `-f` at is the **only** thing that selects the mode (`E2E` is baked
into each file's `environment:` block — unset for vulnerable, `"1"` for fixed). No environment
variables need to be set by hand.

**Note — no real TLS is implemented here.** Vulnerable mode *models* "HTTPS in transit but the
provider stores plaintext"; there is no literal TLS certificate in the lab (adding one would not
change the lesson — the server still terminates it and holds plaintext). The takeaway is precisely
that TLS and E2EE are *different guarantees*, which is why we don't need to implement TLS to
demonstrate the gap. No private key is shipped in this repo either: bob's RSA keypair is generated
**in memory at container startup** (`common.generate_rsa_keypair`) and never written to disk.

## Verified

Both modes were Docker-tested against the exact files in this directory, run fresh from a
scratchpad copy (OneDrive can leave dataless placeholder files that break `docker build` COPY, so
the run was done from a real local copy) and torn down after, with built images removed. The log
excerpts below are the **real captured output**, not a description.

- **Vulnerable** (`docker compose -f docker-compose.vulnerable.yml up -d --build`, then logs):
  ```
  week13-server  | SERVER SAW: meet at pier 39 at midnight
  week13-bob     | BOB RECEIVED: meet at pier 39 at midnight
  week13-alice   | ALICE: message sent
  ```
  `grep -c "SERVER SAW: meet at pier 39 at midnight"` on the server log returned **1**;
  `grep -c "BOB RECEIVED: meet at pier 39 at midnight"` returned **1**.

- **Fixed** (`docker compose -f docker-compose.fixed.yml up -d --build`, then logs):
  ```
  week13-bob     | BOB: published my public key, waiting for a message
  week13-alice   | ALICE: encrypted the secret to bob's public key (client-side)
  week13-server  | SERVER SAW: eyJlbmNfa2V5IjogImdQY29aZVcrSUdOSVJtMlZZZ2RvY2tJaFMrcUpU
                    RjJiYjhna0tsRFRidnZN...In0=   (single long base64 line, wrapped here for
                    display only)
  week13-bob     | BOB DECRYPTED: meet at pier 39 at midnight
  ```
  `grep -c "meet at pier 39 at midnight"` on the **server** log returned **0** (the plaintext is
  never there); `grep -c "BOB DECRYPTED: meet at pier 39 at midnight"` on the bob log returned
  **1**. Both stacks were torn down (`docker compose down`) and their built images removed after
  verification; nothing was left running.

## Deliverable
Worksheet 13 (`worksheet.md`, Parts 1–2), including the captured log evidence from both modes
(Part 2a) — the `SERVER SAW: meet at pier 39 at midnight` leak line, the fixed-mode base64
`SERVER SAW:` line, the `BOB DECRYPTED` line, and the `grep -c` result showing `0` in fixed mode —
plus the Audit-the-AI critique (Part 2b), the WhatsApp EiPE (Part 2c), the Prompt Problem
(Part 2d), and viva prep (Part 2e).

## References
- Signal Protocol documentation — X3DH key agreement and the Double Ratchet:
  https://signal.org/docs/ (the specifications behind TOFU + forward secrecy + post-compromise
  security discussed in Q4).
- Unger et al., *SoK: Secure Messaging*, IEEE S&P 2015 — systematizes trust establishment,
  conversation security, and transport privacy for E2EE messengers (directly relevant to Q2–Q5).
- Whitten & Tygar, *Why Johnny Can't Encrypt*, USENIX Security 1999 — the classic usability study
  on why PGP failed to reach mass adoption (Q3).
- NIST SP 800-56B Rev. 2, *Recommendation for Pair-Wise Key-Establishment Using Integer
  Factorization Cryptography* — RSA-OAEP key transport, the wrapping scheme used in `common.py`.
- https://en.wikipedia.org/wiki/End-to-end_encryption — overview and the TLS-termination /
  provider-access distinction this lab demonstrates.
