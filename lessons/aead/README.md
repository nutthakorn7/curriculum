# {{ slot_label }} — AEAD: the CBC Padding Oracle vs AES-GCM

**Kind:** LAB
**Concepts:** authenticated encryption (AEAD), PKCS#7 padding, padding oracle, AES-GCM,
associated data · **Analogous CWE:** CWE-204 (Observable Response Discrepancy), CWE-649
(Reliance on Obfuscation/Encryption Without Integrity), CWE-353 (Missing Support for Integrity
Check)

## This week — 100-minute class and assigned assessment

1. **Before class** — install **Docker** and run `docker compose up -d` once at home (the image is
   downloaded the first time, and the containers install packages every time they start, so you
   need internet each time). The lab scripts run *inside* the container, so you do **not** need
   Python on your own laptop. Read the Week 4 recap (CBC has no check, GCM has a tag).
2. **In class (100 minutes)** — 10-minute quiz + short brief + guided lab (ask the CBC server
   about a changed message, let the script read the secret from the `200` / `403` answers, see GCM
   give the same answer every time) + debrief + evidence capture. Slides: `{{ slides }}`.
3. **Common work (60 points)** — ask the CBC server three questions with the supplied helper
   `ask.py` (original, a letter changed at the start, a letter changed near the end), run
   `exploit.py` to read the secret without the key, then ask the GCM server the same three
   questions and explain why it gives nothing away.
4. **Assigned format (40 points)** — complete **either** the Conventional written questions
   **or** AIR-Sec (Audit the AI 20 + EiPE 10 + Prompt Problem 10). Both versions total 100.
   Viva checks support feedback/authenticity within the criteria; they add no separate marks.
5. **After class** — finish the explanations and the assigned format. Submit the worksheet
   PDF and required evidence according to [SUBMISSION.md](../../SUBMISSION.md). This week
   has no separate code-fix/GitHub submission.

## Objectives
- Say what **AEAD** means: encryption **and** a check that nothing was changed, in one step.
- See that an **unauthenticated** AES-CBC server that never shows the plaintext still leaks it
  through two different answers (`200` vs `403`): a **padding oracle**.
- Run the supplied script that reads the whole secret from those answers **without the key**.
- Explain in plain words why **AES-GCM** gives nothing away: it checks the **tag first** and gives
  the **same answer** for every failure.
- Know that GCM is not magic: an ignored tag error or a repeated nonce breaks it, and other
  different error messages (for example "user not found" vs "wrong password") leak in the same way.

## 🔓 Decryption game — "Read the Secret Without the Key"
Two Flask targets, same endpoints, different cipher:

| Service | Port | Cipher | Answers differ by where we change? |
|---|---|---|---|
| `vulnerable_app.py` | `:8098` | AES-256-**CBC**, no tag; `/decrypt` says `200` or `403 bad padding` | **Yes** |
| `fixed_app.py` | `:8099` | AES-256-**GCM** (AEAD); `/decrypt` says `403 decryption failed` for every failure | **No** |

Both serve the same encrypted secret at `GET /secret` (base64) and accept
`POST /decrypt {"ciphertext": "<base64>"}`. Neither ever returns the plaintext.

- **Vulnerable (`:8098`, CBC):** `200 {"status":"ok"}` if the decrypted bytes end with **valid
  PKCS#7 padding**, `403 {"error":"bad padding"}` if not. That yes/no is the **oracle**.
- **Fixed (`:8099`, GCM):** `200` only if the 128-bit tag verifies; `403` for **every** failure
  (bad base64, wrong length, wrong tag), checked **before** anything is decrypted.

1. **Look:** fetch the encrypted secret from `:8098` (`curl`).
2. **Ask three questions** with `ask.py`: the original (`200`), one letter changed at the **start**
   (still `200`: the first letter sits in the IV, so only one letter of the first block changes, as in Week 4, and the padding at the end is untouched),
   one letter changed near the **end** (`403`: the padding is broken). Where the change lands decides
   the answer. That is the leak.
3. **Let the script do it:** `exploit.py` asks the oracle a few thousand questions, in a few seconds,
   and prints the secret `msg:FLAG{...}`. It never uses the key.
4. **Confirm the fix:** the same three questions to `:8099` (GCM) give `200`, `403`, `403`; the
   script finds no usable signal and recovers nothing. This is evidence against **this** attack,
   not proof that everything else about the program is safe.

(Curious how the script works? The worksheet's optional Extension at the end of Part 2 has the one
formula, `D(C_t)[15] = guess XOR 0x01`. No student task needs it.)

## Run it

Run everything **inside** the container, so no Python is needed on your laptop:

```bash
cd {{ labpath }}
docker compose up -d                       # :8098 vulnerable, :8099 fixed
docker compose logs | grep "Running on"    # Mac; Windows: docker compose logs | findstr /C:"Running on"
                                           # wait for Running on http://127.0.0.1:8098 and :8099
docker compose exec vulnerable python ask.py vuln original    # 200 ok
docker compose exec vulnerable python ask.py vuln start       # 200 ok
docker compose exec vulnerable python ask.py vuln end         # 403 bad padding
docker compose exec vulnerable python ask.py fixed original   # 200
docker compose exec vulnerable python ask.py fixed start      # 403
docker compose exec vulnerable python ask.py fixed end        # 403
docker compose exec -e FIXED_HOST=fixed vulnerable python exploit.py              # PASS :8098 (secret) + PASS :8099
docker compose down
```

Keep `-e FIXED_HOST=fixed` for `exploit.py`: inside the container the second copy of the site is at
`fixed`, not `localhost`. Without it `exploit.py` waits about a minute and prints
`FAIL: fixed app never came up`. (`ask.py` finds the GCM server by itself, so it does not need it.) (You can also run the
scripts on the host if you have Python 3 with `requests`; then `-e FIXED_HOST=fixed` is not needed.)

`ask.py` is a small helper for this lab: it fetches `/secret`, changes **one letter** (or none),
sends the result to `/decrypt`, and prints the server's answer. It uses only the standard library
and never sees a key.

Flag configuration: the shared demo flag is fine. Every student's run shows the same ciphertext
because the lab uses a fixed key and nonce **for this demo only**: it encrypts exactly one message.
Real systems must never repeat a nonce under a key. Record the value from your own run with your own
evidence and explanation; no personal flag is required this week.

**Verified (2026-11-09):** every command in `worksheet.md` was run in order against freshly started
containers on this machine. The CBC secret is 88 base64 characters (IV + 3 blocks) and the GCM one
84. CBC: the original and the start change answer `200 ok`, the end change answers `403 bad
padding`. GCM: the original answers `200`, the start and end changes both answer `403 decryption
failed`. `exploit.py` took about 3.4 seconds, printed the three blocks and
`Recovered plaintext: b'msg:FLAG{padding_oracle_leaks_all}'`, then both `PASS` lines; `docker
compose down` removes both containers. Not run on Windows.

## Deliverable

Submit the common evidence and reasoning (60) plus only the assigned Conventional (40)
or AIR-Sec (40) format. The details below describe the common artifact; the worksheet
identifies the alternative sections.
The server answers for the three CBC questions and the three GCM questions, the recovered secret
and the two `PASS` lines from `exploit.py`, the two code lines that differ (`pkcs7_valid(plaintext)`
vs `_aesgcm.decrypt(...)`), and a short note saying why a yes/no answer leaked the secret on CBC and
why GCM did not. Full tasks: `worksheet.md`.

## References
- RFC 5116 — *An Interface and Algorithms for Authenticated Encryption* (§2: what AEAD gives and
  what associated data is).
- RFC 5652 §6.3 — the PKCS#7 padding rule (pad with the number of bytes added).
- RFC 8446 §1.2 — TLS 1.3 keeps only AEAD algorithms for record protection.
- Vaudenay (2002), *Security Flaws Induced by CBC Padding* (Eurocrypt) — the first padding-oracle
  attack on CBC.
- NIST SP 800-38D — *Galois/Counter Mode (GCM) and GMAC*.
- CWE-204 (Observable Response Discrepancy): https://cwe.mitre.org/data/definitions/204.html
- Boneh & Shoup, *A Graduate Course in Applied Cryptography* (free online; a graduate text, so
  optional for the curious): https://crypto.stanford.edu/~dabo/cryptobook/
- https://en.wikipedia.org/wiki/Padding_oracle_attack
