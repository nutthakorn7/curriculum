# {{ slot_label }} — IAM Policy Evaluation (Privilege Escalation)

**Topic (source):** Shinya's own troubleshooting notes for AWS Academy Cloud Security
Foundations Lab 3.1 ("devuser can't download/upload; assuming BucketsAccessRole partially
fixes it; bucket3's resource policy is the real question"), described here in our own words —
**not** copied from any AWS Academy file. **Kind:** LAB.
**Concepts:** identity-based vs. resource-based IAM policies, policy evaluation order, least
privilege, wildcard `Principal` misconfiguration · **Analogous CWE:** CWE-284 (Improper Access
Control), CWE-668 (Exposure of Resource to Wrong Sphere).

## ✅ This lesson — what to do
1. **Before class** — Docker Desktop working; complete the real AWS Academy Lab 3.1 in your
   Learner Lab sandbox first (that's still where you learn the actual AWS console UI).
2. **This add-on lab (60–90 min)** — a local, from-scratch simulation of the same IAM concept:
   a tiny "S3-and-IAM-like" API with a policy engine you can inspect and attack without an AWS
   account. Kickoff: `docker compose up -d`.
3. **Submit** — worksheet + flag → Classroom.

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

## Run it
```bash
cd {{ labpath }}
docker compose up -d          # vulnerable_app.py on :8107, fixed_app.py on :8108
pip install requests          # once, on the host
python exploit.py
```
Expect two `PASS` lines and exit `0`: an anonymous write to bucket3 + flag on `:8107`, a
rejected anonymous write (no flag) on `:8108`.

**Verified:** `docker compose up -d --build` was run on this machine; `exploit.py` ran from the
host against the published ports. Real captured output:
```
=== VULNERABLE (bucket3 Principal = '*') (http://localhost:8107) ===
[*] BucketsAccessRole GET bucket1 (no such key yet) -> 404 {'error': 'NoSuchKey'}
[*] BucketsAccessRole PUT bucket2 (resource policy allows it) -> 200 {..., 'status': 'uploaded'}
[*] BucketsAccessRole PUT bucket3 (with role assumed)         -> 200 {..., 'flag': 'FLAG{wildcard_principal_grants_the_world}'}
[*] anonymous (no role assumed) PUT bucket3                  -> 200 {..., 'flag': 'FLAG{wildcard_principal_grants_the_world}'}
PASS: anonymous caller wrote to bucket3 on the vulnerable app, flag = FLAG{wildcard_principal_grants_the_world}

=== FIXED (bucket3 scoped to BucketsAccessRole, get-only) (http://localhost:8108) ===
[*] BucketsAccessRole PUT bucket3 (with role assumed)         -> 403 {'error': 'AccessDenied', ...}
[*] anonymous (no role assumed) PUT bucket3                  -> 403 {'error': 'AccessDenied', ...}
PASS: anonymous caller correctly REJECTED on the fixed app (403), no flag
```
Exit code `0`. Negative controls confirmed separately: `devuser`/anonymous callers get `403` on
`bucket1` (no matching resource or identity policy); an unknown bucket name returns `403`, not a
crash.

Per-student flag: run `python3 instructor/seed_flags.py env <STUDENT_ID>` — this course's own
`instructor/seed_flags.py` already exists and its `CHALLENGES` list already includes `"iam"`.
Without it, `FLAG_IAM` defaults to `FLAG{wildcard_principal_grants_the_world}` and can be
overridden: `FLAG_IAM=FLAG{...} docker compose up`.

**Evidence artifact.** The attributable evidence is the captured `flag` value returned by the
*vulnerable* app's anonymous write to bucket3. The fixed app never returns it. Submitting
another student's flag is a violation.

## Deliverable
The captured flag + the exact request (bucket, method, headers-or-lack-thereof) that produced
it + a one-paragraph explanation of why a wildcard `Principal` on a resource-based policy is
different from "no authentication" — it's not that auth is missing, it's that the policy
itself names everyone as authorized.

## References
- AWS IAM documentation — *Identity-based policies and resource-based policies*, *Policy
  evaluation logic* (publicly available, general concept — no AWS Academy file used or copied).
- AWS S3 documentation — *Bucket policy examples*, specifically why `"Principal": "*"` should
  almost always be paired with a `Condition` block or avoided entirely.
