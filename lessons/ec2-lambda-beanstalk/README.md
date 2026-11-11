# {{ slot_label }} — EC2 Instance Roles and SSRF

**Topic (source):** The EC2 portion of AWS Academy Cloud Foundations Module 6, described here in
our own words — **not** copied from any AWS Academy file. **Kind:** HYBRID — a small Docker lab
covers the EC2 instance-role/SSRF concept. Lambda and Elastic Beanstalk follow in Week 5.
**Concepts:** EC2 instance roles vs. long-lived credentials, the Instance Metadata Service (IMDS),
Server-Side Request Forgery against internal metadata endpoints, credential-theft blast radius ·
**Analogous CWE:** CWE-918 (Server-Side Request Forgery).

## Why this concept matters (in our own words)
A real EC2 instance can have an **IAM instance role** attached. Software running on that instance
can ask a local, link-local-only address — `169.254.169.254` — for **temporary credentials**
scoped to that role, without anyone ever putting a long-lived access key in the code. This is a
genuinely good design: no secrets to leak from source control, no long-lived keys to rotate. The
catch is the *same* design becomes a liability the moment the instance runs a feature that fetches
a **user-supplied URL** server-side (a link-preview generator, a webhook tester, an image-proxy,
anything with a `fetch this URL for me` shape) with no restriction on *which* URL. An attacker who
can't reach the metadata service directly from the internet can simply ask the vulnerable feature
to fetch it *for* them — the request comes from the trusted instance, so IMDS answers it. This
class of bug (SSRF into cloud metadata → temporary credential theft) is one of the most consequential
and well-documented real-world cloud incident patterns of the last decade.

## ✅ This lesson — what to do
1. **Before class** — prepare the EC2 portion of Cloud Foundations Module 6 and check that Docker
   Desktop works. Complete the AWS *Introduction to Amazon EC2* lab in class before this local task.
2. **This add-on lab (45–60 min)** — a local, from-scratch simulation of the SSRF-to-credential-
   theft concept: a tiny Flask "instance" with a fake attached instance role and a link-preview
   feature you can attack without an AWS account. Kickoff: `docker compose up -d`.
3. **Submit** — worksheet evidence and explanation → see [SUBMISSION.md](../../SUBMISSION.md).

## Simulation limits (read this before you start)
On a real EC2 instance, `169.254.169.254` is a **link-local address reachable only from processes
running on that instance** — it is not routable from the internet or from another host, and it is
not something a plain container port mapping can faithfully reproduce. To keep this lab runnable
with plain Docker Compose, the "metadata service" here is just another route
(`/latest/meta-data/iam/security-credentials/AppRole`) on the **same Flask app**, and the exploit
always goes **through** the app's own `/fetch-preview` feature — never a direct hit on the
metadata route from the host. That preserves the real attack shape: the attacker never talks to
the metadata endpoint directly, they trick a server-side fetch feature that already has network
access to it into fetching it on their behalf.

## 🖥️ Signature exercise — "Ask the App to Fetch Its Own Secrets"
Two Flask targets, same two endpoints, one difference in `/fetch-preview`:

| Service | Port | `/fetch-preview` validates the URL? | Self-SSRF to `/latest/meta-data/...` succeeds? |
|---|---|---|---|
| `vulnerable_app.py` | `:8104` | No — plain `requests.get(url)` | **Yes** — leaks fake instance-role credentials + flag |
| `fixed_app.py` | `:8117` | Yes — blocks loopback/link-local hosts and any `/latest/meta-data` path | **No** — `403` |

1. **Baseline:** `POST /fetch-preview {"url": "http://vulnerable:5000/ping"}` (or any ordinary
   external-shaped URL) — this works fine on both apps. The feature itself is legitimate; the bug
   is the *lack of restriction* on which URL it will fetch.
2. **The real question:** `POST /fetch-preview` with
   `{"url": "http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole"}` — asking
   the app to fetch its own metadata route on your behalf.
3. On `:8104` (vulnerable) this succeeds and returns the fake `AccessKeyId`/`SecretAccessKey`/
   `Token` and the flag, embedded in the fetched response body — you never touched the metadata
   route directly, the app fetched it for you.
4. **Confirm the fix:** the identical request against `:8117` (fixed) is rejected (`403`) *before*
   any outbound fetch happens — and so is the literal real-world payload form,
   `http://169.254.169.254/latest/meta-data/iam/security-credentials/AppRole`, while an ordinary
   external-shaped URL still works normally. That's the empirical proof that the fix is a targeted
   allowlist/blocklist decision, not "fetching is now broken."

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
Windows (it comes with Git). Each step says what you should see.

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
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8104/ping
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8117/ping
   ```
   You should see `{"mode":"vulnerable","status":"ok"}` and then `{"mode":"fixed","status":"ok"}`,
   each followed by `HTTP 200`.
3. **Normal use:** ask the vulnerable app to fetch an ordinary page.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8104/fetch-preview -H 'Content-Type: application/json' -d '{"url": "http://vulnerable:5000/ping"}'
   ```
   You should see `"status":"fetched"` and `HTTP 200`. The feature works as designed.
4. **The attack:** ask the vulnerable app to fetch its own metadata route for you.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8104/fetch-preview -H 'Content-Type: application/json' -d '{"url": "http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole"}'
   ```
   You should see `HTTP 200` and a `body` holding fake `AccessKeyId`, `SecretAccessKey` and
   `Token` values plus `\"flag\":\"FLAG{...}\"`. Record the full response in the worksheet,
   together with the `-d '...'` request body you sent.
5. **The same attack on the fixed app:**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8117/fetch-preview -H 'Content-Type: application/json' -d '{"url": "http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole"}'
   ```
   You should see `{"error":"blocked","reason":"internal/metadata URL not allowed",...}` and
   `HTTP 403`, with no flag.
6. **Stop the apps when you finish.**
   ```bash
   docker compose down
   ```

If a step doesn't match, check that Docker Desktop is running and that you are in this lab
folder, then ask in class.

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build   # vulnerable_app.py on :8104, fixed_app.py on :8117
python3 -m pip install requests           # once, on the host
python3 exploit.py
```
`exploit.py` runs the same checks in one go (an optional self-check, not a replacement for the
steps above). Expect five `PASS` lines and exit `0`: the self-SSRF leaks the flag on `:8104`; on
`:8117` it is rejected, and so are the literal `169.254.169.254` form and a redirect-based
bypass, while an ordinary URL still fetches.

**Verified (2026-11-02):** The "get this lab" commands (A, B and C) were run as written on 2026-11-08, in bash and in zsh, on a fresh clone. `docker compose up -d --build` was run on this machine, every command
in Step-by-step was run as written (the optional environment override was tested), and `exploit.py` ran from the host against the published ports. Real
captured output of `exploit.py`, flag value masked:
```
=== VULNERABLE (no URL validation on /fetch-preview) (http://localhost:8104) ===
[*] POST /fetch-preview url=http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole
    -> 200 {'body': '{"AccessKeyId":"ASIAFAKEACCESSKEYID00","Code":"Success","Expiration":"2024-01-01T06:00:00Z","LastUpdated":"2024-01-01T00:00:00Z","SecretAccessKey":"fAkE/SecretAccessKey/ThatLooksReal000000","Token":"FAKE.SESSION.TOKEN.FOR.TEACHING.PURPOSES.ONLY","Type":"AWS-HMAC","flag":"FLAG{...}"}\n', 'status': 'fetched', 'status_code': 200, 'url': 'http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole'}
PASS: SSRF via /fetch-preview leaked instance-role credentials, flag = FLAG{...}

=== FIXED (blocks metadata-shaped/internal URLs) (http://localhost:8117) ===
[*] POST /fetch-preview url=http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole
    -> 403 {'error': 'blocked', 'reason': 'internal/metadata URL not allowed', 'url': 'http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole'}
PASS: fixed app correctly REJECTED the SSRF attempt (403), no flag leaked

PASS: fixed app also rejects the literal 169.254.169.254 payload (403)

PASS: fixed app still fetches an ordinary external-shaped URL (not a blanket failure)

=== FIXED — redirect bypass (http://localhost:8117) ===
[*] POST /fetch-preview url=http://host.docker.internal:<port>/ (redirects to http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole)
    -> 403 {'error': 'blocked', 'reason': 'redirect target not allowed', 'url': 'http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole'}
PASS: fixed app correctly REJECTED the redirect-based bypass (403), no flag leaked
```
Exit code `0`. The `<port>` in the redirect line is a random free port on each run.

**Port note:** the task brief for this lesson suggested `:8104`/`:8105`, but `:8105` is already
in use by this repo's `lesson05-s3-static-site-lambda-sns` lab (built concurrently). This lesson
uses `:8104` (vulnerable) and `:8117` (fixed) instead — both confirmed free across every other
lesson's `docker-compose.yml` in this repo at the time of writing.

**Shared demonstration marker.** No personal `.env` or individual flag is required. Any
`flag` printed by this simulation is a public example marker; it does not identify the student
and is not graded by itself. Submit the exact request or command, the complete relevant
vulnerable and fixed responses, and your own explanation of the security effect. The instructor
may ask you to reproduce and explain the result live. Do not use real credentials in evidence.

## Deliverable
The complete vulnerable/fixed response evidence + the exact request (`POST /fetch-preview` body) that produced it + a
one-paragraph explanation of why this is a **Server-Side Request Forgery** and not "just a bug in
the metadata endpoint" — the metadata endpoint behaved exactly as an EC2 instance's IMDS is
supposed to for callers on the instance; the vulnerability is entirely in `/fetch-preview` trusting
a user-supplied URL as a fetch target with no restriction at all.

## What follows in Week 5
Lambda and Elastic Beanstalk are covered in the next class. Local 02 assesses the EC2 role and
SSRF investigation taught in Week 4; its Part 1 questions do not require the Week 5 topics.

## References
- AWS EC2 documentation — *Instance metadata and user data*, *IAM roles for Amazon EC2*
  (publicly available, general concept — no AWS Academy file used or copied).
- OWASP — *Server-Side Request Forgery Prevention Cheat Sheet* (publicly available).
- Publicly documented industry incident write-ups describing SSRF-to-cloud-metadata credential
  theft as a real-world attack pattern (general, publicly available knowledge — no proprietary or
  AWS Academy source referenced).
