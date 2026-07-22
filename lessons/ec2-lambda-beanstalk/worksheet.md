# Worksheet — {{ slot_label }}: EC2 Instance Roles, Lambda Basics, Elastic Beanstalk

Section is assigned Block 1 = AIR-Sec or Block 2 = Conventional per `course-plan.md`'s block
table — complete only the part assigned to you this block.

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. What is the difference between a **long-lived IAM user access key** embedded in an
   application and an **EC2 instance role**? Why is the instance-role approach generally
   considered more secure?
2. Describe, in your own words, what the **Instance Metadata Service (IMDS)** is for and why it
   is only reachable from processes running *on* the instance itself (not from the public
   internet).
3. A web application running on an EC2 instance has a feature that fetches a user-supplied URL
   and returns its contents (e.g., a link-preview or webhook-test feature). Explain how an
   attacker could abuse this feature to steal the instance's IAM role credentials, even without
   ever directly reaching the metadata service themselves. What is the general name for this
   class of vulnerability?
4. Name at least two concrete defenses an application could use to prevent the attack described
   in Q3, beyond "just block the exact string 169.254.169.254."
5. **Lambda basics:** in your own words, what is the key operational difference between running
   code on an EC2 instance you manage yourself versus running the same logic as an AWS Lambda
   function? Name one class of security concern that changes (for better or worse) when you move
   from EC2 to Lambda.
6. **Elastic Beanstalk / auto-scaling:** Elastic Beanstalk can provision a load balancer in front
   of an auto-scaling group of instances. Explain, conceptually, why an application's IAM
   instance-role misconfiguration (like the one in this lesson) becomes *more* consequential — not
   less — once it's running across an auto-scaling group instead of a single instance.

## Part 2 — AIR-Sec arm

### 2a. The lab (flag capture)
Run the "Ask the App to Fetch Its Own Secrets" exercise (`README.md`). Record:
- The exact request (`POST /fetch-preview` body) that got you the flag on the vulnerable app.
- The captured flag.
- The exact request you tried against the fixed app, and the response you got instead.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 sentences a non-technical stakeholder could understand: why does a "fetch this URL for
me" feature on a cloud server create a path to stealing that server's cloud credentials, and why
does simply blocking the address `169.254.169.254` as a literal string not fully fix it (hint:
think about what other hostnames could reach the same feature, e.g. `localhost`)?

### 2c. Viva spot-check
Be ready to answer verbally, without notes, in under 2 minutes:
- Why does the metadata route in this lab still "work correctly" from the server's own point of
  view — i.e., why is the bug not in the metadata endpoint at all?
- If you changed only one line in `vulnerable_app.py` to fix this, what would it be, and what
  category of check does it add (allowlist vs. blocklist vs. authentication)?
- Why would adding a login requirement to `/fetch-preview` alone (with no URL validation) *not*
  fix this vulnerability?

## Submit
Flag + Part 2a request/response pair + Part 2b answer → Classroom. Viva (2c) is a live spot-check
during lab time or office hours, not a written submission. Conventional-arm students submit
Part 1 only.
