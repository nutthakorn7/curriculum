# Worksheet — {{ slot_label }}: S3 Server-Side Encryption with KMS

Section is assigned Block 1 = AIR-Sec or Block 2 = Conventional per `course-plan.md`'s block
table — complete only the part assigned to you this block.

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no personalized artifact — graded on the
writing itself):

1. Walk through, step by step, what happens between "you click Upload on an object in an
   SSE-KMS bucket" and "the object is stored encrypted." What does S3 ask KMS for, and what does
   KMS send back?
2. What, specifically, does S3 store in the object's metadata after encryption — and what does
   it deliberately discard?
3. If your organization disables (or schedules deletion of) the KMS key used to encrypt an S3
   bucket's objects, what happens to objects already stored there? Why?
4. Why does envelope encryption use a separate "data key" per object/operation instead of just
   asking KMS to encrypt every object directly with the customer master key (CMK) itself?

## Part 2 — AIR-Sec arm

### 2a. Audit the Envelope (personalized)
**Compute your variant number first: `variant = (last digit of your student ID) mod 4`.**
Read *only* the passage for your variant below — each contains exactly one planted factual
error about how SSE-KMS envelope encryption actually works.

> **Variant 0.** "When you upload a file to an S3 bucket configured with SSE-KMS, S3 sends a
> request to AWS KMS for a new data key. KMS generates a plaintext data key and returns both the
> plaintext copy and an encrypted copy of it. S3 uses the plaintext data key to encrypt your
> object, then stores the **plaintext data key alongside the encrypted object** in the bucket
> for faster future decryption, discarding only the encrypted copy."

> **Variant 1.** "...KMS generates a plaintext data key and returns both copies to S3. S3
> encrypts your object using the plaintext data key, discards the plaintext copy immediately,
> and stores the encrypted copy of the data key in the object's metadata. Because the encrypted
> data key is stored right there in S3, **decrypting the object never requires contacting KMS
> again** — S3 can decrypt it locally using its own master key."

> **Variant 2.** "...If you disable the KMS key that was used to encrypt an object, **the object
> remains readable indefinitely**, because S3 always caches a working copy of the plaintext data
> key for objects it has previously decrypted at least once — so disabling the key only blocks
> *new* uploads, not existing reads."

> **Variant 3.** "...The data key AWS KMS generates for envelope encryption is a **long-term key
> used to encrypt every object in the bucket**, similar to how the bucket's KMS master key
> works — one data key per bucket, reused across all uploads for efficiency."

Report:
- Your variant number and the exact sentence containing the error.
- Why it's wrong (what actually happens instead).
- The corrected sentence.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 sentences a non-technical stakeholder could understand: why does disabling a KMS key
make old data permanently unreadable, when disabling, say, a database user account usually
doesn't destroy the database's existing data?

### 2c. Viva prompt (spot-check, in class)
Be ready to answer without notes: "If S3 kept the plaintext data key around after encrypting,
what would that defeat the *entire point* of envelope encryption?"

## Submit
Your variant + error + correction + Part 2b/2c → Classroom. Conventional-arm students submit
Part 1 only.
