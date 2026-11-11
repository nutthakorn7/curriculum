# Worksheet — {{ slot_label }}: S3 Versioning, Lifecycle, and Cross-Region Replication

This lesson is **Block 1** per `course-plan.md`'s block table. Section A = Block 1 **AIR-Sec**;
Section B = Block 1 **Conventional**. Complete only the part assigned to your section this block.

**Language:** you may answer in Thai or English. Keep AWS names (S3, versioning, lifecycle rule,
storage class, cross-region replication) in English. Short, clear answers are enough: 2–4
sentences per question.

## Weekly scope

- **Week 07:** Complete the assigned Cloud Foundations Module 8 database lab. In the local
  workshop, learn versioning and lifecycle from the Week 07 S3 supplement slides. Conventional
  students can answer Part 1 Questions 1, 2 and 4. AIR-Sec students can identify their variant
  and work on a versioning or lifecycle claim if that is their assigned variant.
- **Week 08:** Study Cloud Foundations Module 9. Learn replication and recovery from the Week 08
  S3 supplement slide before answering those questions. Conventional students complete Part 1
  Question 3; AIR-Sec students finish Part 2a and 2b and prepare for the Part 2c viva. Submit
  only your assigned Part in the Week 08 Classroom Assignment by its posted deadline.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no personalized artifact — graded on the
writing itself):

1. **An overwritten object.** Your S3 bucket has **versioning** turned on. A teammate uploads a new
   file with the same name and overwrites an important object by mistake. What happened to the
   old data? How can your teammate get it back? What would be different if versioning had never
   been turned on?
2. **A 30-day lifecycle rule.** A **lifecycle rule** says "move objects to a colder (cheaper)
   storage class after 30 days". The bucket has versioning turned on. What does this rule do to
   (a) the *current* version of an object, and (b) the *noncurrent* (older) versions of the same
   object? Is that one lifecycle action, or two different ones?
3. **Replication on a bucket that already has data.** Your bucket already holds two years of
   objects. Your team turns on **cross-region replication (CRR)** as a disaster-recovery (DR)
   backup. The next day, does the bucket in the other region have a full copy of those two years
   of old objects? Say why. What, if anything, would you need to do to get a full copy of the old
   objects into that bucket?
4. **Turning versioning off again.** After versioning is turned on, can you set the bucket back
   to how it was before (**unversioned**)? What is the only other state you can move it to, and
   why is that not the same as a real "undo"?

## Part 2 — AIR-Sec arm

### 2a. Audit the Backup Plan (personalized)
**Find your variant first** from the last digit of your student ID:

| Last digit of your student ID | Your variant |
|---|---|
| 0, 4 or 8 | 0 |
| 1, 5 or 9 | 1 |
| 2 or 6 | 2 |
| 3 or 7 | 3 |

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

Write down:
- Your variant number and the last digit of your student ID.
- The wrong sentence(s), copied exactly.
- Why it is wrong: what really happens in S3 (1–2 sentences).
- The sentence rewritten so that it is correct.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why is
"turning on cross-region replication" not an instant, one-time backup of everything already in
the bucket? What would you need to do so that years of old data is protected in the same way as
new uploads?

### 2c. Viva prompt (spot-check, in class)
Be ready to answer without notes: "Your company turned on CRR for a bucket six months ago.
Nobody ever ran a Batch Replication job for the objects that were already in the bucket before
that day. Today the main region is destroyed. What happens to those older objects? Whose
assumption was wrong?"

## Submit
Write your answers on the **Local04 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 04 (no PDF needed). AIR-Sec-arm students fill in Part 2: the variant, the
error and its correction from 2a, plus the 2b answer. The viva (2c) is a live spot-check during
lab time or office hours, not a written answer. Conventional-arm students fill in Part 1 only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
