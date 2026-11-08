# {{ slot_label }} — AWS Fundamentals: Shared Responsibility & IAM Basics

**Topic (source):** AWS Academy Modules 1–3 (Cloud Foundations intro, security fundamentals,
IAM/access-securing concepts) and their Knowledge Checks, described here in our own words —
**not** copied from any AWS Academy file. **Kind:** CONCEPTUAL (no exploitable target — this is
a concept-check / mental-model lesson, same precedent as {{ ref('kms-envelope-encryption') }}'s KMS envelope-encryption
week). **Concepts:** the AWS Shared Responsibility Model (security *of* the cloud vs. security
*in* the cloud), IAM default-deny policy evaluation, root-user hygiene, multi-factor
authentication. **Analogous CWE:** CWE-269 (Improper Privilege Management) / CWE-287 (Improper
Authentication) — as categories describing the *misconceptions* this lesson corrects, not a
coding bug in any artifact.

## ✅ This lesson — what to do
1. **Before class** — complete the real AWS Academy Modules 1–3 in your Learner Lab sandbox
   (intro to cloud concepts, security fundamentals, and the IAM Knowledge Checks).
2. **This add-on (45–60 min, no Docker)** — an Audit-the-AI exercise on the Shared Responsibility
   Model and basic IAM hygiene, personalized per student.
3. **Submit** — worksheet → see [SUBMISSION.md](../../SUBMISSION.md).

## Get this lab onto your computer
You need your own copy of the course files. You download them once, then update them each
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
   You should see `README.md` and `worksheet.md`. There is no Docker and nothing to run in this
   lab: read `worksheet.md` here, or on GitHub with the link in the Classroom post.

## Objectives
- State the AWS Shared Responsibility Model's split precisely for an IaaS service like EC2: AWS
  secures the **infrastructure** (host hardware, hypervisor, physical facilities, and the network
  fabric underneath); the **customer** secures everything they put on top of it — guest operating
  system patching, application software, IAM configuration, and data.
- Explain why this split is different for a fully-managed service (e.g., a managed database or a
  serverless runtime), where AWS takes on more of the stack — and why EC2, specifically, does not
  get guest-OS patching from AWS.
- Explain IAM's **default-deny** evaluation model: a principal (user or role) with no attached
  policy has **no** access, not broad access that must be manually restricted.
- Explain why the AWS account **root user** should be reserved for the handful of tasks that
  require it, with an ordinary administrative IAM identity used for everyday work — and why MFA
  on the root user is a *second factor added to*, not a *replacement for*, a strong password.

## 🔎 Signature exercise — "Audit the AI"
No lab/flag this lesson (CONCEPTUAL) — the personalized, attributable artifact is **which planted
error your assigned AI explanation contains** (see `worksheet.md` Part 2a). Every student gets a
different variant (from a bank of 4, picked by the last digit of your student ID with the table in
`worksheet.md`); correctly identifying
*your own* variant's specific error is what's attributable — describing someone else's variant's
error does not satisfy the task.

**Why it's exciting:** each passage reads as a fluent, confident, plausible-sounding explanation
of a real AWS concept — the error is a single false claim that only someone who has actually
internalized *who is responsible for what* (not just the vocabulary) will catch.

## Deliverable
Which variant you were assigned, the exact planted error, why it's wrong, and the corrected
sentence — plus the four Part 1 short-answer questions if you're in the Conventional block instead. You may
answer in Thai or English.
Full tasks: `worksheet.md`.

## References
- AWS — *Shared Responsibility Model* (aws.amazon.com/compliance/shared-responsibility-model)
  (publicly available, general concept — no AWS Academy file used or copied).
- AWS IAM User Guide — *Security best practices in IAM*, *Policy evaluation logic* (implicit-deny
  default), *Root user best practices for your AWS account* (publicly available AWS
  documentation — no AWS Academy file used or copied).
