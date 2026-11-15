# {{ slot_label }} — Hybrid Encryption (lock the key with RSA, lock the messages with AES-GCM)

**Kind:** Docker lab, guided step by step. No math and no programming for the common 60 points. One container, no open ports,
local demo only. (Weeks 2–6 and 11–15 follow the same pattern.)
**References:** NIST SP 800-56A (key establishment), SP 800-38D (GCM, §8.2 nonce uniqueness) · OWASP Cryptographic Storage Cheat Sheet

## 100-minute class and assigned worksheet version

**In class:** 10 min retrieval review + 10 min brief + 60 min lab + 15 min debrief + 5 min evidence capture = 100 min. The Week 10 scored quiz opens Week 11.

**Common part — every student (60 points):** three guided tasks with `demo.py`: A1 watch Bob send two messages to Alice (new nonce each time),
A2 Bob reuses the nonce and Eve reads the secret without any key, A3 new nonces and Eve reads nothing, then compare the two lines of code.

**Assessment:** the common 60 points plus **one assigned version** (40 points): Conventional written questions Q1–Q4, or AIR-Sec Audit-the-AI 20 +
EiPE 10 + Prompt Problem 10. Both versions total 100. The other version is ungraded practice.

**Evidence:** copy the commands and results from your own machine into the answer sheet, with your name and student ID. The nonces are random per run, so your
hex numbers differ from your friends'; the `YES` / `NO` answers and the `RESULT` lines are the same. There is no personal flag this week.

## This week — what to do
1. **Before class** — Docker Desktop installed and the lab ZIP downloaded (worksheet "ก่อนเริ่ม"). Skim the Week 6 recap (AEAD).
2. **In class** — follow **Worksheet 10** step by step. Slides: `slides/week10.md`.
3. **Assigned version** — Conventional answers the four questions in the worksheet; AIR-Sec audits `audit_the_ai/broken_hybrid_encrypt.py`
   (it runs in the same container) and attaches the proof script, its output and `fixed_hybrid_encrypt.py` in the PDF.
4. **Submit** — one PDF `Wk10_<StudentID>.pdf` at `learn.zcr.ai/submit` (see [SUBMISSION.md](../../SUBMISSION.md)).
5. **Project** — if your term project sends data between two parties that do not already share a secret, this week's pattern
   (a public key locks an AES session key) applies directly.

## Objectives
- Explain why RSA alone is not used for bulk data (slow, short messages) and how hybrid encryption solves that.
- Name who holds which key (Alice: public + private, Bob: session key, Eve: nothing).
- Explain what a nonce is, and show that reusing one lets Eve read a message without any key.
- Fix it with a new nonce per message, and say what the scheme still does not give (who sent it, whether the public key is really Alice's).
- (AIR-Sec) Audit an AI-generated implementation whose only flaw is how the nonce is chosen.

## Files
| File | What it is |
|---|---|
| `docker-compose.yml`, `requirements.txt` | one container that installs the `cryptography` package and waits |
| `demo.py` | `good`, `reuse`, `attack good`, `attack reuse` (the helper the worksheet uses) |
| `audit_the_ai/` | the AIR-Sec audit file and instructions |
| `img/gcm-nonce-reuse.svg` | picture used on the slides |

## Deliverable
The common 60 points plus the assigned 40, as in the worksheet rubric. AIR-Sec keeps every audit deliverable: the quoted line, the proof script and output,
and the corrected code.

## References
- NIST SP 800-56A Rev. 3, *Pair-Wise Key-Establishment Schemes Using Discrete Logarithm Cryptography*.
- NIST SP 800-38D, *GCM and GMAC*, §8.2 (the uniqueness requirement on the nonce).
- https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- SEC 1: Elliptic Curve Cryptography, §5.1 (ECIES).
- Joux, *Authentication Failures in NIST version of GCM* (2006).
