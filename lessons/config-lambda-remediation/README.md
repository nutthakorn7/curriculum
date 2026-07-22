# {{ slot_label }} — AWS Config + Lambda Auto-Remediation (Inverted Allowlist)

**Topic (source):** Shinya's own troubleshooting notes for the AWS Academy Cloud Security
Foundations lesson on AWS Config detecting a non-compliant security group and a Lambda function
auto-remediating it, described here in our own words — **not** copied from any AWS Academy file.
**Kind:** HYBRID (small lab + conceptual material; the AWS Config "resource inventory / compliance
tracking" mechanics are covered as concept only, in the worksheet, not simulated in code).
**Concepts:** compliance auto-remediation, allowlist vs. denylist logic, silent logic-inversion
bugs, security-group inbound-rule hygiene · **Analogous CWE:** CWE-697 (Incorrect Comparison),
CWE-284 (Improper Access Control).

## This lesson — what to do
1. **Before class** — Docker Desktop working; complete the real AWS Academy lab covering Config +
   Lambda remediation in your Learner Lab sandbox first (that's still where you learn the actual
   AWS console UI: Config rules, compliance timeline, Lambda console, CloudWatch Logs).
2. **This add-on lab (45–60 min)** — a local, from-scratch simulation of the same
   auto-remediation concept: a tiny Flask API standing in for "a security group" plus a
   "remediation function" you can inspect and attack without an AWS account. Kickoff:
   `docker compose up -d`.
3. **Submit** — worksheet + flag → Classroom.

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
returns `200 OK` with no exception either way, and the compliance dashboard would show
"remediation: succeeded" — but the dangerous rule is still there and legitimate traffic just
broke. This is what makes inverted-logic remediation bugs so dangerous: **they fail silently and
look like success.**

1. **Baseline:** `POST /reset` seeds a security group with three inbound rules: port 80
   (`0.0.0.0/0`), port 443 (`0.0.0.0/0`), and port 22/SSH (`0.0.0.0/0`) — the last one is what a
   real Config rule (e.g. `restricted-ssh`) would flag as NON_COMPLIANT.
2. **Run remediation:** `POST /remediate` on each target.
3. **Check the result:** `GET /security-group`.
4. On `:8115` (vulnerable) the SSH-from-anywhere rule **survives** remediation, ports 80/443 are
   **gone**, and the response includes a flag confirming the dangerous rule was left in place.
5. **Confirm the fix:** the identical sequence against `:8116` (fixed) leaves only the 80/443
   rules — the SSH rule is correctly revoked, and no flag is returned.

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build       # vulnerable_app.py on :8115, fixed_app.py on :8116
pip install requests               # once, on the host
python exploit.py
```
Expect two `PASS` lines and exit `0`: the dangerous SSH rule + flag surviving remediation on
`:8115`, and the dangerous rule being correctly removed (no flag) on `:8116`.

**Verified:** `docker compose up -d --build` was run on this machine; `exploit.py` ran from the
host against the published ports. Real captured output:
```
=== VULNERABLE (inverted allowlist condition) (http://localhost:8115) ===
[*] seeded starting rules                 -> 200 [{'cidr': '0.0.0.0/0', 'port': 80}, {'cidr': '0.0.0.0/0', 'port': 443}, {'cidr': '0.0.0.0/0', 'port': 22}]
[*] POST /remediate                        -> 200 after=[{'cidr': '0.0.0.0/0', 'port': 22}]
[*] GET /security-group (post-remediation)  -> 200 {'dangerous_rules_present': True, 'flag': 'FLAG{inverted_allowlist_leaves_ssh_open}', 'rules': [{'cidr': '0.0.0.0/0', 'port': 22}]}
PASS: vulnerable app's remediation left port 22 open to 0.0.0.0/0 and wrongly revoked 80/443, flag = FLAG{inverted_allowlist_leaves_ssh_open}

=== FIXED (correct allowlist condition) (http://localhost:8116) ===
[*] seeded starting rules                 -> 200 [{'cidr': '0.0.0.0/0', 'port': 80}, {'cidr': '0.0.0.0/0', 'port': 443}, {'cidr': '0.0.0.0/0', 'port': 22}]
[*] POST /remediate                        -> 200 after=[{'cidr': '0.0.0.0/0', 'port': 80}, {'cidr': '0.0.0.0/0', 'port': 443}]
[*] GET /security-group (post-remediation)  -> 200 {'dangerous_rules_present': False, 'rules': [{'cidr': '0.0.0.0/0', 'port': 80}, {'cidr': '0.0.0.0/0', 'port': 443}]}
PASS: fixed app's remediation revoked port 22 and kept only 80/443, no flag
```
Exit code `0`. Negative controls confirmed separately: calling `/remediate` a second time on
either target is idempotent (fixed app stays at `{80, 443}`; vulnerable app stays at `{22}`) — the
bug isn't a one-time fluke, it's the function's steady-state behavior.

Per-student flag: run `python3 instructor/seed_flags.py env <STUDENT_ID>` — this course's own
`instructor/seed_flags.py` already exists and its `CHALLENGES` list already includes
`"remediate"`. Without it, `FLAG_REMEDIATE` defaults to `FLAG{inverted_allowlist_leaves_ssh_open}`
and can be overridden: `FLAG_REMEDIATE=FLAG{...} docker compose up`.

**Evidence artifact.** The attributable evidence is the captured `flag` value returned by the
*vulnerable* app's `GET /security-group` after `/remediate` has run. The fixed app never returns
it. Submitting another student's flag is a violation.

## Deliverable
The captured flag + the exact request sequence (`/reset`, `/remediate`, `/security-group`) that
produced it + a one-paragraph explanation of why an inverted allowlist condition is more
dangerous than a rule that simply does nothing — it doesn't just fail to fix the problem, it
actively breaks legitimate traffic while leaving the actual danger in place, and reports success.

## References
- AWS Config documentation — *Evaluating resources with rules*, *Remediating noncompliant
  resources* (publicly available, general concept — no AWS Academy file used or copied).
- AWS Lambda documentation — *Using Lambda with other services* (event-driven remediation
  pattern, general concept only).
- AWS EC2 documentation — *Security group rules*, specifically why an inbound rule open to
  `0.0.0.0/0` on a management port (22/3389) is treated as a high-severity finding by most cloud
  security posture tools.
