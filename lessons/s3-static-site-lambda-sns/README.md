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
   without an AWS account. Kickoff: `docker compose up -d`.
3. **Submit** — worksheet + flag → Classroom.

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

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build   # vulnerable_app.py on :8105, fixed_app.py on :8106
pip install requests           # once, on the host
python exploit.py
```
Expect two `PASS` lines and exit `0`: an anonymous defacement + flag on `:8105`, a rejected
anonymous write (no flag) on `:8106`, with public GET succeeding on both.

**Verified:** `docker compose up -d --build` was run on this machine; `exploit.py` ran from the
host against the published ports. Real captured output:
```
=== VULNERABLE (bucket policy grants Principal:'*' both Get+PutObject) (http://localhost:8105) ===
[*] anonymous GET index.html (public website hosting) -> 200 {'content': '<html><body><h1>Welcome to our official site</h1></body></html>', 'key': 'index.html'}
[*] anonymous (no auth header at all) PUT index.html   -> 200 {'content': '<html><body><h1>PWNED by anonymous PUT</h1></body></html>', 'flag': 'FLAG{public_putobject_defaces_your_website}', 'key': 'index.html', 'status': 'uploaded'}
PASS: anonymous caller defaced index.html on the vulnerable app, flag = FLAG{public_putobject_defaces_your_website}

=== FIXED (bucket policy grants Principal:'*' GetObject only) (http://localhost:8106) ===
[*] anonymous GET index.html (public website hosting) -> 200 {'content': '<html><body><h1>Welcome to our official site</h1></body></html>', 'key': 'index.html'}
[*] anonymous (no auth header at all) PUT index.html   -> 403 {'error': 'AccessDenied', 'key': 'index.html'}
PASS: anonymous caller correctly REJECTED on the fixed app (403), no flag
```
Exit code `0`. Negative controls confirmed separately: an unknown object key returns `404
NoSuchKey` (not a crash) on both apps; re-`GET`ting `index.html` on the vulnerable app after the
exploit confirms the defacement persisted (the site now really does serve the attacker's HTML),
demonstrating that this is a real overwrite, not just an accepted-but-discarded request.

Per-student flag: run `python3 instructor/seed_flags.py env <STUDENT_ID>` — this course's own
`instructor/seed_flags.py` already exists and its `CHALLENGES` list already includes `"s3site"`.
Without it, `FLAG_S3SITE` defaults to `FLAG{public_putobject_defaces_your_website}` and can be
overridden: `FLAG_S3SITE=FLAG{...} docker compose up`.

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
