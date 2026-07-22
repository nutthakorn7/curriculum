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
   our alerting pipeline fire?" without needing an AWS account. Kickoff: `docker compose up -d`.
3. **Submit** — worksheet + flag → Classroom.

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

A successful login (`"success": true`) resets that key's failure streak, same as a real
CloudWatch metric filter that only increments on `ConsoleLogin` failure events would stop
accumulating once a login for that key succeeds.

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

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build     # vulnerable_app.py on :8111, fixed_app.py on :8112
pip install requests             # once, on the host
python3 exploit.py
```
Expect two `PASS` lines and exit `0`: the vulnerable app never alerts across 20 rotating-username
attempts from one IP (no flag leaked), and the fixed app alerts exactly on the 3rd attempt with
the flag.

**Verified:** `docker compose up -d --build` was run on this machine; `exploit.py` ran from the
host against the published ports. Real captured output:
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

Per-student flag: run `python3 instructor/seed_flags.py env <STUDENT_ID>` — this course's own
`instructor/seed_flags.py` already exists and its `CHALLENGES` list already includes `"monitor"`.
Unlike the other lessons, `vulnerable_app.py`'s `FLAG_MONITOR = os.environ.get("FLAG_MONITOR")`
has **no default value** — if it's unset, the response simply never includes a `flag` key at all
(by design: the vulnerable app's own code path must never leak one, see below). Set it explicitly
via `FLAG_MONITOR=FLAG{...} docker compose up` to exercise the fixed app's alert-then-flag path.

**Evidence artifact.** The attributable evidence is the captured `flag` value returned once the
*fixed* app's alert fires. The vulnerable app never returns it, no matter how many attempts are
sent. Submitting another student's flag is a violation.

## Deliverable
The captured flag + the attempt number it appeared on + a one-paragraph explanation of why
`(source_ip, username)` is the wrong aggregation key for detecting a password-spray attack,
while `source_ip` alone correctly catches it.

## References
- AWS CloudTrail documentation — *Logging AWS API and console sign-in events* (publicly
  available, general concept — no AWS Academy file used or copied).
- AWS CloudWatch documentation — *Creating metric filters and alarms for log data*, specifically
  the concept of an aggregation/dimension key for a custom metric.
- AWS EventBridge documentation — *Event patterns and rules for routing to a target* (general
  concept, no AWS Academy file used or copied).
