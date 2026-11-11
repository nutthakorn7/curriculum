# Worksheet — {{ slot_label }}: IAM Policy Evaluation

This lesson is **Block 2** per `course-plan.md`'s block table. Section A = Block 2 **Conventional**;
Section B = Block 2 **AIR-Sec** (reversed from Block 1). Complete only the part assigned to your
section this block.

**Language:** you may answer in Thai or English. Keep AWS names (IAM, S3, `BucketsAccessRole`,
`Principal`) and actions such as `s3:GetObject` / `s3:PutObject` in English. Short, clear answers
are enough: 2–4 sentences per question.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. **Two kinds of policy.** What is the difference between an **identity-based** policy and a
   **resource-based** policy in AWS IAM? Give one example of each.
2. **Access without an identity grant.** In the AWS Academy lab (Lab 3.1, *Using Resource-Based
   Policies to Secure an S3 Bucket*), `devuser`'s identity policy has no `s3:GetObject` and no
   `s3:PutObject`. So why can `devuser`, by using `BucketsAccessRole`, still read from bucket1 and
   write to bucket2?
3. **`"Principal": "*"`.** A resource-based policy has `"Principal": "*"`. Who does this really
   give access to? Is it the same as "any AWS user in our account"? Say why or why not.
4. **What could go wrong?** Give one real result of a public cloud storage bucket whose resource
   policy is too broad. You may name a real incident you know of, or explain what could happen.
5. **Least privilege for a bucket.** What does "least privilege" mean for a resource-based policy,
   compared with an identity-based policy?

## Part 2 — AIR-Sec arm

### 2a. The lab

```sim
iam-evaluation
```

Do the lab with the **Step-by-step** section of `README.md` ("Assume the Wrong Role"). Write down:
- The whole `curl` command that got you the flag from the vulnerable app (`:8107`). Note which
  headers it sent, and which it did not.
- Your flag.
- The same request sent to the fixed app (`:8108`), and the response you got instead (the HTTP
  code and the error).

### 2b. Audit-the-AI
Below is an AI-generated S3 bucket policy the AI claims is "secure and scoped to only our
internal application role." Find the planted flaw and explain, in plain English, what it
actually grants.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AppReadWrite",
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::internal-app-bucket/*",
      "Condition": {
        "StringEquals": { "aws:PrincipalTag/team": "backend" }
      }
    }
  ]
}
```

Hint: check whether `Principal: "*"` combined with a `Condition` on a *tag* actually restricts
who can match — does an anonymous, unauthenticated caller have any `PrincipalTag` at all?

### 2c. EiPE (Explain-in-Plain-English)
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why did
changing `Principal` from `"*"` to `BucketsAccessRole` fix the vulnerability, without taking away
any access that was supposed to be there?

## Submit
Write your answers on the **Local06 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 06 (no PDF needed). AIR-Sec-arm students fill in Part 2: the 2a lab evidence
and the flag, plus the 2b and 2c answers. Conventional-arm students fill in Part 1 only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
