# Worksheet — {{ slot_label }}: S3 Static Website Hosting + Lambda/SNS Event-Driven Email

This lesson is **Block 1** per `course-plan.md`'s block table. Section A = Block 1 **AIR-Sec**;
Section B = Block 1 **Conventional**. Complete only the part assigned to your section this block.

**Language:** you may answer in Thai or English. Keep AWS names (S3, Lambda, SNS) and action
names (`s3:GetObject`, `s3:PutObject`) in English. Short, clear answers are enough: 2–4 sentences
per question.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. **Public read is normal.** To host a website on S3, the bucket policy lets everyone
   (`Principal: "*"`) do `s3:GetObject`. Why is this correct for a public website, and not a
   security mistake?
2. **Read and write.** Another bucket policy gives everyone (`Principal: "*"`) both
   `s3:GetObject` **and** `s3:PutObject`. What can an attacker do with this policy that they
   cannot do with the first one?
3. **Least privilege for a public bucket.** A website bucket must be readable by everyone. So what
   does "least privilege" mean for its bucket policy? (Hint: it does not mean "no public access".
   It means choosing exactly *which actions* are public.)
4. **What could go wrong?** Give one real result of a company website whose S3 bucket anyone can
   write to. You may name a real incident you know of, or describe what an attacker would do with
   write access to the company's homepage.
5. **Lambda and SNS.** In the AWS Academy exercise, a Lambda function publishes a message to an SNS
   topic, and an email address subscribed to that topic gets the message. Why does the Lambda
   function not need the email inbox to be online, reachable, or even subscribed yet at the moment
   it publishes? How is this different from a normal API call, where the caller waits for the
   answer?

## Part 2 — AIR-Sec arm

### 2a. The lab (flag capture)
Follow **Step-by-step** in `README.md` and copy its commands; each step shows what you should
see. Write down:
- The request that returned your flag from the vulnerable app (`:8105`): copy the whole `curl`
  command. Notice that it sends no `Authorization` header and no credentials of any kind.
- Your flag.
- What the vulnerable app's `index.html` shows when you read it again after your request (the
  site has really changed).
- The same request sent to the fixed app (`:8106`), and the response you got (the HTTP code and
  the `error`).
- Whether reading `index.html` with no credentials (`GET /bucket/website/index.html`) worked on
  **both** apps. It should: the fix did not break public read access.

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
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why does
removing `PutObject` from the public bucket-policy statement (and keeping `GetObject`) stop the
attack, while everyone can still see the website?

## Submit
Write your answers on the **Local03 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 03 (no PDF needed). AIR-Sec-arm students fill in Part 2: the flag and the
2a requests and responses, plus the 2b and 2c answers. Conventional-arm students fill in Part 1
only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
