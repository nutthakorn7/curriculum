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
1. **Before class** — complete the real AWS Academy Lab 5.1 in your Learner Lab sandbox (SSE-KMS
   setup, uploading/viewing an encrypted object, the CloudTrail `GenerateDataKey` event).
2. **This add-on (45–60 min, no Docker)** — an Audit-the-AI exercise on the envelope-encryption
   concept, personalized per student.
3. **Submit** — worksheet → Classroom.

## Objectives
- Explain **envelope encryption**: why S3 asks KMS for a *data key* instead of asking KMS to
  encrypt the object directly, and what KMS actually returns (a plaintext copy **and** an
  encrypted copy of that data key).
- State precisely what S3 keeps and what it discards after encrypting an object with SSE-KMS.
- Explain the **blast radius** of disabling or deleting a KMS key: every object ever encrypted
  under that key becomes permanently unreadable, because the *encrypted* data key stored in each
  object's metadata can no longer be decrypted.

## 🔎 Signature exercise — "Audit the Envelope"
No lab/flag this lesson (CONCEPTUAL) — the personalized, attributable artifact is **which planted
error your assigned AI explanation contains** (see `worksheet.md` Part 2a). Every student gets a
different variant (`variant = (last digit of your student ID) mod 4`, from a bank of 4); correctly identifying
*your own* variant's specific error is what's attributable — describing someone else's variant's
error does not satisfy the task.

**Why it's exciting:** the AI's explanation reads completely fluently and confidently — the error
is a one-word/one-clause swap that only someone who actually understands the *data flow* (not
just the vocabulary) will catch.

## Deliverable
Which variant you were assigned, the exact planted error, why it's wrong, and the corrected
sentence — plus the two Part 1 essay-style questions if you're in the Conventional block instead.
Full tasks: `worksheet.md`.

## References
- AWS KMS documentation — *How envelope encryption works*, *Amazon S3 encryption with AWS KMS
  (SSE-KMS)* (publicly available, general concept — no AWS Academy file used or copied).
- AWS docs — *Deleting AWS KMS keys* (blast-radius / irreversibility warnings AWS itself
  publishes).
