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
   internal counter that plays the role of an Auto Scaling Group's `current_instances`. Follow
   **Step-by-step** below (kickoff: `docker compose up -d --build`).
3. **Submit** — worksheet → see [SUBMISSION.md](../../SUBMISSION.md). The Conventional room does
   Part 1; the AIR-Sec room does Part 2 and also submits the flag.

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

## Step-by-step (copy these commands)
Run these in a terminal inside this lab folder: Terminal on macOS or Linux, or **Git Bash** on
Windows (it comes with Git). Each step says what you should see. Do them in order: both apps
remember every call until they restart.

0. **Your personal flag:** save your `.env` file in this folder first (see "Your personal flag"
   below). It is the same `.env` you got in your Classroom private comment for an earlier lab:
   one file works for every lab. Without it you capture the shared placeholder flag, which earns
   no marks.
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
   for i in $(seq 1 40); do printf 'call %s: ' "$i"; curl -s -X POST http://localhost:8109/generate-load; done
   ```
   Watch `current_instances` grow from 2 by one every 10 calls (`load_units` 10, 20, 30, 40). On
   call 40 it reaches 6 (the maximum) and the answer also contains `"flag":"FLAG{...}"`. That flag
   is yours: copy it into the worksheet, together with the loop command and the call number.
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

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build   # vulnerable_app.py on :8109, fixed_app.py on :8110
python3 -m pip install requests           # once, on the host
python3 exploit.py
```
`exploit.py` runs the main checks in one go (an optional self-check, not a replacement for the
steps above; the Step-by-step needs no Python). Run it on freshly started apps (`docker compose
restart vulnerable fixed` first). Expect two `PASS` lines and exit `0`: the vulnerable app
reaching max instances (6) and returning the flag in well under 100 anonymous calls, and the fixed
app rejecting the anonymous caller (401) before it can accumulate any meaningful load.

**Verified (2026-11-04):** `docker compose up -d --build` was run on this machine (macOS) and
every command in Step-by-step was run as written in bash; the step 4 loop was also run in zsh,
the macOS default shell. Windows Git Bash was not tested. Step 0 was tested with a stand-in `.env`,
and the captured flag changed to its value; `docker compose restart vulnerable fixed` returned
both apps to `current_instances` 2, `load_units` 0. `exploit.py` then ran from the host against
the published ports and printed the same lines as before. Real captured output, flag value masked:
```
=== VULNERABLE (no auth, no rate limit) (http://localhost:8109) ===
[*] call 40: anonymous POST /generate-load -> 200 {'current_instances': 6, 'flag': 'FLAG{...}', 'load_units': 40, 'max_instances': 6, 'min_instances': 2, 'status': 'job-accepted'}
PASS: anonymous caller drove current_instances to 6 in 40 calls on the vulnerable app, flag = FLAG{...}

=== FIXED (X-Api-Key required + rate limit) (http://localhost:8110) ===
[*] call 1: anonymous POST /generate-load -> 401 {'error': 'Unauthorized', 'reason': 'missing or invalid X-Api-Key'}
PASS: anonymous caller correctly REJECTED on the fixed app (401) after 1 call(s), no flag, fleet never reached max instances
```
Exit code `0`. Additional negative-control check performed separately (not part of
`exploit.py`'s asserted path, but worth demonstrating in class): calling the fixed app **with**
the correct `X-Api-Key` still gets capped — 5 successful calls (`current_instances` stays at 2,
`load_units` stops at 5), then a `6th` call returns `429 {"error": "TooManyRequests", ...}`. This
is the defense-in-depth proof: the fix is auth **and** a throttle together, not either one alone.

**Your personal flag.** Each student gets a personal `.env` file from the instructor, sent
privately (in this course, as a Google Classroom private comment). Save it as `.env` in this lab
folder before `docker compose up`: Compose reads `FLAG_SCALING` from it, so the flag you capture is
yours alone. Without it, `FLAG_SCALING` falls back to a shared placeholder that is the same for
everyone and earns no marks. Don't share or commit your `.env` (it is git-ignored). Instructors
generate the files with `python3 instructor/seed_flags.py env <STUDENT_ID>` (instructor-only, not
in this repo), which mints this lesson's `scaling` flag from the course manifest.

**Evidence artifact.** The attributable evidence is the captured `flag` value returned by the
*vulnerable* app once `current_instances` reaches 6. The fixed app never returns it. Submitting
another student's flag is a violation.

## Deliverable
The captured flag + the exact request pattern (endpoint, headers-or-lack-thereof, approximate
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
