# {{ slot_label }} — CloudTrail + CloudWatch + EventBridge Monitoring

**Topic (source):** Shinya's own troubleshooting notes for AWS Academy Cloud Security
Foundations Lab 3.2-class material on failed-console-login alerting (CloudTrail event
recording → CloudWatch metric filter/alarm → EventBridge rule → SNS notification),
described here in our own words — **not** copied from any AWS Academy file. **Kind:** HYBRID.
**Concepts:** detective controls, log-event aggregation keys, metric filters, alarm
thresholds, password-spray vs. classic brute-force threat patterns · **Analogous bug class:**
CWE-778 (Insufficient Logging) adjacent / detective-control logic error — the control exists
and runs, but its aggregation key silently excludes the real attack shape.

## This lesson — what to do
1. **Before class** — complete the real AWS Academy Lab (CloudTrail/CloudWatch/EventBridge
   failed-login alerting) in your Learner Lab sandbox first — that's still where you learn the
   actual AWS console UI, metric filter syntax, and EventBridge rule configuration.
2. **This add-on lab (45–60 min)** — a local, from-scratch simulation of the same monitoring
   concept: a tiny Flask service that stands in for "CloudTrail recorded this login event, did
   our alerting pipeline fire?" without needing an AWS account. Follow **Step-by-step** below
   (kickoff: `docker compose up -d --build`).
3. **Submit** — worksheet + flag → see [SUBMISSION.md](../../SUBMISSION.md).

## Signature exercise — "The Spray That Never Alerts"

Two Flask targets, same endpoint, one aggregation-key difference in how failed logins are
counted:

| Service | Port | Failed-login counter keyed by | 20x rotating-username spray from one IP triggers alert? |
|---|---|---|---|
| `vulnerable_app.py` | `:8111` | `(source_ip, username)` | **No** |
| `fixed_app.py` | `:8112` | `source_ip` alone | **Yes — on the 3rd attempt** |

**Why it's exciting:** the detective control is not missing, misconfigured-off, or crashing —
it runs on every single request and faithfully counts failures. It just counts them against
the wrong key, so a very common real attack pattern (password spraying: many different
usernames, same attacking IP, only 1–2 failures against any *one* username) never crosses any
individual counter's threshold, no matter how many total attempts the attacker makes.

### Endpoint

`POST /login-attempt` — simulates CloudTrail recording a console login event.

Request body:
```json
{"username": "admin7", "success": false, "source_ip": "203.0.113.20"}
```

Response (no alert yet):
```json
{"status": "recorded", "alert": false, "count_for_key": 2, "note": "..."}
```

Response (alert fires — fixed app only, once threshold is reached):
```json
{"status": "recorded", "alert": true, "reason": "...", "flag": "FLAG{...}"}
```

A successful login (`"success": true`) resets that key's failure streak — **a lab
simplification**. (Real CloudWatch is different: a metric filter is a *stateless* counter of
matching failure events, and its alarm sums those over a fixed evaluation window. A success just
produces no datapoint; it does **not** zero or pause the count, so failures on either side of an
intervening success within the same window still add up. Real reset-on-success would need custom
logic, e.g. an EventBridge → Lambda rule.)

### The vulnerability

`vulnerable_app.py` tracks the failed-attempt counter keyed by the **tuple**
`(source_ip, username)`. Threshold is 3 failures. An attacker who tries `admin1`, `admin2`,
`admin3`, ... from the same IP never accumulates more than 1 failure against any single
`(ip, username)` pair — even after 20+ total failed attempts from that one IP, **no counter
ever reaches 3, and no alert ever fires.** (A negative-control check: the *same username*
repeated 3x from the same IP against the vulnerable app *does* alert — its counting logic is
not broken, only its choice of key. It correctly never returns a flag either way, since
`FLAG_MONITOR` is only configured on the fixed service.)

### The fix

`fixed_app.py` tracks the failed-attempt counter keyed by `source_ip` **alone**, ignoring
username. The exact same 20-attempt rotating-username spray now correctly accumulates against
one key and fires the alert on the 3rd failed attempt, regardless of which usernames were
tried — because from a detection standpoint, "one IP, many failed usernames" and "one IP, many
failed attempts at one username" are the same underlying threat (someone at that IP is
guessing credentials) and should trip the same control.

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
   even if you downloaded them last week. It never touches your `.env` file.
   ```bash
   cd ~/cloud-infrastructure-security
   git pull
   ```
   You should see `Already up to date.` or a list of changed files. If you see
   `No such file or directory`, your copy is in another folder: do A to make a new one here. If you
   see `Your local changes to the following files would be overwritten`, run `git checkout -- .`
   and then `git pull` again. That throws away any edits you made to the course files; your
   answers are on the Answer Sheet, so they are safe.

C. **Go into this lab's folder and check it.**
   ```bash
   cd {{ labpath }}
   ls
   ```
   You should see `README.md`, `worksheet.md` and `docker-compose.yml` among the files. Every
   command below runs from this folder. If you open a new terminal later, do B and C again first.

Run these in a terminal inside this lab folder: Terminal on macOS or Linux, or **Git Bash** on
Windows (it comes with Git). Each step says what you should see. Do them in order: both apps
remember every attempt until they restart. In this lab the flag comes from the **fixed** app,
when its alert fires; the vulnerable app never gives one.

0. **Your personal flag:** save the `.env` file from your Classroom private comment in this folder
   first (see "Your personal flag" below). Without it you capture the shared placeholder flag,
   which earns no marks.
1. **Start both apps.** The first run downloads and builds the image, so it can take a few
   minutes.
   ```bash
   docker compose up -d --build
   ```
   When it finishes, wait about 10 seconds for the apps to start.
2. **Check that both apps are running.** If you see only `HTTP 000`, the apps are still starting:
   wait a few seconds and run the command again.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8111/ping
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8112/ping
   ```
   You should see `{"mode":"vulnerable","status":"ok"}` and then `{"mode":"fixed","status":"ok"}`,
   each followed by `HTTP 200`.
3. **The attack on the vulnerable app:** a password spray. One IP, `203.0.113.20`, tries 20
   different usernames (`admin1` to `admin20`), each once, and every attempt fails. The loop
   prints the attempt number in front of each answer.
   ```bash
   for i in $(seq 1 20); do printf 'attempt %s: ' "$i"; curl -s -X POST http://localhost:8111/login-attempt -H 'Content-Type: application/json' -d '{"username": "admin'"$i"'", "success": false, "source_ip": "203.0.113.20"}'; done
   ```
   All 20 answers say `"alert":false` and `"count_for_key":1`. The vulnerable app counts each
   (IP, username) pair on its own, so no counter ever reaches the threshold of 3, and it never
   alerts. Copy the loop command and the last answer into the worksheet.
4. **The same spray on the fixed app:**
   ```bash
   for i in $(seq 1 20); do printf 'attempt %s: ' "$i"; curl -s -X POST http://localhost:8112/login-attempt -H 'Content-Type: application/json' -d '{"username": "admin'"$i"'", "success": false, "source_ip": "203.0.113.20"}'; done
   ```
   Attempts 1 and 2 say `"alert":false` with `"count_for_key"` 1 and then 2. On **attempt 3**
   the answer says `"alert":true` and contains `"flag":"FLAG{...}"`: the fixed app counts by IP
   alone, so the third failure from that IP fires the alert. Every later attempt alerts too. That
   flag is yours: copy it into the worksheet, with the loop command and the attempt number where
   the first alert appeared.
5. **Check that the vulnerable app's counter itself works:** the same username fails 3 times from
   one IP.
   ```bash
   for i in 1 2 3; do printf 'attempt %s: ' "$i"; curl -s -X POST http://localhost:8111/login-attempt -H 'Content-Type: application/json' -d '{"username": "alice", "success": false, "source_ip": "198.51.100.7"}'; done
   ```
   On attempt 3 you should see `"alert":true`, with no flag. The vulnerable app *can* alert; it
   just counts by the wrong key, so a spray across many usernames slips past it.
6. **Stop the apps when you finish.**
   ```bash
   docker compose down
   ```

To start again from zero, run `docker compose restart vulnerable fixed` (the counters live in each
app's memory, so a restart resets them). If a step doesn't match, check that Docker Desktop is
running and that you are in this lab folder, then ask in class.

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build     # vulnerable_app.py on :8111, fixed_app.py on :8112
python3 -m pip install requests             # once, on the host
python3 exploit.py
```
`exploit.py` runs the main checks in one go (an optional self-check, not a replacement for the
steps above; the Step-by-step needs no Python). Run it on freshly started apps (`docker compose
restart vulnerable fixed` first): it picks a random `203.0.113.x` address on each run, so its IP
will differ from the transcript below, and an address the apps have already seen would make its
checks fail. Expect two `PASS` lines and exit `0`: the vulnerable app never
alerts across 20 rotating-username attempts from one IP (no flag leaked), and the fixed app alerts
exactly on the 3rd attempt with the flag.

**Verified (2026-11-04):** The "get this lab" commands (A, B and C) were run as written on 2026-11-08, in bash and in zsh, on a fresh clone. `docker compose up -d --build` was run on this machine (macOS) and
every command in Step-by-step was run as written, in bash and in zsh (the macOS default shell).
Windows Git Bash was not tested. Step 0 was tested with a stand-in `.env`, and the captured flag
changed to its value; without a `.env` the shared placeholder came back.
`docker compose restart vulnerable fixed` reset both counters. `exploit.py` then ran from the host
against the published ports. Real captured output, flag value masked:
```
=== VULNERABLE (counter keyed by (source_ip, username)) (http://localhost:8111) — source_ip=203.0.113.20 ===
[*] attempt  1 username=admin1     -> 200 {'alert': False, 'count_for_key': 1, 'note': 'counter tracked per (source_ip, username) pair', 'status': 'recorded'}
[*] attempt  2 username=admin2     -> 200 {'alert': False, 'count_for_key': 1, 'note': 'counter tracked per (source_ip, username) pair', 'status': 'recorded'}
[*] attempt  3 username=admin3     -> 200 {'alert': False, 'count_for_key': 1, 'note': 'counter tracked per (source_ip, username) pair', 'status': 'recorded'}
...
[*] attempt 20 username=admin20    -> 200 {'alert': False, 'count_for_key': 1, 'note': 'counter tracked per (source_ip, username) pair', 'status': 'recorded'}
PASS: vulnerable app never alerted across 20 password-spray attempts from a single source_ip (rotating usernames), no flag leaked

=== FIXED (counter keyed by source_ip alone) (http://localhost:8112) — source_ip=203.0.113.20 ===
[*] attempt  1 username=admin1     -> 200 {'alert': False, 'count_for_key': 1, 'note': 'counter tracked per source_ip only', 'status': 'recorded'}
[*] attempt  2 username=admin2     -> 200 {'alert': False, 'count_for_key': 2, 'note': 'counter tracked per source_ip only', 'status': 'recorded'}
[*] attempt  3 username=admin3     -> 200 {'alert': True, 'flag': 'FLAG{aggregation_key_must_match_the_threat_model}', 'reason': "3 failed attempts from source_ip='203.0.113.20' (usernames vary)", 'status': 'recorded'}
PASS: fixed app correctly alerted on attempt 3 (3rd failed attempt from source_ip=203.0.113.20), flag = FLAG{aggregation_key_must_match_the_threat_model}
```
Exit code `0`. (Attempts 4–19 elided above for brevity — the full attempt-by-attempt lines,
identically shaped, are in the actual run output.) Negative control confirmed separately:
3 identical-username failed attempts from one IP against the vulnerable app **does** alert
(`alert: true`), proving its counter mechanics work — it is specifically the `(ip, username)`
key choice that misses the password-spray pattern, not a broken counter.

**Your personal flag.** Each student gets a personal `.env` file from the instructor, sent
privately (in this course, as a Google Classroom private comment). Save it as `.env` in this lab
folder before `docker compose up`: Compose reads `FLAG_MONITOR` from it, so the flag you capture is
yours alone. Without it, `FLAG_MONITOR` falls back to a shared placeholder that is the same for
everyone and earns no marks. Don't share or commit your `.env` (it is git-ignored). Instructors
generate the files with `python3 instructor/seed_flags.py env <STUDENT_ID>` (instructor-only, not
in this repo), which mints this lesson's `monitor` flag from the course manifest.
Unlike the other lessons, `vulnerable_app.py`'s `FLAG_MONITOR = os.environ.get("FLAG_MONITOR")`
has **no default value** — if it's unset, the response simply never includes a `flag` key at all
(by design: the vulnerable app's own code path must never leak one, see below). You don't need to set it by hand: the fixed service reads it from your `.env` (or falls back to the
shared placeholder in `docker-compose.yml`).

**Evidence artifact.** The attributable evidence is the captured `flag` value returned once the
*fixed* app's alert fires. The vulnerable app never returns it, no matter how many attempts are
sent. Submitting another student's flag is a violation.

## Deliverable
The captured flag + the attempt number it appeared on + a one-paragraph explanation of why
`(source_ip, username)` is the wrong aggregation key for detecting a password-spray attack,
while `source_ip` alone correctly catches it. You may answer in Thai or English. Write your
answers on the **Local09 Answer Sheet** copy in Classroom and click Turn in (no PDF needed). Full
tasks: `worksheet.md`.

## References
- AWS CloudTrail documentation — *Logging AWS API and console sign-in events* (publicly
  available, general concept — no AWS Academy file used or copied).
- AWS CloudWatch documentation — *Creating metric filters and alarms for log data*, specifically
  the concept of an aggregation/dimension key for a custom metric.
- AWS EventBridge documentation — *Event patterns and rules for routing to a target* (general
  concept, no AWS Academy file used or copied).
