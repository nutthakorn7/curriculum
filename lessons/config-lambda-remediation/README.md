# {{ slot_label }} — AWS Config + Lambda Auto-Remediation (Inverted Allowlist)

**Topic:** The Week 18 AWS Academy Cloud Security Foundations Module 7 lab introduces AWS Config
and Lambda in an incident response workflow. Follow the current AWS Academy instructions for the
real lab; this original local exercise isolates one remediation logic error.
**Kind:** HYBRID (small lab + conceptual material; the AWS Config "resource inventory / compliance
tracking" mechanics are covered as concept only, in the worksheet, not simulated in code).
**Concepts:** compliance auto-remediation, allowlist vs. denylist logic, silent logic-inversion
bugs, security-group inbound-rule hygiene · **Analogous CWE:** CWE-697 (Incorrect Comparison),
CWE-284 (Improper Access Control).

## This lesson — what to do
1. **Week 18 class (100 min)** — open Cloud Security Foundations Module 7 before class, then
   complete Lab 7.1 (*Remediating an Incident by Using AWS Config and Lambda*) in the scheduled
   75-minute Learner Lab block. Use it to learn the AWS console UI: Config rules, compliance
   timeline, Lambda console, and CloudWatch Logs. Keep before/after security-group observations.
2. **After that class (45–60 min outside class)** — read the Week 18 course bridge's Local 10
   slides, then run a local, from-scratch simulation of the same remediation idea. A tiny Flask
   API stands in for a security group and a remediation function you can inspect without an AWS
   account. Follow **Step-by-step** below (kickoff: `docker compose up -d --build`).
3. **Submit** — worksheet evidence and explanation → see [SUBMISSION.md](../../SUBMISSION.md).

## Objectives
- Explain, at a high level, how AWS Config flags a resource NON_COMPLIANT and how a Lambda-based
  remediation action is meant to fix it automatically (full treatment in worksheet Part 1 — this
  lab does not simulate Config's resource-inventory/compliance-timeline machinery, only the
  remediation function itself).
- Identify an **inverted comparison** (`in` vs. `not in` an allowed-ports set) as the bug class,
  and explain why it is a *silent* failure — no exception, no error log, `200 OK` either way.
- Fix the bug by correcting the keep/revoke condition, and explain why "it ran without errors"
  is not evidence that a remediation function did the right thing.

## Signature exercise — "The Inverted Allowlist"
Two Flask targets, same endpoints, one condition flipped in the remediation logic:

| Service | Port | `/remediate` logic | After remediation, is port 22 from `0.0.0.0/0` gone? | Are 80/443 still there? |
|---|---|---|---|---|
| `vulnerable_app.py` | `:8115` | keeps rules whose port is **NOT** in the allowed set `{80, 443}` (inverted) | **No — it survives** | **No — wrongly revoked** |
| `fixed_app.py` | `:8116` | keeps only rules whose port **is** in the allowed set `{80, 443}` (correct) | **Yes — revoked** | **Yes — kept** |

**Why it's exciting:** the bug is a single flipped comparison (`in` vs. `not in`), the function
returns `200 OK` with no exception either way. A system that records only the invocation result
could show success while the dangerous rule remains and legitimate traffic breaks. Check the
final security-group state rather than treating the function response as proof of remediation.

1. **Baseline:** `POST /reset` seeds a security group with three inbound rules: port 80
   (`0.0.0.0/0`), port 443 (`0.0.0.0/0`), and port 22/SSH (`0.0.0.0/0`) — the last one is what a
   real Config rule (e.g. `restricted-ssh`) would flag as NON_COMPLIANT.
2. **Run remediation:** `POST /remediate` on each target.
3. **Check the result:** `GET /security-group`.
4. On `:8115` (vulnerable) the SSH-from-anywhere rule **survives** remediation, ports 80/443 are
   **gone**, and the response includes a flag confirming the dangerous rule was left in place.
5. **Confirm the fix:** the identical sequence against `:8116` (fixed) leaves only the 80/443
   rules — the SSH rule is correctly revoked, and no flag is returned.

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
Windows (it comes with Git). Each step says what you should see. Do them in order: the
vulnerable app gives the flag only after its remediation has run.

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
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8115/ping
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8116/ping
   ```
   You should see `{"mode":"vulnerable","status":"ok"}` and then `{"mode":"fixed","status":"ok"}`,
   each followed by `HTTP 200`.
3. **Reset the vulnerable app's security group** to its starting rules.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8115/reset
   ```
   You should see `"status":"reset"` and three inbound rules, all from `0.0.0.0/0`: ports 80, 443
   and 22 (SSH). Port 22 open to everyone is the rule a real AWS Config check would flag.
4. **Run the vulnerable app's remediation:**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8115/remediate
   ```
   You should see `"status":"remediated"` and `HTTP 200`, which looks like success. But read
   `"after"`: only port 22 is left. The function removed the allowed ports 80 and 443 and kept SSH.
5. **Check the vulnerable app's security group now:**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8115/security-group
   ```
   You should see `"dangerous_rules_present":true`, `"rules"` with only port 22, and
   `"flag":"FLAG{...}"`. Record the full response in the worksheet, together with the three
   commands from steps 3–5 and which rules survived and which were removed.
6. **The same three steps on the fixed app:**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8116/reset
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8116/remediate
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8116/security-group
   ```
   The last answer should show `"dangerous_rules_present":false` and only ports 80 and 443, with
   no flag. The fixed remediation removed SSH and kept the allowed ports.
7. **Stop the apps when you finish.**
   ```bash
   docker compose down
   ```

You can repeat steps 3–6 at any time: `/reset` puts the starting rules back. If a step doesn't
match, check that Docker Desktop is running and that you are in this lab folder, then ask in class.

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build       # vulnerable_app.py on :8115, fixed_app.py on :8116
python3 -m pip install requests               # once, on the host
python3 exploit.py
```
`exploit.py` runs the main checks in one go (an optional self-check, not a replacement for the
steps above; the Step-by-step needs no Python). Expect two `PASS` lines and exit `0`: the
dangerous SSH rule + flag surviving remediation on `:8115`, and the dangerous rule being correctly
removed (no flag) on `:8116`.

**Verified (2026-11-04):** The "get this lab" commands (A, B and C) were run as written on 2026-11-08, in bash and in zsh, on a fresh clone. `docker compose up -d --build` was run on this machine (macOS) and
every command in Step-by-step was run as written, in bash and in zsh (the macOS default shell).
Windows Git Bash was not tested. The optional environment override was tested; the public default is a shared marker. `exploit.py` then ran
from the host against the published ports. Real captured output, flag value masked:
```
=== VULNERABLE (inverted allowlist condition) (http://localhost:8115) ===
[*] seeded starting rules                 -> 200 [{'cidr': '0.0.0.0/0', 'port': 80}, {'cidr': '0.0.0.0/0', 'port': 443}, {'cidr': '0.0.0.0/0', 'port': 22}]
[*] POST /remediate                        -> 200 after=[{'cidr': '0.0.0.0/0', 'port': 22}]
[*] GET /security-group (post-remediation)  -> 200 {'dangerous_rules_present': True, 'flag': 'FLAG{...}', 'rules': [{'cidr': '0.0.0.0/0', 'port': 22}]}
PASS: vulnerable app's remediation left port 22 open to 0.0.0.0/0 and wrongly revoked 80/443, flag = FLAG{...}

=== FIXED (correct allowlist condition) (http://localhost:8116) ===
[*] seeded starting rules                 -> 200 [{'cidr': '0.0.0.0/0', 'port': 80}, {'cidr': '0.0.0.0/0', 'port': 443}, {'cidr': '0.0.0.0/0', 'port': 22}]
[*] POST /remediate                        -> 200 after=[{'cidr': '0.0.0.0/0', 'port': 80}, {'cidr': '0.0.0.0/0', 'port': 443}]
[*] GET /security-group (post-remediation)  -> 200 {'dangerous_rules_present': False, 'rules': [{'cidr': '0.0.0.0/0', 'port': 80}, {'cidr': '0.0.0.0/0', 'port': 443}]}
PASS: fixed app's remediation revoked port 22 and kept only 80/443, no flag
```
Exit code `0`. Negative controls confirmed separately: calling `/remediate` a second time on
either target is idempotent (fixed app stays at `{80, 443}`; vulnerable app stays at `{22}`) — the
bug isn't a one-time fluke, it's the function's steady-state behavior.

**Shared demonstration marker.** No personal `.env` or individual flag is required. Any
`flag` printed by this simulation is a public example marker; it does not identify the student
and is not graded by itself. Submit the exact request or command, the complete relevant
vulnerable and fixed responses, and your own explanation of the security effect. The instructor
may ask you to reproduce and explain the result live. Do not use real credentials in evidence.

## Deliverable
The complete vulnerable/fixed response evidence + the exact request sequence (`/reset`, `/remediate`, `/security-group`) that
produced it + a one-paragraph explanation of why an inverted allowlist condition is more
dangerous than a rule that simply does nothing — it doesn't just fail to fix the problem, it
actively breaks legitimate traffic while leaving the actual danger in place, and reports success.
You may answer in Thai or English. Write your answers on the **Local10 Answer Sheet** copy in
Classroom and click Turn in (no PDF needed). Full tasks: `worksheet.md`.

## References
- AWS Config documentation — *Evaluating resources with rules*, *Remediating noncompliant
  resources* (publicly available, general concept — no AWS Academy file used or copied).
- AWS Lambda documentation — *Using Lambda with other services* (event-driven remediation
  pattern, general concept only).
- AWS EC2 documentation — *Security group rules*, specifically why an inbound rule open to
  `0.0.0.0/0` on a management port (22/3389) is treated as a high-severity finding by most cloud
  security posture tools.
