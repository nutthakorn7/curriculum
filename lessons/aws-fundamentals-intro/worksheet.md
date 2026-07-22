# Worksheet — {{ slot_label }}: AWS Fundamentals (Shared Responsibility & IAM Basics)

Section is assigned Block 1 = AIR-Sec or Block 2 = Conventional per `course-plan.md`'s block
table — complete only the part assigned to you this block.

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no personalized artifact — graded on the
writing itself):

1. Draw (or describe in words) the line the AWS Shared Responsibility Model draws for an EC2
   instance. What, specifically, is AWS responsible for, and what is the customer responsible
   for?
2. Guest operating system patching on an EC2 instance: whose job is it, and why does that answer
   change for a fully-managed service like a managed relational database or a serverless
   function runtime?
3. What does it mean for IAM to be "default-deny"? What access does a brand-new IAM user have
   the moment they're created, before any policy is attached?
4. Why does AWS recommend that day-to-day administrative work be done with an ordinary IAM
   identity rather than the account's root user? What is the root user supposed to be used for
   instead?

## Part 2 — AIR-Sec arm

### 2a. Audit the AI (personalized)
**Compute your variant number first: `variant = (last digit of your student ID) mod 4`.**
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

Report:
- Your variant number and the exact sentence containing the error.
- Why it's wrong (what actually happens instead).
- The corrected sentence.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 sentences a non-technical stakeholder could understand: why does "AWS runs the cloud" not
mean "AWS keeps your servers patched and secure for you"? Use the EC2 guest-OS example.

### 2c. Viva prompt (spot-check, in class)
Be ready to answer without notes: "If AWS patched the guest OS on every customer's EC2 instance
automatically, what would that mean for a customer who deliberately runs an old OS version or
custom kernel for compatibility reasons — and why is that a hint about who actually needs
control here?"

## Submit
Your variant + error + correction + Part 2b/2c → Classroom. Conventional-arm students submit
Part 1 only.
