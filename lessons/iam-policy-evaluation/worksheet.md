# Worksheet — {{ slot_label }}: IAM Policy Evaluation

Section is assigned Block 1 = AIR-Sec or Block 2 = Conventional per `course-plan.md`'s block
table — complete only the part assigned to you this block.

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. What is the difference between an **identity-based** policy and a **resource-based** policy
   in AWS IAM? Give one example of each.
2. In Lab 3.1's setup, `devuser`'s identity policy does not include `s3:GetObject` or
   `s3:PutObject`. Explain why `devuser` (via `BucketsAccessRole`) can still read from bucket1
   and write to bucket2.
3. A resource-based policy has `"Principal": "*"`. What does this actually grant access to?
   Is it the same as "any AWS user in our account"? Why or why not?
4. Describe one real-world consequence of a public cloud storage bucket with an overly broad
   resource policy (you may reference a real incident you're aware of, or reason from first
   principles).
5. What does "least privilege" mean for a resource-based policy specifically, as opposed to an
   identity-based one?

## Part 2 — AIR-Sec arm

### 2a. The lab
Run the "Assume the Wrong Role" exercise (`README.md`). Record:
- The exact request (method, URL, headers) that got you the flag on the vulnerable app.
- The captured flag.
- The exact request you tried against the fixed app, and the response you got instead.

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
In 3–4 sentences a non-technical stakeholder could understand: why did scoping `Principal` to
`BucketsAccessRole` (instead of leaving it as `"*"`) fix the vulnerability, without removing any
legitimate access?

## Submit
Flag + Part 2a request/response pair + Part 2b/2c answers → Classroom. Conventional-arm students
submit Part 1 only.
