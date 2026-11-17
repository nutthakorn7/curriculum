# {{ slot_label }} — User Authentication: The Server Sees Your Password (Unless It Can't)

**Topic (course-plan):** User Authentication · **Kind:** HYBRID
**Concepts:** password submission vs. challenge-response / PAKE, verifier storage, authentication
factors, TOTP vs. FIDO2, credential stuffing, delegated authentication (SSO/OIDC) ·
**Analogous CWE:** CWE-522 (Insufficiently Protected Credentials) and CWE-532 (Insertion
of Sensitive Information into Log File). The lab uses HTTP inside a local Docker network;
CWE-319 describes that unencrypted transport, not a server receiving plaintext after TLS termination.

## 100-minute class and assigned worksheet version

**In class:** 10 min Week 13 retrieval quiz/review + 10 min brief explanation + 60 min practice/analysis + 15 min debrief + 5 min evidence capture = 100 min. The scored Week 14 quiz opens in Week 15, after this lesson.

**Shared core — every student:** Run password-submission and challenge-response scenarios; capture successful login and the log differences; explain replay protection, verifier theft and the limits of this simplified protocol.

**Preparation and extensions:** Prepare images and read the authentication overview. Complete the full factor/MFA/SSO essays or AIR-Sec critique/EiPE/Prompt outside the core block as needed.

**Assessment:** everyone completes the shared core (60 points) plus **one assigned version** (40 points): Conventional written analysis, or AIR-Sec Audit-the-AI 20 + EiPE 10 + Prompt Problem 10. Both versions total 100. All questions remain available; complete the assigned version's full questions, using out-of-class time for extended responses. The other version is ungraded reference practice, not an additional requirement. Viva/micro-demo questions are formative checks of the submitted explanation, with no separate points or automatic pass/fail score gate.

**Evidence:** record reproducible observations or reasoning and your name/student ID. Where the local target prints a shared placeholder flag, record it as observed; a personalized flag or live CTFd account is not a prerequisite. Follow SUBMISSION.md for the announced hand-in channel.

## This week — what to do
1. **Before class** — Docker Desktop working (same Docker-first setup as `software-security` and
   this course's earlier weeks); skim the Week 2 password-hashing recap (you will reuse "store a
   verifier, never the password").
2. **Concept preparation and brief explanation (within the 100-minute plan)** — Week 13 retrieval quiz first (~10 min), then the lecture: why "log in by sending
   your password" hands the plaintext to the *server*, and what a challenge-response / PAKE buys
   you. Slides: `slides/week14.md`.
3. **Practice and assigned-version work (core in class; extensions outside class)** — run the demo in both modes below, then complete **Worksheet 14**
   (`worksheet.md`, shared lab evidence plus the assigned Conventional essays or AIR-Sec Audit-the-AI, EiPE and Prompt Problem).
4. **Submit** — shared-core evidence/reasoning plus your assigned 40-point version in the worksheet PDF via [SUBMISSION.md](../../SUBMISSION.md). Include the observed flag/log artifact where applicable. Supplied exploit/reference code does not require an unchanged GitHub commit.

## Objectives
- Explain why sending a password to the server is a risk **even over TLS** — TLS protects the
  *wire*, but the server *terminates* the TLS and therefore holds your plaintext password; a
  malicious, compromised, or merely over-logging server harvests it.
- **Execute and observe** the difference: in plain-password mode the server logs
  `SERVER SAW PASSWORD: correct-horse-battery`; in challenge-response mode the server logs only a
  nonce and a proof (`SERVER SAW: nonce=... proof=...`) and the password appears **nowhere in the fixed-mode server logs**, yet
  the client still authenticates (`LOGIN OK`).
- Explain how this toy challenge-response accepts possession of a password-derived verifier
  *without* transmitting the password in the login request, and how the server checks a proof
  using its preloaded `v = KDF(salt, password)`. A thief with `v` can impersonate the client.
- Distinguish the three authentication factors (know / have / are) and reason about TOTP,
  FIDO2/WebAuthn, credential stuffing, and delegated authentication (SSO/OIDC) — the conceptual
  half of this HYBRID week (Conventional Q4 on paper; optional Q5–Q8 for early finishers).
- **Understand the honest limits of this demo** (see the box below): the fixed side proves only
  *"password never transmitted."* It is **not** a full PAKE.

## 🗝️ Signature game — "Never Say the Password"
Play server operator and catch your own login system handing you the plaintext password on a
silver platter, sitting right there in your logs. Then flip on challenge-response and log in
successfully **without sending the password in the login exchange**. Compare the server log
and inspect the client request code to see both sides of that claim.

**Why it matters:** the login succeeds while the fixed-mode server log contains no plaintext
password. A "Sign in with..." button is usually delegated authentication
through an identity provider; it does not imply this challenge-response protocol.

## How this maps to the concept

Two services, one network:

| Service | Role | What it does |
|---|---|---|
| `server.py` | Flask auth server | Listens on `:8080`. Behaviour set by env var `PAKE`. **Vulnerable** (`PAKE` unset): `POST /login {username, password}` — receives the plaintext password, **logs it** (`SERVER SAW PASSWORD: ...`), checks it. **Fixed** (`PAKE=1`): `GET /challenge` hands out a random nonce; `POST /login {username, nonce, proof}` — the server recomputes the proof from its **stored verifier** and logs only the nonce + proof, **never** the password. |
| `client.py` | Login client | Runs the flow that matches the mode and prints `LOGIN OK` on success. **Vulnerable:** puts the actual password in the request body. **Fixed:** fetches the nonce, derives `verifier = KDF(salt, password)` **locally**, sends `proof = HMAC(verifier, nonce)` — the password never leaves the client. |

The premise: **TLS is not the whole story.** TLS (which this demo omits for clarity — the lesson is
about the *server endpoint*, not the wire) would stop a network eavesdropper from reading the
password in transit. It does **nothing** about the fact that the server on the other end decrypts
the TLS and then holds your plaintext password in a request handler — free to log it, store it,
forward it, or leak it in a breach. Plain-password login trusts the server completely. A
challenge-response protocol reduces that trust for the login request: the client demonstrates possession of a password-derived verifier by
answering a fresh random challenge, and the server checks the answer against a **verifier**
`v = KDF(salt, password)` it can store without holding the plaintext in this fixed-mode server image. The password is never
transmitted in fixed-mode login, so its server log does not directly contain the plaintext password. This does not prevent offline guessing from a known-salt transcript, and a stolen verifier is directly usable for impersonation in this toy protocol.

> ### Honest scope — this fixed demo is NOT a full PAKE
> The simplified HMAC challenge-response shows that the login request omits the password and that a consumed challenge cannot simply be replayed. Its verifier is password-equivalent: theft permits direct impersonation, and a known-salt transcript or stolen fast verifier permits offline guessing.
>
> A real PAKE provides a mutually authenticated key exchange and resists offline guessing from protocol transcripts under its stated assumptions. **OPAQUE does not eliminate offline guessing after full server compromise**; it prevents pre-computation, and key stretching increases guess cost. Read [RFC 9807, Sections 1 and 10.11](https://www.rfc-editor.org/rfc/rfc9807.html#section-10.11). Keep transcript, credential-file and full-server compromise distinct.
>
> Do not present this toy protocol as SRP/OPAQUE, a production login design or phishing-resistant WebAuthn. Explain the actual observed property and its threat-model limits.

## Run it

Vulnerable mode — plain password login, server harvests the plaintext:
```bash
cd labs/week14-authentication
docker compose -f docker-compose.vulnerable.yml up --build --abort-on-container-exit
```
Expected log lines (timestamps/IPs vary run to run — the container names and the
`SERVER SAW PASSWORD` / `LOGIN OK` text do not):
```
week14-server  | SERVER: listening on 0.0.0.0:8080 (PAKE=False)
week14-client  | CLIENT: plain-password login to http://server:8080 as 'alice' (PAKE=False)
week14-server  | SERVER SAW PASSWORD: correct-horse-battery
week14-client  | LOGIN OK
```
`client` exits `0` once it authenticates; `server` is a long-running server. With
`--abort-on-container-exit` the stack stops as soon as `client` exits. Tear it down:
```bash
docker compose -f docker-compose.vulnerable.yml down
```

Fixed mode — challenge-response, password never transmitted:
```bash
docker compose -f docker-compose.fixed.yml up --build --abort-on-container-exit
```
Expected log lines (the `nonce`/`proof` hex values are random every run):
```
week14-server  | SERVER: listening on 0.0.0.0:8080 (PAKE=True)
week14-client  | CLIENT: challenge-response login to http://server:8080 as 'alice' (PAKE=True)
week14-server  | SERVER SAW: nonce=<32 hex chars> proof=<64 hex chars>
week14-client  | LOGIN OK
```
`client` still exits `0` (`LOGIN OK`) — authentication succeeded — but the fixed-mode
**server log** has no `SERVER SAW PASSWORD` line or `correct-horse-battery` string. Inspect
the request construction in `client.py` as well; log absence alone cannot prove that a secret
was never transmitted. Record the logs with commands that work in PowerShell and Mac Terminal:
```bash
docker compose -f docker-compose.fixed.yml logs server
docker compose -f docker-compose.fixed.yml logs client
```
The server output should show `SERVER SAW: nonce=... proof=...` and no plaintext password;
the client output should show `LOGIN OK`.
Tear down the same way:
```bash
docker compose -f docker-compose.fixed.yml down
```

Which compose file you point `-f` at is the **only** thing that selects vulnerable vs. fixed mode
(`PAKE` is baked into each file's `environment:` block for both `server` and `client`). No
environment variables need to be set by hand.

**The captured `SERVER SAW PASSWORD: correct-horse-battery` line (vulnerable mode) — submitted with
your attribution — is the attributable evidence artifact for this HYBRID week, in
place of a CTF flag.** For fixed mode, submit both log outputs and state that the server log
has no match for the password or `SERVER SAW PASSWORD`.

## Verified

Both modes were Docker-tested on Mac against a scratchpad copy of these files (OneDrive
placeholders can break `docker build` COPY in place). Each run used
`--abort-on-container-exit`; the stack was torn down after each mode.

- **Vulnerable:** the run printed `SERVER: listening on 0.0.0.0:8080 (PAKE=False)`,
  `CLIENT: plain-password login ... (PAKE=False)`, `SERVER SAW PASSWORD: correct-horse-battery`,
  and `LOGIN OK`, with `client` exiting `0`.
- **Fixed:** the run printed `SERVER: listening on 0.0.0.0:8080 (PAKE=True)`,
  `CLIENT: challenge-response login ... (PAKE=True)`, a single

```text
SERVER SAW: nonce=327decaec7e5d719846da41ed2c55010 proof=40e701177990a639995ceedb524305dacc1dfa6246484327f687426916b65b15
```

  line (hex random per run), and `LOGIN OK` — with `client` still exiting `0`.
  The fixed-mode server log contained no plaintext password and no `SERVER SAW PASSWORD` line.
- Both stacks were torn down (`docker compose down`) after verification; nothing was left running.

## Deliverable
Complete the shared core (60 points) and only the assigned version (40 points), as listed in the worksheet rubric. Include reproducible evidence/reasoning in your worksheet PDF. All unassigned-version questions remain available for ungraded practice.

## References
- OWASP *Authentication Cheat Sheet* and *Credential Stuffing Prevention Cheat Sheet* — controls,
  MFA guidance, and why not to log credentials.
- NIST SP 800-63B, *Digital Identity Guidelines — Authentication and Lifecycle Management* —
  authenticator types (memorized secrets, OTP, cryptographic/FIDO), verifier storage, phishing
  resistance.
- T. Wu, *The SRP Authentication and Key Exchange System* (RFC 2945), and [RFC 9807](https://www.rfc-editor.org/rfc/rfc9807.html), *OPAQUE* — distinguish transcript guessing, server compromise and pre-computation resistance.
- W3C *Web Authentication (WebAuthn) Level 2* — origin-bound, phishing-resistant FIDO2 credentials
  (contrast with TOTP).
- RFC 6238, *TOTP: Time-Based One-Time Password Algorithm* — how authenticator-app codes work (and
  why a phished code still works for the attacker).
