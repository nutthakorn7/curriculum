# {{ slot_label }} — Cryptography Used Correctly (and Misused)

**OWASP 2025:** A04 Cryptographic Failures · **CWE:** CWE-327, CWE-916, CWE-330, CWE-321 (key case of CWE-798)

## ✅ This week — what to do
1. **Before class** — Docker Desktop working ({{ ref('threat-modeling') }} *Lab 0*); the {{ ref('sdlc-tooling') }} images still pulled (`semgrep/semgrep`, `zricethezav/gitleaks`), plus `docker pull python:3.12-slim`; skim last week's recap.
2. **Slides, then class** — read `{{ slides }}` and answer the worksheet's **Part 2** before class; class opens with the weekly quiz (~10 min) and a short explanation + demo (~15 min).
3. **Lab (in class)** — play this week's game, then complete **Worksheet 3** (`worksheet.md`, Parts 1–4, incl. *Audit the AI* + *EiPE/Prompt*). Kickoff: `docker compose up`. Part 3 marks the core tasks (in class) and the optional bonus task (homework).
4. **Submit before the next class** (homework included) — worksheet PDF → `learn.zcr.ai/submit` · code → GitHub · weekly quiz → `learn.zcr.ai/quiz`. (How: [SUBMISSION.md](../../SUBMISSION.md).)
5. **Project** — apply this week's lesson to your [NoteVault project](../../project/README.md) where it fits.

*Time breakdown: [AGENDA.md](../../AGENDA.md). Grading: see the worksheet rubric.*

## Objectives
- Find crypto misuse in application code — with a scanner first, then by reading the code — and know why tools miss some of it.
- Store passwords with a vetted KDF (argon2id), and move legacy MD5 records to it with rehash-on-login.
- Keep keys out of source code, and use a CSPRNG for tokens.

How the primitives themselves work and break (cracking hashes, cipher modes, MACs, TLS) is taught in
Cryptography and Network Security (02005104). This week stays on the application-code side.

## 🔎 Signature game — "Misuse Hunt"
1. **Scan:** run Semgrep and Gitleaks on `vulnerable_crypto.py` and note what they flag — and what they don't.
2. **Hunt:** read the code with the checklist (MD5/SHA-1, `MODE_ECB`, key literals, `random` for secrets) and find all four mistakes with their line numbers.
3. **Remediate:** finish the rehash-on-login in `migrate.py` until it prints `ALL PASS`, then run the fixed version (argon2id, AES-GCM, `secrets`, key from `ENC_KEY_HEX`).

## Deliverable
The mistake table (line, mistake, CWE, flagged by a tool or not) + before/after code + a short note on which CWE each change closes.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
