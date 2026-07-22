# {{ slot_label }} — S3 Data Protection: Versioning, Lifecycle, and Cross-Region Replication

**Topic (source):** S3 data protection strategies — versioning, lifecycle rules, and cross-region
replication (CRR) — same general concept as AWS Academy's static-website challenge lab, described
here in original words, **not copied**. No AWS Academy file, scenario, character name, or exact
lab wording is referenced anywhere in this lesson. **Kind:** CONCEPTUAL (no exploitable target —
architecture/analysis lesson, same precedent as {{ ref('kms-envelope-encryption') }}).
**Concepts:** object versioning (accidental delete/overwrite protection), lifecycle rules
(storage-tier transitions and expiration of old versions), cross-region replication as a
disaster-recovery (DR) strategy, and — critically — **what CRR does and does not do
automatically**. **Analogous CWE:** CWE-1188-adjacent (Insecure Default Initialization of a
Resource, applied loosely — this lesson is about correct configuration assumptions, not a coding
bug) / general data-protection misconfiguration category.

## This lesson — what to do
1. **Before class** — complete the real AWS Academy challenge lab in your Learner Lab sandbox
   (the "static website" lab that exercises S3 versioning, lifecycle rules, and cross-region
   replication).
2. **This add-on (45–60 min, no Docker)** — an Audit-the-AI exercise on versioning/lifecycle/CRR
   concepts, personalized per student.
3. **Submit** — worksheet → Classroom.

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
different variant (`variant = (last digit of your student ID) mod 4`, from a bank of 4).
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
sentence — plus the Part 1 essay-style questions if you're in the Conventional block instead.
Full tasks: `worksheet.md`.

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
