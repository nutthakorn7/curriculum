# {{ slot_label }} — Load Balancing & Auto-Scaling Under Load

**Topic (source):** AWS Academy Cloud Foundations' load-balancer / auto-scaling-group lab topic
(target groups behind an ALB, an Auto Scaling Group reacting to CPU load), described here in our
own words — **not** copied from any AWS Academy file. **Kind:** HYBRID (Part 1 conceptual essay
+ Part 2 small lab).

**Concepts:** load balancer + target group + auto-scaling group relationship, min/max/desired
capacity, scaling triggers, unauthenticated/unthrottled endpoints as a cost and availability
risk · **Analogous CWE:** CWE-400 (Uncontrolled Resource Consumption). This general pattern is
sometimes called "Denial of Wallet" — an economic denial-of-service where the attacker's goal is
to inflate the victim's cloud bill (and/or starve capacity) rather than to crash the service
outright.

## This lesson — what to do
1. **Before class** — Docker Desktop working; complete the real AWS Academy load-balancing /
   auto-scaling lab in your Learner Lab sandbox first (that's still where you learn the actual
   ALB/target-group/ASG console UI).
2. **This add-on lab (45–60 min)** — a local, from-scratch simulation of the same auto-scaling
   concept: a tiny Flask service that stands in for "a fleet behind a load balancer," with an
   internal counter that plays the role of an Auto Scaling Group's `current_instances`. Kickoff:
   `docker compose up -d`.
3. **Submit** — worksheet → Classroom (Part 1 essay for everyone; Part 2 AIR-Sec students also
   submit the flag).

## Objectives
- Explain, in your own words, how a **load balancer**, its **target group(s)**, and an
  **Auto Scaling Group** work together to keep a fleet sized to demand.
- Explain why an Auto Scaling Group's **min/max capacity** bounds exist — both as an
  availability floor and as a **cost ceiling**.
- Identify why a publicly reachable, unauthenticated, unthrottled "trigger load" endpoint is a
  **security and cost** problem (CWE-400), not just a performance one — and why "just add rate
  limiting" or "just add auth" alone is each individually insufficient.

## Signature exercise — "Generate Load"
Two Flask targets simulate the same scaler; the only difference is what `POST /generate-load`
requires before it will accept a job:

| Service | Port | Auth required? | Rate limit? | Anonymous caller can reach `current_instances = 6`? |
|---|---|---|---|---|
| `vulnerable_app.py` | `:8109` | No | No | **Yes — in ~40 calls** |
| `fixed_app.py` | `:8110` | Yes (`X-Api-Key`) | Yes (5 calls/key) | **No — rejected at call 1 (401)**; even a *correctly-keyed* caller is capped at 5 calls, well short of the ~40 needed |

**Why it's exciting:** you don't need to exploit a code bug — the endpoint does exactly what it
was built to do. The vulnerability is that *nothing* gates who can call it or how often, so a
trivial `for` loop from an anonymous script is enough to force expensive scaling events. This is
the same shape as real "Denial of Wallet" incidents where a public, unauthenticated endpoint
that triggers paid cloud resources (compute, storage, third-party API calls) gets hammered by a
script and runs up a large bill before anyone notices.

1. **Baseline:** `GET /status` on either app shows `current_instances` starting at 2 (the
   simulated ASG's minimum), `load_units` at 0.
2. **The attack:** loop `POST /generate-load` with no headers at all against the vulnerable app.
   Every 10 `load_units` triggers +1 instance (capped at the simulated ASG max of 6). By call
   ~40, `current_instances` hits 6 and the response includes the flag.
3. **Confirm the fix:** the identical anonymous loop against the fixed app is rejected
   immediately (`401 Unauthorized` — no `X-Api-Key` header). Even supplying the correct key only
   buys 5 calls before `429 Too Many Requests` — nowhere near enough to reach max capacity. That
   empirically proves this needs **both** auth *and* a throttle: auth alone still lets a
   legitimate-but-compromised or careless key hammer the endpoint; a throttle alone still lets
   any anonymous caller through.

## Run it
```bash
cd {{ labpath }}
docker compose up -d          # vulnerable_app.py on :8109, fixed_app.py on :8110
pip install requests          # once, on the host
python exploit.py
```
Expect two `PASS` lines and exit `0`: the vulnerable app reaching max instances (6) and
returning the flag in well under 100 anonymous calls, and the fixed app rejecting the anonymous
caller (401) before it can accumulate any meaningful load.

**Verified:** `docker compose up -d --build` was run on this machine; `exploit.py` ran from the
host against the published ports. Real captured output:
```
=== VULNERABLE (no auth, no rate limit) (http://localhost:8109) ===
[*] call 40: anonymous POST /generate-load -> 200 {'current_instances': 6, 'flag': 'FLAG{denial_of_wallet_no_throttle}', 'load_units': 40, 'max_instances': 6, 'min_instances': 2, 'status': 'job-accepted'}
PASS: anonymous caller drove current_instances to 6 in 40 calls on the vulnerable app, flag = FLAG{denial_of_wallet_no_throttle}

=== FIXED (X-Api-Key required + rate limit) (http://localhost:8110) ===
[*] call 1: anonymous POST /generate-load -> 401 {'error': 'Unauthorized', 'reason': 'missing or invalid X-Api-Key'}
PASS: anonymous caller correctly REJECTED on the fixed app (401) after 1 call(s), no flag, fleet never reached max instances
```
Exit code `0`. Additional negative-control check performed separately (not part of
`exploit.py`'s asserted path, but worth demonstrating in class): calling the fixed app **with**
the correct `X-Api-Key` still gets capped — 5 successful calls (`current_instances` stays at 2,
`load_units` stops at 5), then a `6th` call returns `429 {"error": "TooManyRequests", ...}`. This
is the defense-in-depth proof: the fix is auth **and** a throttle together, not either one alone.

Per-student flag: run `python3 instructor/seed_flags.py env <STUDENT_ID>` — this course's own
`instructor/seed_flags.py` already exists and its `CHALLENGES` list already includes `"scaling"`.
Without it, `FLAG_SCALING` defaults to `FLAG{denial_of_wallet_no_throttle}` and can be overridden:
`FLAG_SCALING=FLAG{...} docker compose up`.

**Evidence artifact.** The attributable evidence is the captured `flag` value returned by the
*vulnerable* app once `current_instances` reaches 6. The fixed app never returns it. Submitting
another student's flag is a violation.

## Deliverable
The captured flag + the exact request pattern (endpoint, headers-or-lack-thereof, approximate
call count) that produced it + a one-paragraph explanation of why "no rate limit and no
authentication" on a load-generating endpoint is a security problem even though the endpoint
itself has no memory-safety bug or injection flaw — the vulnerability is entirely in what the
endpoint *doesn't check* before doing expensive work.

## References
- AWS Elastic Load Balancing documentation — *What is a target group?*, *Application Load
  Balancer components* (publicly available, general concept — no AWS Academy file used or
  copied).
- AWS Auto Scaling documentation — *Auto Scaling group concepts*, specifically minimum, maximum,
  and desired capacity, and scaling policies (publicly available, general concept only).
- OWASP — *API4:2023 Unrestricted Resource Consumption* (general, publicly documented concept
  matching this lesson's endpoint design).
