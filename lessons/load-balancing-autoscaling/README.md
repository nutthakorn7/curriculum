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
1. **Before Week 09 class** — make sure Docker Desktop works, study Cloud Foundations Module 10,
   and complete its Knowledge Check after learning. Open the assigned AWS load-balancing and
   auto-scaling lab so you are ready to run it during class.
2. **Week 09 class** — complete the AWS lab in your Learner Lab sandbox first; that is where you
   learn the actual ALB, target-group and ASG console workflow. Then start this local simulation
   with the **Step-by-step** below (`docker compose up -d --build`). Its Flask counter stands in
   for an Auto Scaling Group's `current_instances`; it does not create real AWS capacity.
3. **Week 10 and submission** — finish your assigned Part and submit the Local05 Answer Sheet in
   Classroom by its posted deadline. The Conventional room does Part 1; the AIR-Sec room does
   Part 2 and submits the request/response evidence. See [SUBMISSION.md](../../SUBMISSION.md).

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
| `fixed_app.py` | `:8110` | Yes (`X-Api-Key`) | Yes (per-key call cap) | **No — rejected at call 1 (401)**; even a correctly keyed caller reaches the cap well before the ~40 calls needed |

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
   buys a bounded number of calls before `429 Too Many Requests` — nowhere near enough to reach max capacity. That
   empirically proves this needs **both** auth *and* a throttle: auth alone still lets a
   legitimate-but-compromised or careless key hammer the endpoint; a throttle alone still lets
   any anonymous caller through.

## Step-by-step (copy these commands)
**First, get this lab onto your computer.** You need your own copy of the course files. You download them once, then update them each
time. Open a terminal (Terminal on macOS or Linux, **Git Bash** on Windows) and do
A, B and C in order. You installed Git in the Week 01 setup; if `git` is "not found", do that
setup first.

A. **Download the course files (first time only).** Skip this if you already did it in Week 01.
   ```bash
   cd ~
   git clone https://github.com/nutthakorn7/cloud-infrastructure-security.git
   ```
   You should see `Cloning into 'cloud-infrastructure-security'...` and no error. If it says
   `already exists`, you have the files already: go on to B.

B. **Get the newest version (every time).** The course files change during the term, so do this
   even if you downloaded them last week. Your answers stay in Classroom; update the repo before each lab.
   ```bash
   cd ~/cloud-infrastructure-security
   git pull
   ```
   You should see `Already up to date.` or a list of changed files. If you see
   `No such file or directory`, your copy is in another folder: do A to make a new one here. If you
   see `Your local changes to the following files would be overwritten`, stop and ask the
   instructor for help syncing your copy. Do not discard your local changes blindly.

C. **Go into this lab's folder and check it.**
   ```bash
   cd {{ labpath }}
   ls
   ```
   You should see `README.md`, `worksheet.md` and `docker-compose.yml` among the files. Every
   command below runs from this folder. If you open a new terminal later, do B and C again first.

Run these in a terminal inside this lab folder: Terminal on macOS or Linux, or **Git Bash** on
Windows (it comes with Git). Each step says what you should see. Do them in order: both apps
remember every call until they restart.

0. **No private setup:** this public lab runs without a personal `.env` or an instructor message.
   The `flag` field is a shared demonstration marker, not proof of identity. Submit the complete
   request and vulnerable/fixed responses plus your explanation.

1. **Start both apps.** The first run downloads and builds the image, so it can take a few
   minutes.
   ```bash
   docker compose up -d --build
   ```
   When it finishes, wait about 10 seconds for the apps to start.
2. **Check that both apps are running.** If you see only `HTTP 000`, the apps are still starting:
   wait a few seconds and run the command again.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8109/ping
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8110/ping
   ```
   You should see `{"mode":"vulnerable","status":"ok"}` and then `{"mode":"fixed","status":"ok"}`,
   each followed by `HTTP 200`.
3. **Look at the starting size of each fleet.**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8109/status
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8110/status
   ```
   Both should show `"current_instances":2,"load_units":0` (2 is the minimum) and `HTTP 200`.
4. **The attack:** send 40 load requests to the vulnerable app with no key and no headers at
   all. The loop prints the call number in front of each answer.
   ```bash
   for i in $(seq 1 40); do printf 'call %s: ' "$i"; curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8109/generate-load; done
   ```
   Watch `current_instances` grow from 2 by one every 10 calls (`load_units` 10, 20, 30, 40). On
   call 40 it reaches 6 (the maximum) and the answer contains `"flag":"FLAG{...}"` and `HTTP 200`. Record
   the complete response, loop command, and call number; the marker is shared.
5. **Check the vulnerable fleet now.**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8109/status
   ```
   You should see `"current_instances":6,"load_units":40`: an anonymous script pushed the fleet
   to its most expensive size.
6. **The same request on the fixed app, with no key:**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8110/generate-load
   ```
   You should see `{"error":"Unauthorized","reason":"missing or invalid X-Api-Key"}` and
   `HTTP 401`, with no flag.
7. **The fixed app with the valid API key.** The key is set in this lab's `docker-compose.yml`
   (`API_KEY`). This loop sends 8 requests with it:
   ```bash
   for i in $(seq 1 8); do printf 'call %s: ' "$i"; curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8110/generate-load -H 'X-Api-Key: s3cret-scaling-key'; done
   ```
   The first calls show `"status":"job-accepted"` and `HTTP 200`. Then the answers change to
   `{"error":"TooManyRequests",...}` and `HTTP 429`. Count how many calls were accepted before
   the first `429`, and copy the `429` message: you need both for the worksheet (2a and 2c).
8. **Check the fixed fleet now.**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8110/status
   ```
   Compare `current_instances` here with what you saw in step 5.
9. **Stop the apps when you finish.**
   ```bash
   docker compose down
   ```

Both apps keep their counters in memory. If you run the steps a second time, the vulnerable app
returns the flag on the first call and the fixed app answers `429` straight away. To start again
from the beginning, run `docker compose restart vulnerable fixed`. If a step doesn't match, check
that Docker Desktop is running and that you are in this lab folder, then ask in class.

## Optional self-check
The Step-by-step above needs only Docker and `curl`. If you also want to run `exploit.py`, install
its Python dependency in a virtual environment inside this lab folder (`.venv/` is ignored by Git).

macOS or Linux:
```bash
python3 -m venv .venv
.venv/bin/python -m pip install requests
.venv/bin/python exploit.py
```
Windows Git Bash (with the Python launcher installed):
```bash
py -3 -m venv .venv
.venv/Scripts/python.exe -m pip install requests
.venv/Scripts/python.exe exploit.py
```
`exploit.py` runs the main checks in one go (an optional self-check, not a replacement for the
steps above). Run it on freshly started apps (`docker compose
restart vulnerable fixed` first). Expect two `PASS` lines and exit `0`: the vulnerable app
reaching max instances (6) and returning the flag in well under 100 anonymous calls, and the fixed
app rejecting the anonymous caller (401) before it can accumulate any meaningful load.

**Verified (2026-11-08; revised commands retested 2026-11-12 on macOS):** The "get this lab" commands (A, B and C) were run as written on 2026-11-08, in bash and in zsh, on a fresh clone. `docker compose up -d --build` was run on this machine (macOS) and
every command in Step-by-step was run as written in bash; the step 4 loop was also run in zsh,
the macOS default shell. Windows Git Bash was not tested. The optional environment override was tested; `docker compose restart vulnerable fixed` returned
both apps to `current_instances` 2, `load_units` 0. `exploit.py` then ran from the host against
the published ports and printed the same lines as before. On 2026-11-12, the revised step 4 loop
showed `HTTP 200`, and the virtual-environment self-check returned two `PASS` lines. Real captured
output, flag value masked:
```
=== VULNERABLE (no auth, no rate limit) (http://localhost:8109) ===
[*] call 40: anonymous POST /generate-load -> 200 {'current_instances': 6, 'flag': 'FLAG{...}', 'load_units': 40, 'max_instances': 6, 'min_instances': 2, 'status': 'job-accepted'}
PASS: anonymous caller drove current_instances to 6 in 40 calls on the vulnerable app, flag = FLAG{...}

=== FIXED (X-Api-Key required + rate limit) (http://localhost:8110) ===
[*] call 1: anonymous POST /generate-load -> 401 {'error': 'Unauthorized', 'reason': 'missing or invalid X-Api-Key'}
PASS: anonymous caller correctly REJECTED on the fixed app (401) after 1 call(s), no flag, fleet never reached max instances
```
Exit code `0`. Additional negative-control check performed separately (not part of
`exploit.py`'s asserted path, but worth demonstrating in class after students answer 2c): calling
the fixed app **with** the correct `X-Api-Key` reaches its configured per-key cap and then returns
`429 {"error": "TooManyRequests", ...}`. This
is the defense-in-depth proof: the fix is auth **and** a throttle together, not either one alone.

**Shared demonstration marker.** No personal `.env` or individual flag is required. Any
`flag` printed by this simulation is a public example marker; it does not identify the student
and is not graded by itself. Submit the exact request or command, the complete relevant
vulnerable and fixed responses, and your own explanation of the security effect. The instructor
may ask you to reproduce and explain the result live. Do not use real credentials in evidence.

## Deliverable
The complete vulnerable/fixed response evidence + the exact request pattern (endpoint, headers-or-lack-thereof, approximate
call count) that produced it + a one-paragraph explanation of why "no rate limit and no
authentication" on a load-generating endpoint is a security problem even though the endpoint
itself has no memory-safety bug or injection flaw — the vulnerability is entirely in what the
endpoint *doesn't check* before doing expensive work. You may answer in Thai or English. Write
your answers on the **Local05 Answer Sheet** copy in Classroom and click Turn in (no PDF needed).

## References
- AWS Elastic Load Balancing documentation — *What is a target group?*, *Application Load
  Balancer components* (publicly available, general concept — no AWS Academy file used or
  copied).
- AWS Auto Scaling documentation — *Auto Scaling group concepts*, specifically minimum, maximum,
  and desired capacity, and scaling policies (publicly available, general concept only).
- OWASP — *API4:2023 Unrestricted Resource Consumption* (general, publicly documented concept
  matching this lesson's endpoint design).
