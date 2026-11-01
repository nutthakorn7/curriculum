# Worksheet — {{ slot_label }}: AWS Fundamentals (Shared Responsibility & IAM Basics)

This lesson is **Block 1** per `course-plan.md`'s block table. Section A = Block 1 **AIR-Sec**;
Section B = Block 1 **Conventional**. Complete only the part assigned to your section this block.

**Language:** you may answer in Thai or English. Keep AWS names (EC2, IAM, root user, MFA) in
English. Short, clear answers are enough: 2–4 sentences per question.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no personalized artifact — graded on the
writing itself):

1. **Who does what for EC2?** Make two lists for an EC2 instance (a table or a drawing is fine):
   at least two things AWS takes care of, and at least two things you, the customer, take care of.
2. **Who patches the operating system?** On EC2, who installs security updates on the guest
   operating system? Is it the same for a managed database (Amazon RDS) or a Lambda function?
   Say why in one or two sentences.
3. **A brand-new IAM user.** You create an IAM user and attach no policy. What can this user do in
   AWS? Use this example to explain what "default-deny" means.
4. **The root user.** Why should you not use the root user for everyday work? What should you use
   instead, and what is the root user still needed for?

## Part 2 — AIR-Sec arm

### 2a. Audit the AI (personalized)
**Find your variant first** from the last digit of your student ID:

| Last digit of your student ID | Your variant |
|---|---|
| 0, 4 or 8 | 0 |
| 1, 5 or 9 | 1 |
| 2 or 6 | 2 |
| 3 or 7 | 3 |

Read *only* the passage for your variant below — each contains exactly one planted factual
error about the AWS Shared Responsibility Model or basic IAM hygiene.

> **Variant 0.** "The AWS Shared Responsibility Model splits duties between AWS and the
> customer. For a service like EC2, AWS is responsible for patching the guest operating system
> on your EC2 instances, since AWS manages all the underlying infrastructure. The customer is
> responsible for their application code, their data, and configuring IAM correctly."

> **Variant 1.** "AWS Identity and Access Management (IAM) is default-deny: a request is only
> allowed if some policy explicitly allows it, and an explicit deny always wins. However, **a
> brand-new IAM user, before any policy is ever attached to them, starts out with full access to
> every AWS service in the account** — administrators are expected to attach a policy afterward
> to narrow that access down to what the user actually needs."

> **Variant 2.** "AWS strongly recommends against using access keys or day-to-day sign-ins with
> the account's root user. Instead, create an ordinary administrative IAM identity for daily
> work and reserve the root user for the small set of tasks that specifically require it. **Once
> you've created that administrative IAM identity, the root user account itself can be deleted
> outright**, since AWS accounts don't actually need a root user to keep functioning."

> **Variant 3.** "Multi-factor authentication (MFA) adds a second authentication factor — a
> device-generated code or hardware key — on top of a user's sign-in. For the account root user
> in particular, **enabling MFA means a strong, unique root password is no longer necessary,
> since MFA alone is sufficient to secure the sign-in.**"

Write down:
- Your variant number and the last digit of your student ID.
- The wrong sentence, copied exactly.
- Why it is wrong: what really happens in AWS (1–2 sentences).
- The sentence rewritten so that it is correct.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why does
"AWS runs the cloud" not mean "AWS keeps your servers patched and secure for you"? Use the EC2
guest-OS example.

### 2c. Viva prompt (spot-check, in class)
Be ready to answer without notes: "Some companies keep an old operating system version on their
EC2 server because their app only works on that version. If AWS updated every customer's
operating system automatically, what would happen to them? What does that tell you about who
should control the updates?"

## Submit
Your variant + error + correction + Part 2b → Classroom. Viva (2c) is a live spot-check
during lab time or office hours, not a written submission. Conventional-arm students submit
Part 1 only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
