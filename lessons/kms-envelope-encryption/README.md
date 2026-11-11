# {{ slot_label }} — S3 Server-Side Encryption with KMS (Envelope Encryption)

**Topic (source):** Shinya's own notes for AWS Academy Cloud Security Foundations Lab 5.1
(SSE-KMS setup, `GenerateDataKey` CloudTrail event, and the "instance won't start after the KMS
key is disabled" scenario), described here in our own words — **not** copied from any AWS
Academy file. **Kind:** CONCEPTUAL (no exploitable target — this is an architecture/analysis
lesson, same precedent as `software-security`'s threat-modeling week and
`security-cryptography`'s asymmetric-encryption week).
**Concepts:** envelope encryption, data keys vs. customer master keys, ciphertext blast radius
when a key is disabled/deleted · **Analogous CWE:** CWE-320 (Key Management Errors, as a
category — this lesson is about correct KMS use, not a coding bug).

## ✅ This lesson — what to do
1. **Week 15 (100-minute class)** — study AWS Academy Cloud Security Foundations Module 5 and
   complete Lab 5.1 (*Encrypting Data at Rest by Using AWS KMS*) in the scheduled 75-minute lab.
   Record the S3 SSE-KMS, CloudTrail KMS-event and EBS/key-access observations requested by the
   current LMS instructions. Preview Local 08; do not answer or submit its worksheet this week.
2. **Week 16 (100-minute class)** — use the Week 15 observations in the local conceptual workshop.
   Complete only your assigned Part of the worksheet; the 45–60-minute analysis portion needs no
   Docker, local target, or AWS console.
3. **Submit by Mon 22 Feb 2027, 23:59** — fill in your Classroom **Local08 Answer Sheet** copy and
   click Turn in. See [SUBMISSION.md](../../SUBMISSION.md).

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
   even if you downloaded them last week. Your answers remain in Classroom.
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
   You should see `README.md` and `worksheet.md`. There is no Docker and nothing to run in this
   lab: read `worksheet.md` here, or on GitHub with the link in the Classroom post.

## Objectives
- Explain **envelope encryption**: why S3 asks KMS for a *data key* instead of asking KMS to
  encrypt the object directly, and what KMS actually returns (a plaintext copy **and** an
  encrypted copy of that data key).
- State precisely what S3 keeps and what it discards after encrypting an object with SSE-KMS.
- Under the worksheet's stated per-object SSE-KMS assumptions, explain the **blast radius** of
  disabling vs. deleting a customer managed KMS key. Reads that need a fresh KMS decryption fail
  while the key is disabled or pending deletion; re-enabling restores that path. Completed deletion
  after the mandatory 7–30-day waiting period is irreversible, so objects that still depend on that
  key cannot be decrypted. S3 Bucket Keys and data keys already in use can change the timing of an
  observed failure; do not generalize the worksheet model to every AWS service or configuration.

## 🔎 Signature exercise — "Audit the Envelope"
No lab/flag this lesson (CONCEPTUAL) — the personalized, attributable artifact is **which planted
error your assigned AI explanation contains** (see `worksheet.md` Part 2a). Every student gets a
different variant (from a bank of 4, picked by the last digit of your student ID with the table in
`worksheet.md`); correctly identifying
*your own* variant's specific error is what's attributable — describing someone else's variant's
error does not satisfy the task.

**Why it's exciting:** the AI's explanation reads completely fluently and confidently — the error
is a one-word/one-clause swap that only someone who actually understands the *data flow* (not
just the vocabulary) will catch.

## Deliverable
Which variant you were assigned, the exact planted error, why it's wrong, and the corrected
sentence, plus the Part 2b answer (the 2c viva is oral) — or the four Part 1 short-answer questions
if you're in the Conventional block instead. You may answer in Thai or English. Write your answers
on the **Local08 Answer Sheet** copy in Classroom and click Turn in (no PDF needed). Full tasks:
`worksheet.md`.

## References
- [Amazon S3 SSE-KMS workflow](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html)
  and [S3 Bucket Keys](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-key.html).
- [How unusable KMS keys affect data keys](https://docs.aws.amazon.com/kms/latest/developerguide/unusable-kms-keys.html),
  [deleting KMS keys](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html),
  and [cancelling deletion](https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys-cancelling-key-deletion.html).
