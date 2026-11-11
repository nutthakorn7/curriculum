# Worksheet — {{ slot_label }}: S3 Server-Side Encryption with KMS

This lesson is **Block 2** per `course-plan.md`'s block table. Section A = Block 2 **Conventional**;
Section B = Block 2 **AIR-Sec** (reversed from Block 1). Complete only the part assigned to your
section this block.

**Language:** you may answer in Thai or English. Keep AWS names (S3, KMS, SSE-KMS, data key,
`GenerateDataKey`) in English. Short, clear answers are enough: 2–4 sentences per question.

**Scenario assumption:** use per-object SSE-KMS without S3 Bucket Keys. S3 does not retain a
plaintext data key between object requests. This keeps the key-state questions focused on the
envelope-encryption flow taught in this lesson.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no personalized artifact — graded on the
writing itself):

1. **From Upload to encrypted.** Your S3 bucket uses SSE-KMS. Step by step, what happens between
   "you click Upload" and "the object is stored encrypted"? What does S3 ask KMS for, and what does
   KMS send back?
2. **Kept and thrown away.** After the object is encrypted, what does S3 store in the object's
   metadata? What does it throw away on purpose?
3. **Turning the key off.** Under the stated scenario assumptions, compare disabling the KMS key,
   scheduling it for deletion, and completed deletion. What happens to the encrypted objects and
   to reads that require KMS decryption? Which states are reversible? If pending deletion is
   cancelled, what must happen before the key can be used again?
4. **Why a data key?** Why does envelope encryption use a separate "data key" for each
   object (or operation), instead of asking KMS to encrypt every object directly with the
   customer master key (CMK)?

## Part 2 — AIR-Sec arm

### 2a. Audit the Envelope (personalized)
**Find your variant first** from the last digit of your student ID:

| Last digit of your student ID | Your variant |
|---|---|
| 0, 4 or 8 | 0 |
| 1, 5 or 9 | 1 |
| 2 or 6 | 2 |
| 3 or 7 | 3 |

Read *only* the passage for your variant below — each contains exactly one planted factual
error about how SSE-KMS envelope encryption actually works.

> **Variant 0.** "When you upload a file to an S3 bucket configured with SSE-KMS, S3 sends a
> request to AWS KMS for a new data key. KMS generates a plaintext data key and returns both the
> plaintext copy and an encrypted copy of it. S3 uses the plaintext data key to encrypt your
> object, then stores the plaintext data key alongside the encrypted object in the bucket
> for faster future decryption, discarding only the encrypted copy."

> **Variant 1.** "...KMS generates a plaintext data key and returns both copies to S3. S3
> encrypts your object using the plaintext data key, discards the plaintext copy immediately,
> and stores the encrypted copy of the data key in the object's metadata. Because the encrypted
> data key is stored right there in S3, decrypting the object never requires contacting KMS
> again — S3 can decrypt it locally using its own master key."

> **Variant 2.** "...If you disable the KMS key that was used to encrypt an object, the object
> remains readable indefinitely, because S3 always caches a working copy of the plaintext data
> key for objects it has previously decrypted at least once — so disabling the key only blocks
> *new* uploads, not existing reads."

> **Variant 3.** "...The data key AWS KMS generates for envelope encryption is a long-term key
> used to encrypt every object in the bucket, similar to how the bucket's KMS master key
> works — one data key per bucket, reused across all uploads for efficiency."

Write down:
- Your variant number and the last digit of your student ID.
- The wrong sentence, copied exactly.
- Why it is wrong: what really happens with SSE-KMS (1–2 sentences).
- The sentence rewritten so that it is correct.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why does
disabling a KMS key make old data unreadable (until the key is turned back on), even though the
encrypted objects are still in the bucket? Why does disabling one database user account *not* make
the database's data unreadable? And how is *deleting* the key different from disabling it?

### 2c. Viva prompt (spot-check, in class)
Be ready to answer without notes: "If S3 kept the plaintext data key after encrypting, why would
that defeat the *whole point* of envelope encryption?"

## Submit
Write your answers on the **Local08 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 08 (no PDF needed). AIR-Sec-arm students fill in Part 2: the variant, the
error and its correction from 2a, plus the 2b answer. The viva (2c) is a live spot-check during
lab time or office hours, not a written answer. Conventional-arm students fill in Part 1 only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
