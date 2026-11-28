# {{ slot_label }} — Key Exchanges: MITM Against Unauthenticated Diffie-Hellman

**Topic (KOSEN68 source):** `Week5_Key Exchanges Questions.docx` · **Kind:** HYBRID
**Concepts:** Diffie-Hellman key exchange, active vs. passive attackers, machine-in-the-middle,
public-key authentication, forward secrecy · **Analogous CWE:** CWE-322 (Key Exchange without
Entity Authentication), CWE-300 (Channel Accessible by Non-Endpoint)

## This week — 100-minute class and assigned assessment

1. **Before class** — Prepare Docker and download the lab files before the contact block. Read the Week 4 recap.
2. **In class (100 minutes)** — 10 quiz/review + 10 brief + 60 shared practice/analysis +
   15 debrief + 5 evidence capture. The opening quiz reviews Week 4; the Week 5 quiz is
   taken at the start of Week 6. Slides: `{{ slides }}`.
3. **Common work (60 points)** — Run both DH topologies. Trace Relay's two independent handshakes, the intercepted message, and both authentication failures. Explain what the HMAC check changes and why fresh DH is still used. The worksheet guides this in 13 numbered steps: A1 relay reads the message (steps 1–4), A2 the HMAC check stops it (5–9), A3 why it works and its limits (10–12).
4. **Assigned format (40 points)** — complete **either** four short Conventional questions
   **or** AIR-Sec (Audit the AI 20 + EiPE 10 + Prompt Problem 10). Both versions total 100.
   Viva checks support feedback/authenticity within the criteria; they add no separate marks.
5. **After class** — finish the short explanations and assigned format. The group-validation
   questions are optional study only. Submit the worksheet
   PDF and required evidence according to [SUBMISSION.md](../../SUBMISSION.md). This week
   has no separate code-fix/GitHub submission.

## Objectives
- Explain why Alice and Bob need a *key exchange* rather than simply sending a symmetric key,
  and what an eavesdropper gains if they skip it.
- Trace a full Diffie-Hellman handshake (private exponent → public value → shared secret) and
  explain why the discrete-log problem makes the shared secret hard for an eavesdropper to
  recover.
- **Execute and observe** a full active machine-in-the-middle against unauthenticated DH: two
  independent handshakes, one attacker-controlled shared secret with each side, silent
  decrypt-relog-reencrypt of the traffic in between.
- Explain why authenticating the DH public keys (here: an HMAC under a pre-shared key) defeats
  that MITM, **without** giving up the property DH exists for in the first place (forward
  secrecy of the session key).
- Recognize that input validation is a separate concern; a small-subgroup attack is **not**
  demonstrated or assessed this week.

## 🕵️ Signature game — "The Silent Third Wheel"
Be the eavesdropper who becomes an active puppet-master: sit silently between Alice and Bob,
run your own DH handshake with each of them, and read their "secure" channel in the clear —
they never notice. Then watch a single HMAC tag over the public key shut you out completely,
with no other code change.

**Why it's exciting:** it's the one week where you get to be the invisible third wheel in
someone else's "private" conversation — and then feel exactly how thin that privacy was.

## How this maps to the DH / MITM concept

Three services, three roles, one shared 2048-bit MODP group (RFC3526 Group 14):

| Service | Role | What it does |
|---|---|---|
| `bob.py` | Server | Listens on `:5000`, does a DH handshake with whoever connects, decrypts one AES-GCM message, prints `BOB RECEIVED: <plaintext>`. |
| `alice.py` | Client | Connects to `PEER_HOST:PEER_PORT` (`relay`, **never** `bob` directly), does a DH handshake, encrypts a fixed message under the derived key, sends it. |
| `relay.py` | Attacker | Sits on the network path between Alice and Bob. In vulnerable mode it runs **two entirely independent DH handshakes** — one with Alice (posing as Bob), one with Bob (posing as Alice). Alice and Relay share the first secret; Bob and Relay share the second. Relay is the **only party holding both**. It decrypts Alice's message with the Alice-side key, logs it, then re-encrypts the same plaintext under the Bob-side key and forwards it on. |

The premise: **Alice's `PEER_HOST` is `relay`, not `bob`.** That is the whole lesson — over an
unauthenticated network, "whoever answers when I dial Bob's address" is not the same claim as
"Bob." Plain DH gives Alice and Bob a shared secret that no *eavesdropper* can compute (the
discrete-log problem), but it gives neither side any way to check *who* they just agreed that
secret with. An *active* attacker who can intercept and re-originate connections can simply run
the protocol twice and stand in the middle — invisibly, because both handshakes complete
successfully and no independently trusted authentication tag gets checked.

The fix (`SIGNED=1`) does **not** replace DH with sending a symmetric key directly — Alice and
Bob still run a fresh DH exchange every session. If the ephemeral DH secrets are erased,
later disclosure of `AUTH_KEY` alone does not reveal captured past session traffic. Each side
computes an HMAC **tag** over its DH public key under a pre-shared `AUTH_KEY` that `relay` does
not have, and verifies the peer's tag before deriving any session key. `relay` still *attempts*
the identical key-substitution attack — same code path, same two-handshake structure — but
without `AUTH_KEY` it cannot forge a valid tag for the public keys it substitutes, so Alice's and
Bob's own verification fails and both abort. (Production systems typically authenticate DH with
signatures/certificates rather than a shared secret — TLS and SSH both do this — but the
principle demonstrated here, *authenticate the exchange, don't just run it*, is the same one.)

**What this lab does *not* show:** a small-subgroup attack or the consequences of skipping
public-key validation. Those are optional study topics. The running demo is specifically
the key-substitution MITM.

## Run it

Start Docker Desktop and wait for **Engine running**. Download the course ZIP from
<https://github.com/nutthakorn7/security-cryptography> (**Code → Download ZIP**)
and extract it, unless your existing Week 4 ZIP already has this lab. Open
`security-cryptography-master/labs/week05-key-exchanges` in File Explorer (Windows)
or Finder (Mac). On Windows, right-click empty space and choose **Open in Terminal**
(or Shift-right-click → **Open PowerShell window here**). On Mac, open Terminal,
type `cd `, drag the lab folder into Terminal, then press Enter. Check that `dir`
(Windows) or `ls` (Mac) lists both `docker-compose.vulnerable.yml` and
`docker-compose.fixed.yml`. Run every command below from that lab folder; no host
Python installation is needed. The worksheet has the full beginner checklist.

Vulnerable mode — full, invisible MITM:
```bash
docker compose -f docker-compose.vulnerable.yml up --build
```
Expected log lines (interleaving/ports/IPs vary run to run — the container names and message
text do not):
```
week05-bob    | BOB: listening on 0.0.0.0:5000 (SIGNED=False)
week05-relay  | RELAY: listening on 0.0.0.0:5000, forwarding to bob:5000 (SIGNED=False)
week05-alice  | ALICE: connecting to relay:5000 (SIGNED=False)
week05-relay  | RELAY: completed independent DH handshake with Alice (posing as Bob)
week05-alice  | ALICE: sent encrypted message ('the launch code is 4471')
week05-relay  | RELAY: completed independent DH handshake with Bob (posing as Alice)
week05-relay  | RELAY INTERCEPTED: the launch code is 4471
week05-bob    | BOB RECEIVED: the launch code is 4471
```
Alice exits `0` once her message is sent; `bob` and `relay` are long-running servers — stop the
stack with `Ctrl-C` then tear it down:
```bash
docker compose -f docker-compose.vulnerable.yml down
```

Fixed mode — HMAC-authenticated DH public keys:
```bash
docker compose -f docker-compose.fixed.yml up --build
```
Expected log lines:
```
week05-bob    | BOB: listening on 0.0.0.0:5000 (SIGNED=True)
week05-relay  | RELAY: listening on 0.0.0.0:5000, forwarding to bob:5000 (SIGNED=True)
week05-alice  | ALICE: connecting to relay:5000 (SIGNED=True)
week05-relay  | RELAY: (fixed mode) attempted DH substitution with Alice (posing as Bob)
week05-alice  | AUTH FAILED - ABORTING
week05-relay  | RELAY: (fixed mode) attempted DH substitution with Bob (posing as Alice)
week05-bob    | AUTH FAILED - ABORTING
```
Both `alice` and `bob` exit `1`. There is **no** `RELAY INTERCEPTED` line anywhere in this mode's
logs — that absence is your evidence the fix worked. Tear down the same way:
```bash
docker compose -f docker-compose.fixed.yml down
```

No environment variables need to be set by hand — which compose file you point `-f` at is the
*only* thing that selects vulnerable vs. fixed mode (`SIGNED`/`AUTH_KEY` are baked into each
file's `environment:` block). This deliberately avoids an earlier design bug an advisor review
caught: a single-file/`--profile` scheme where `--profile fixed` could silently still run
vulnerable behavior unless `SIGNED=1` was also exported by hand.

## Verified

Both modes were Docker-tested against the actual files in this directory, independently, twice:
once by the colleague who built this lab (`docker compose -f <file> up --build`, no env-var
overrides, run fresh from a scratchpad copy and torn down after) and once again while writing
this README (`docker compose -f <file> up --build --abort-on-container-exit`, run fresh from
this directory, `down` + images removed after each mode).

- **Vulnerable:** both runs printed `RELAY: completed independent DH handshake with Alice
  (posing as Bob)`, `RELAY: completed independent DH handshake with Bob (posing as Alice)`,
  `RELAY INTERCEPTED: the launch code is 4471`, and `BOB RECEIVED: the launch code is 4471`, in
  that relative order, with `alice` exiting `0`.
- **Fixed:** both runs printed `AUTH FAILED - ABORTING` from **both** `alice` and `bob` (exit
  code `1` each), `RELAY: (fixed mode) attempted DH substitution with Alice (posing as Bob)` and
  the matching line for Bob, and **zero** occurrences of `RELAY INTERCEPTED` — confirmed with
  `docker compose -f docker-compose.fixed.yml logs | grep -c "RELAY INTERCEPTED"` returning `0`
  on both runs (Mac/Linux Terminal). On Windows PowerShell, use
  `(docker compose -f docker-compose.fixed.yml logs | Select-String -SimpleMatch "RELAY INTERCEPTED" | Measure-Object).Count`.
- Both stacks were torn down (`docker compose down`) and their built images removed after
  verification; nothing was left running.

## Deliverable

Submit the common evidence and reasoning (60) plus only the assigned Conventional (40)
or AIR-Sec (40) format. The details below describe the common artifact; the worksheet
identifies the alternative sections.
Worksheet 5: shared log evidence and control/limitations explanation (common 60), plus
either four short Part 2 questions (Conventional 40) or Audit-the-AI (Part 3), EiPE and Prompt
Problem (Part 4) tasks (AIR-Sec 20/10/10). The viva spot-check is formative/authenticity feedback.

## References
- RFC 3526, *More Modular Exponential (MODP) Diffie-Hellman groups for Internet Key Exchange
  (IKE)* — Group 14 (2048-bit) is the exact prime/generator used in `common.py`.
- Boneh & Shoup, *A Graduate Course in Applied Cryptography*, ch. 10 (Key Exchange) — covers
  authenticated vs. unauthenticated DH and active-attacker MITM; free online.
- NIST SP 800-56A Rev. 3, *Recommendation for Pair-Wise Key-Establishment Schemes Using Discrete
  Logarithm Cryptography* — public-key validation requirements (optional study).
- https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange#Man-in-the-middle_attack
