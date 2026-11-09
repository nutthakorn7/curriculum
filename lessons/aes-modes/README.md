# {{ slot_label }} — AES / Block-Cipher Modes: CBC vs GCM

**Kind:** LAB
**Concepts:** AES block cipher, ECB/CBC/GCM modes, IV vs. nonce, malleability, authenticated
encryption (AEAD) · **Analogous CWE:** CWE-353 (Missing Support for Integrity Check), CWE-649
(Reliance on Obfuscation/Encryption Without Integrity)

## This week — 100-minute class and assigned assessment

1. **Before class** — install **Docker** and run `docker compose up -d` once at home (the image is
   downloaded the first time, and the containers install packages every time they start, so you
   need internet each time). The lab script runs *inside* the container, so you
   do **not** need Python on your own laptop. Read the Week 3 recap.
2. **In class (100 minutes)** — 10-minute Week 3 quiz + short brief + guided lab (change an
   encrypted token, let the script turn it into `admin`, see GCM refuse the same kind of change) +
   debrief + evidence capture. Slides: `{{ slides }}`. The CryptoVault team and design-plan
   milestone is also handled in this class: teams review the KDF + AEAD design plan and submit it as the
   project brief says. It is a project item, not part of the worksheet.
3. **Common work (60 points)** — see that the server does not notice a change to a CBC token, run
   `exploit.py` to turn `guest` into `admin`, then show that the GCM copy refuses a changed token.
   Explain why.
4. **Assigned format (40 points)** — complete **either** the Conventional written questions
   **or** AIR-Sec (Audit the AI 20 + EiPE 10 + Prompt Problem 10). Both versions total 100.
   Viva checks support feedback/authenticity within the criteria; they add no separate marks.
5. **After class** — finish the explanations and the assigned format. Submit the worksheet
   PDF and required evidence according to [SUBMISSION.md](../../SUBMISSION.md). This week
   has no separate code-fix/GitHub submission.

## Objectives
- Say why **AES itself being secure** does not make an AES-based scheme secure: the **mode**
  (ECB/CBC/GCM) and whether the data is **checked for changes** decide it.
- See that an unauthenticated AES-CBC token can be **changed without the key**, and that the server
  does not notice.
- Explain in plain words why **authenticated encryption** (AES-GCM here) refuses a changed token:
  it checks a **tag**.
- Name two mode pitfalls that are *not* in this week's exploit: ECB repeating patterns, and reusing
  an IV or nonce.

## 🔓 Token game — "Flip Your Way to Admin"
Two Flask targets, same endpoints, different token scheme:

| Service | Port | Token scheme | Changed token noticed? |
|---|---|---|---|
| `vulnerable_app.py` | `:8096` | `base64(IV ‖ AES-256-**CBC**(plaintext))` — **no MAC/tag** | **No** |
| `fixed_app.py` | `:8097` | `base64(nonce ‖ AES-256-**GCM**(plaintext) ‖ tag)` — AEAD | **Yes** (`403`) |

`GET /login` gives a session token for `role=guest`. `GET /whoami` decrypts it and reports the role.
`GET /admin` returns the flag only if the role is `admin`.

1. **Look:** log in on `:8096`, ask `/whoami`, try `/admin` (refused for a guest).
2. **Edit the first letter:** replace the first letter of the token with `A` (or `B` if it already
   is `A`); replace it, do not insert one. The CBC server still answers `guest`: it did not notice.
   (Other positions can give a different role or an error; the first letter is the safe one.)
3. **Let the script do it:** `exploit.py` changes the encrypted token so the server reads `admin`
   and returns the flag, without ever knowing the key.
4. **Confirm the fix:** the same kind of change on a `:8097` (GCM) token is refused:
   `{"error":"invalid or tampered token"}` (`403`).

(Curious how the script changes the token? Read the comments at the top of `vulnerable_app.py` and
in `exploit.py`. The worksheet does not ask you to do it by hand.)

## Run it

Run the script **inside** the container, so no Python is needed on your laptop:

```bash
cd {{ labpath }}
docker compose up -d                       # :8096 vulnerable, :8097 fixed
docker compose logs | grep "Running on"    # Mac; Windows: docker compose logs | findstr /C:"Running on"
                                           # wait for Running on http://127.0.0.1:8096 and :8097
docker compose exec -e FIXED_HOST=fixed vulnerable python exploit.py   # PASS :8096 (flag) + PASS :8097 (rejected)
```

Keep `-e FIXED_HOST=fixed`: inside the container, the second copy of the site is at `fixed`, not
`localhost`. Without it the script waits about a minute and prints `FAIL: fixed app never came up`. (You can also run `python exploit.py` on the host if you have Python 3 with
`requests`; then `-e FIXED_HOST=fixed` is not needed.)

Flag configuration: the shared demo flag is fine — record the value from your own run with your
own evidence and explanation; no personal flag is required this week.

**Verified (2026-11-09):** every command in `worksheet.md` was run in order against freshly started
containers on this machine. A login gives a 64-character CBC token and an 80-character GCM token;
`/whoami` answers `guest`; changing the first letter of the CBC token still answers `guest` while the
same change on the GCM token answers `invalid or tampered token` (403); `exploit.py` prints both
`PASS` lines and exits `0`; `docker compose down` removes both containers. Not run on Windows.

## Deliverable

Submit the common evidence and reasoning (60) plus only the assigned Conventional (40)
or AIR-Sec (40) format. The details below describe the common artifact; the worksheet
identifies the alternative sections.
Your token and `/whoami` replies, the reply after you changed a letter (CBC and GCM), the script
lines that show `guest` becoming `admin`, the two `PASS` lines, and a short note saying why the CBC
server accepted a changed token and why GCM did not. Full tasks: `worksheet.md`.

## References
- NIST SP 800-38A (block-cipher modes: ECB/CBC/…) and SP 800-38D (GCM).
- RFC 5116 — *An Interface and Algorithms for Authenticated Encryption* (AEAD).
- Boneh & Shoup, *A Graduate Course in Applied Cryptography* (free online; a graduate text, so
  optional for the curious): https://crypto.stanford.edu/~dabo/cryptobook/
- https://en.wikipedia.org/wiki/Malleability_(cryptography) and
  https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation
