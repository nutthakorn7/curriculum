# {{ slot_label }} — S3 Data Protection: Versioning, Lifecycle, and Cross-Region Replication

**Topic:** S3 data protection strategies — versioning, lifecycle rules, and cross-region
replication (CRR), described here in original words. No AWS Academy file, scenario, character
name, or exact lab wording is referenced anywhere in this lesson. **Kind:** CONCEPTUAL (no
exploitable target —
architecture/analysis lesson, same precedent as {{ ref('kms-envelope-encryption') }}).
**Concepts:** object versioning (accidental delete/overwrite protection), lifecycle rules
(storage-tier transitions and expiration of old versions), cross-region replication as a
disaster-recovery (DR) strategy, and — critically — **what CRR does and does not do
automatically**. **Analogous CWE:** CWE-1188-adjacent (Insecure Default Initialization of a
Resource, applied loosely — this lesson is about correct configuration assumptions, not a coding
bug) / general data-protection misconfiguration category.

## This lesson — what to do
1. **Week 07** — study Cloud Foundations Module 8 and complete its assigned RDS lab in AWS
   Academy. In the local workshop, use the Week 07 S3 supplement slides to work on versioning
   and lifecycle. Start only the questions for these topics in your assigned Part.
2. **Week 08** — study Cloud Foundations Module 9 and use the Week 08 S3 supplement slide for
   replication and recovery. Complete the remaining questions in your assigned Part during the
   45–60 minute local workshop. This add-on needs no extra AWS console lab or Docker.
3. **Submit** — complete the Local04 Answer Sheet in the Week 08 Classroom Assignment by its
   posted deadline; see [SUBMISSION.md](../../SUBMISSION.md).

For Week 07, Conventional students can work on Part 1 Questions 1, 2 and 4. AIR-Sec students
can find their variant and work on its versioning or lifecycle claim if applicable. Leave the
replication and recovery questions or claim until the Week 08 workshop teaches them.

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
- Explain why enabling **versioning** on a bucket protects against accidental delete and
  accidental overwrite, and what actually happens to an object's prior contents when a new
  version is uploaded or a "delete" is issued.
- Explain what a **lifecycle rule** does: moving (transitioning) older object versions to a
  colder, cheaper storage class, and permanently expiring versions after a retention window —
  and which lifecycle actions apply to the *current* version versus *noncurrent* versions.
- Explain **cross-region replication (CRR)** as a disaster-recovery strategy, including the
  precise scope of what gets replicated automatically versus what requires a separate one-time
  action.
- State precisely why enabling CRR on a bucket that already contains objects does **not** by
  itself back-copy those pre-existing objects to the destination region — and what AWS feature
  closes that gap.

## Signature exercise — "Audit the Backup Plan"
No lab/flag this lesson (CONCEPTUAL) — the personalized, attributable artifact is **which planted
error your assigned AI explanation contains** (see `worksheet.md` Part 2a). Every student gets a
different variant (from a bank of 4, picked by the last digit of your student ID with the table in
`worksheet.md`).
Correctly identifying *your own* variant's specific error is what's attributable — describing
someone else's variant's error does not satisfy the task.

**Why it's exciting:** each passage reads like a confident, helpful AI assistant summarizing a
data-protection feature — and each one contains exactly one plausible-sounding but factually
wrong claim about versioning, lifecycle, or replication. The errors are the kind a rushed
engineer could genuinely believe and act on — for example, treating CRR as an instant, complete
backup the moment it's switched on, which would leave a real gap in an actual disaster-recovery
plan.

## Deliverable
Which variant you were assigned, the exact planted error, why it's wrong, and the corrected
sentence — plus the four Part 1 short-answer questions if you're in the Conventional block instead.
You may answer in Thai or English. Write your answers on the **Local04 Answer Sheet** copy in
Classroom and click Turn in (no PDF needed). Full tasks: `worksheet.md`.

## References
- AWS S3 documentation — *What does Amazon S3 replicate?* (scope of live replication: only
  objects created/updated after the replication configuration is added).
- AWS S3 documentation — *Replicating existing objects with S3 Batch Replication* (the separate,
  one-time job required to replicate objects that existed before a replication rule was created).
- AWS S3 documentation — *Retaining multiple versions of objects with S3 Versioning* (unversioned
  / versioning-enabled / versioning-suspended states; versioning cannot be reverted to
  unversioned, only suspended).
- AWS S3 documentation — *Lifecycle configuration elements* and the lifecycle-actions/versioning
  state table (how `Transition`, `Expiration`, `NoncurrentVersionTransition`, and
  `NoncurrentVersionExpiration` behave differently on current vs. noncurrent versions).

All references are to AWS's own publicly available S3 user-guide documentation describing general
product behavior — no AWS Academy course file was used or copied.
