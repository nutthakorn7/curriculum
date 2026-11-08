# {{ slot_label }} — MACs: Hash-Only Cookies and Length-Extension

**Kind:** LAB
**Concepts:** message authentication codes, secret-prefix hashing, length-extension, HMAC
**Analogous CWE:** CWE-347 (Improper Verification of Cryptographic Signature), CWE-290
(Authentication Bypass by Spoofing)

## This week — 100-minute class and assigned assessment

1. **Before class** — install **Docker** and run `docker compose up -d` once at home (the first run
   downloads an image and installs packages). The lab script runs *inside* the container, so you
   do **not** need Python on your own laptop. Read the Week 2 recap.
2. **In class (100 minutes)** — 10-minute Week 2 quiz + short brief + guided lab (try to change a
   signed cookie, run the forgery, show HMAC stops it) + debrief + evidence capture. Slides: `{{ slides }}`.
3. **Common work (60 points)** — see the signature catch a change made by hand, run `exploit.py` to
   get the flag from the secret-prefix copy, then show the same script is refused by the HMAC copy.
   Explain why.
4. **Assigned format (40 points)** — complete **either** the Conventional written questions
   **or** AIR-Sec (Audit the AI 20 + EiPE 10 + Prompt Problem 10). Both versions total 100.
   Viva checks support feedback/authenticity within the criteria; they add no separate marks.
5. **After class** — finish the explanations and the assigned format. Submit the worksheet
   PDF and required evidence according to [SUBMISSION.md](../../SUBMISSION.md). This week
   has no separate code-fix/GitHub submission.

## Objectives
- Say what a MAC gives you that a plain hash does not, and why it needs a secret key.
- Explain why `SHA256(key + message)` is **not** a safe MAC, and see a forgery succeed against a
  local target without the secret.
- Explain in plain words why HMAC stops that forgery, and verify it by running the same script
  against a fixed target.
- Name two things HMAC does not fix by itself: non-constant-time comparison and replay.

## 🔓 Signature game — "Forge the Admin Cookie"
Two Flask targets, same endpoints, different signature scheme:

| Service | Port | Signature scheme | Should the forgery work? |
|---|---|---|---|
| `vulnerable_app.py` | `:8092` | `sig = SHA256(MAC_SECRET + data)` (secret-prefix hash) | **Yes** |
| `fixed_app.py` | `:8093` | `sig = HMAC-SHA256(MAC_SECRET, data)` | **No** |

Both accept usernames of 1–64 ASCII letters, digits, `_`, `.` or `-`; malformed names
return `400` before any cookie is issued. Both issue a cookie at `GET /login?user=<name>` encoding
`data="user=<name>&admin=false"` plus a signature. `GET /admin` recomputes the signature and, if it
matches **and** `data` contains `admin=true`, returns the flag.

1. **Look:** log in as `guest` against `:8092` and read the `data`/`sig` cookies.
2. **Change it by hand:** set `admin=true` and keep the old `sig` → refused (`bad signature`).
3. **Forge:** run `exploit.py` → accepted, flag, without ever learning `MAC_SECRET`.
4. **Confirm the fix:** the same script against `:8093` (HMAC) → refused (`403`, no flag).

Both apps use a demo secret of **exactly 16 ASCII bytes**. `exploit.py` is told the secret's
*length* but never its *value*.

## Run it

Run the script **inside** the container, so no Python is needed on your laptop:

```bash
cd {{ labpath }}
docker compose up -d                       # :8092 vulnerable, :8093 fixed
docker compose logs                        # wait for Running on http://127.0.0.1:8092 and :8093
docker compose exec -e FIXED_HOST=fixed vulnerable python exploit.py   # PASS :8092 (flag) + PASS :8093 (rejected)
```

Keep `-e FIXED_HOST=fixed`: inside the container, the second copy of the site is at `fixed`, not
`localhost`. (You can also run `python exploit.py` on the host if you have Python 3 with
`requests`; then `-e FIXED_HOST=fixed` is not needed.)

Flag configuration: the shared demo flag is fine — record the value from your own run with your
own evidence and explanation; no personal flag is required this week.

**Verified (2026-11-08):** every command in `worksheet.md` was run in order against freshly started
containers on this machine. The hand-changed cookie returned `bad signature`, `exploit.py` printed
both `PASS` lines and exited `0`, and `docker compose down` removed both containers. Not run on
Windows.

## Deliverable

Submit the common evidence and reasoning (60) plus only the assigned Conventional (40)
or AIR-Sec (40) format. The details below describe the common artifact; the worksheet
identifies the alternative sections.
The captured flag + the `bad signature` reply from your hand-changed cookie + a short note saying
why the forgery worked against `:8092` and why HMAC stopped it. Full tasks: `worksheet.md`.

## References
- Boneh & Shoup, *A Graduate Course in Applied Cryptography*, ch. 6 (MACs) — free online.
- RFC 2104 — *HMAC: Keyed-Hashing for Message Authentication*.
- https://en.wikipedia.org/wiki/Length_extension_attack
- NIST FIPS 198-1 — *The Keyed-Hash Message Authentication Code (HMAC)*.
