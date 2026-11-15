# {{ slot_label }} — End-to-End Encryption: HTTPS is not enough

**Kind:** Docker lab, guided step by step. No math and no programming. Local containers only, no open ports; the server, Alice and Bob are small programs on one Docker network.
**Concepts:** transport encryption (TLS/HTTPS) vs. end-to-end encryption (E2EE), the server as a trusted third party, hybrid public-key encryption (RSA-OAEP key wrap + AES-GCM), the root-of-trust / key-distribution problem, Signal vs. PGP ·
**Analogous CWE:** CWE-311 (Missing Encryption of Sensitive Data), CWE-532 (Insertion of Sensitive Information into Log File); the Audit-the-AI example also illustrates CWE-312 (Cleartext Storage of Sensitive Information). CWE-319 concerns cleartext *transmission* and does not describe this TLS-only scenario.

## 100-minute class and assigned worksheet version

**In class:** 10 min Week 12 retrieval/review + 10 min brief + 60 min lab + 15 min debrief + 5 min evidence = 100 min. The scored Week 13 quiz is given at the start of Week 14.

**Common part — every student (60 points):** three guided tasks: A1 the TLS-only mode, where the server logs `SERVER SAW: meet at pier 39 at midnight`; A2 the client-side encryption (E2EE) mode, where the server logs unreadable base64 and Bob prints `BOB DECRYPTED: ...`; A3 find the two lines in `alice.py` that differ (`payload = hybrid_encrypt(...)` vs `payload = SECRET_MESSAGE`) and explain what the lab does **not** prove (Alice trusts the public key the server relays).

**Assessment:** the common 60 points plus **one assigned version** (40 points): Conventional written questions Q1–Q4, or AIR-Sec Audit-the-AI 20 + EiPE 10 + Prompt Problem 10. Both versions total 100. The other version is ungraded practice.

**Evidence:** copy the commands and results from your own machine into the answer sheet, with your name and student ID. The secret `meet at pier 39 at midnight` is the same for everyone; the base64 text in the E2EE mode differs per run (fresh keys). There is no personal flag this week.

## ✅ This week — what to do
1. **Before class** — Docker Desktop working, the lab ZIP downloaded, and the image built (worksheet "ก่อนเริ่ม", `docker compose -f docker-compose.vulnerable.yml build`). Skim the Week 10 recap on hybrid encryption.
2. **In class** — follow **Worksheet 13** step by step. Slides: `slides/week13.md`.
3. **Assigned version** — Conventional answers four questions; AIR-Sec audits an AI-written "secure chat backend", and writes the EiPE and the Prompt Problem.
4. **Submit** — one PDF `Wk13_<StudentID>.pdf` at `learn.zcr.ai/submit` (see [SUBMISSION.md](../../SUBMISSION.md)).

## Objectives
- Explain why HTTPS/TLS does not stop the **provider** from reading messages (the server terminates TLS and holds plaintext).
- See the same server code log readable text in one mode and unreadable ciphertext in the other, depending only on what Alice sends.
- Name where the encryption boundary sits in each mode (the server vs. the sender's device).
- State what the demo does **not** prove: it does not authenticate the public key relayed by the server, so a malicious relay could substitute its own key.
- Describe how safety numbers and Signal-style automatic key management address that gap.

## 👀 The two modes
`server.py` is byte-for-byte the same in both modes; it always prints `SERVER SAW: <payload>`. What changes is `alice.py`.

| Compose file | Alice sends | Server log | Bob |
|---|---|---|---|
| `docker-compose.vulnerable.yml` | the raw plaintext | `SERVER SAW: meet at pier 39 at midnight` | `BOB RECEIVED: ...` |
| `docker-compose.fixed.yml` (`E2E=1`) | ciphertext encrypted to Bob's public key | `SERVER SAW: <long base64>` | `BOB DECRYPTED: ...` |

In the E2EE mode Bob generates an RSA key pair in memory at start and publishes only the public half; Alice fetches it and encrypts client-side (AES-256-GCM, key wrapped with RSA-OAEP). No private key is stored on disk or committed.

## Run it (what the worksheet does)

```bash
cd labs/week13-e2e-encryption
docker compose -f docker-compose.vulnerable.yml build
docker compose -f docker-compose.vulnerable.yml up -d --build
docker compose -f docker-compose.vulnerable.yml logs server
docker compose -f docker-compose.vulnerable.yml logs bob
docker compose -f docker-compose.fixed.yml up -d --build
docker compose -f docker-compose.fixed.yml logs server
docker compose -f docker-compose.fixed.yml logs bob
docker compose -f docker-compose.fixed.yml run --rm --entrypoint grep alice -n "payload = " alice.py
docker compose -f docker-compose.vulnerable.yml down
docker compose -f docker-compose.fixed.yml down
```

Switching from the first mode to the second without a `down` in between works (verified); the older `up --build` plus `logs -f` flow with Ctrl-C also still works. The server log contains HTTP request lines too: look for the `SERVER SAW` line.

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
The common 60 points plus the assigned 40, as in the worksheet rubric.

## References
- Signal Protocol documentation — historical X3DH, PQXDH and the Double Ratchet:
  https://signal.org/docs/ (key agreement and conditional forward/post-compromise protection in Q4).
- Unger et al., *SoK: Secure Messaging*, IEEE S&P 2015 — systematizes trust establishment,
  conversation security, and transport privacy for E2EE messengers (directly relevant to Q2–Q5).
- Whitten & Tygar, *Why Johnny Can't Encrypt*, USENIX Security 1999 — the classic usability study
  on why PGP failed to reach mass adoption (Q3).
- NIST SP 800-56B Rev. 2, *Recommendation for Pair-Wise Key-Establishment Using Integer
  Factorization Cryptography* — RSA-OAEP key transport, the wrapping scheme used in `common.py`.
- https://en.wikipedia.org/wiki/End-to-end_encryption — overview and the TLS-termination /
  provider-access distinction this lab demonstrates.
