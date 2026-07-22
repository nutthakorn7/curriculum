# Worksheet — {{ slot_label }}: S3 Static Website Hosting + Lambda/SNS Event-Driven Email

Section is assigned Block 1 = AIR-Sec or Block 2 = Conventional per `course-plan.md`'s block
table — complete only the part assigned to you this block.

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. When you enable S3 static website hosting, the bucket policy must grant `Principal: "*"`
   the `s3:GetObject` action. Explain why this is the **correct, intended** configuration for a
   public website, not a security mistake in itself.
2. Now explain the difference between that correct configuration and one that **also** grants
   `Principal: "*"` the `s3:PutObject` action. What can an attacker do with the second
   configuration that they cannot do with the first?
3. What does "least privilege" mean for a static-website bucket's resource policy, given that
   the bucket's whole purpose is to be publicly readable? (Hint: least privilege doesn't mean
   "no public access" here — it means being precise about *which* actions are public.)
4. Describe one real-world consequence of a publicly-writable cloud storage bucket hosting a
   website (you may reference a real defacement/incident you're aware of, or reason from first
   principles about what an attacker would do with write access to a company's homepage).
5. In the AWS Academy Lambda + SNS event-driven email exercise, a Lambda function publishes a
   message to an SNS topic, and a subscribed email address receives a notification. Explain why
   the Lambda function does **not** need the subscriber's email client or inbox to be online,
   reachable, or even subscribed yet at the exact moment it publishes. How is this different
   from a normal request-response API call, where the caller waits for the callee to respond?

## Part 2 — AIR-Sec arm

### 2a. The lab
Run the "Deface the Site" exercise (`README.md`). Record:
- The exact request (method, URL, headers, body) that got you the flag on the vulnerable app.
- The captured flag.
- The exact request you tried against the fixed app, and the response you got instead.
- Confirm (and note in your answer) that anonymous `GET /bucket/website/index.html` still
  succeeds on **both** apps — the fix did not break public read access.

### 2b. Audit-the-AI
Below is an AI-generated S3 bucket policy the AI claims is "the standard policy for static
website hosting." Find the planted flaw and explain, in plain English, what it actually grants.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicWebsiteAccess",
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-company-website/*"
    }
  ]
}
```

Hint: static website hosting only requires visitors' browsers to *read* pages. Does a visitor's
browser ever need to *write* to the bucket for the website to work? What does it mean that this
single statement's `Principal` is `"*"` for **both** actions listed?

### 2c. EiPE (Explain-in-Plain-English)
In 3–4 sentences a non-technical stakeholder could understand: why does removing `PutObject`
from the public bucket-policy statement (while keeping `GetObject`) fix the vulnerability
without breaking the website for visitors?

## Submit
Flag + Part 2a request/response pair + Part 2b/2c answers → Classroom. Conventional-arm students
submit Part 1 only.
