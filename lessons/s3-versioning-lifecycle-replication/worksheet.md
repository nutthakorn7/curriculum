# Worksheet — {{ slot_label }}: S3 Versioning, Lifecycle, and Cross-Region Replication

Section is assigned Block 1 = AIR-Sec or Block 2 = Conventional per `course-plan.md`'s block
table — complete only the part assigned to you this block.

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no personalized artifact — graded on the
writing itself):

1. A teammate accidentally overwrites an important object in an S3 bucket that has **versioning**
   enabled. Walk through what actually happened to the original object's data, and how your
   teammate can recover it. Would the outcome be different if versioning had never been enabled?
2. What does a **lifecycle rule** that "transitions objects to a colder storage tier after 30
   days" actually do to (a) the *current* version of an object in a versioning-enabled bucket,
   and (b) any *noncurrent* (older) versions of that same object? Are these the same action, or
   two different lifecycle actions?
3. Your team enables **cross-region replication (CRR)** on a bucket that already holds two years
   of existing objects, intending it as a disaster-recovery (DR) measure. The day after enabling
   it, does the destination bucket in the other region contain a full copy of those two years of
   existing objects? Justify your answer, and explain what (if anything) you would need to do to
   get a complete copy of the pre-existing objects into the destination bucket.
4. Once you enable versioning on a bucket, can you later configure the bucket back to its
   original **unversioned** state? What is the only other state change available, and how does it
   differ from a true "undo" of versioning?

## Part 2 — AIR-Sec arm

### 2a. Audit the Backup Plan (personalized)
**Compute your variant number first: `variant = (last digit of your student ID) mod 4`.**
Read *only* the passage for your variant below — each contains exactly one planted factual error
about how S3 versioning, lifecycle rules, or cross-region replication actually work.

> **Variant 0.** "Once you enable cross-region replication on your S3 bucket, all of your
> bucket's existing objects are automatically copied to the destination bucket, giving you an
> instant disaster-recovery backup. From that point forward, both the objects that were already
> there and any new objects you upload will be kept in sync between the two regions."

> **Variant 1.** "A lifecycle rule that transitions objects to a colder storage tier after 30
> days will also reach back and transition any versions that have already expired or been
> permanently deleted under a separate expiration rule — since the transition rule re-scans the
> bucket's full history, it restores those expired versions just long enough to move them to the
> colder tier before removing them again."

> **Variant 2.** "Enabling versioning on an S3 bucket is a fully reversible setting: if you decide
> you no longer want version history, you can switch the bucket back to its original unversioned
> state at any time, and Amazon S3 will discard the stored version history and return the bucket
> to exactly how it behaved before versioning was ever turned on."

> **Variant 3.** "S3 Versioning is very storage-efficient because each new version you upload is
> stored only as a small diff against the previous version, not as a full copy of the object —
> so keeping ten versions of a large file costs only slightly more than storing the object once."

Report:
- Your variant number and the exact sentence(s) containing the error.
- Why it's wrong (what actually happens instead).
- The corrected sentence.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 sentences a non-technical stakeholder could understand: why can't you treat "turning on
cross-region replication" as an instant, one-time backup of everything already in the bucket —
and what would you actually need to do to make sure years of old data is protected in the same way
as new uploads?

### 2c. Viva prompt (spot-check, in class)
Be ready to answer without notes: "If your company enabled CRR on a bucket six months ago but
never ran a Batch Replication job for the objects that existed before that day, and the primary
region is destroyed today, what happens to those older objects — and whose assumption was wrong?"

## Submit
Your variant + error + correction + Part 2b/2c → Classroom. Conventional-arm students submit
Part 1 only.
