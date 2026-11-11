# Worksheet — {{ slot_label }}: VPC Networking

This lesson is **Block 2** per `course-plan.md`'s block table. Section A = Block 2 **Conventional**;
Section B = Block 2 **AIR-Sec** (reversed from Block 1). Complete only the part assigned to your
section this block.

**Language:** you may answer in Thai or English. Keep AWS names (VPC, security group, network ACL,
NAT gateway, CIDR) in English. Short, clear answers are enough: 2–4 sentences per question.

**Weekly scope:** Week 13 is reserved for AWS Academy Module 4 and Lab 4.1. Bring forward
your Week 03 VPC diagram and Week 13 notes, but do not submit Local 07 yet. In the Week 14
workshop, complete only your assigned part; Part 2 runs the local Docker simulation on your
own computer. Submit in the Week 14 Classroom Assignment by its due date. The earlier VPC
diagram is a study aid, not a separate Local 07 deliverable.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. **Security group or network ACL?** What is the difference between a **security group** and a
   **network ACL** in a VPC? Answer both parts: (a) which one is stateful and which is stateless,
   and (b) what that means for the reply to a request. Use this example: an inbound rule allows
   traffic to a web server on port 443. Does the reply going back out need its own rule?
2. **Allow only, or allow and deny?** Security groups can only **allow**; network ACLs can
   **allow** and **deny**. How does this change the way you use each one? Why might you still
   want an explicit deny at the subnet level, when your security groups already block everything
   you did not allow?
3. **First match wins.** AWS checks network ACL rules from the **lowest rule number up, and stops
   at the first match**. In your own words, why does it work this way? What would go wrong, or
   just be different, if it checked *all* rules and picked the most specific one, or used "deny
   wins if any rule denies"?
4. **NAT gateway.** Consider a public NAT gateway used for internet access. What is it for, and
   why does it sit in a public subnet while the instances using it are in a private subnet? With
   the necessary routes and traffic rules in place, give one connection the private instance can
   initiate and one unsolicited internet connection that cannot reach it through this NAT gateway.
5. **What could go wrong?** Give one real result of a database or internal service that could be
   reached from the internet because a network boundary was set up wrong. You may name a real
   incident you know of, or explain what could happen.

## Part 2 — AIR-Sec arm

The Docker lab needs no personal `.env`. Any `FLAG{…}` shown is a shared demo marker. Grading
uses your complete commands, before/after responses, explanation, and a live spot-check.

### 2a. The lab
Do the lab with the **Step-by-step** section of `README.md` ("The Deny Rule That Never Runs").
Write down:
- The whole `curl` command that demonstrated the vulnerable result from the vulnerable app (`:8113`), with the
  `source_ip` and `port` it sent.
- The vulnerable response body and HTTP status code; the shared demo marker is not identity evidence.
- The same request sent to the fixed app (`:8114`), and the response you got instead.
- The `GET /rules` output of both apps (step 3), and which rule number matched first in each
  case.

### 2b. Audit-the-AI
Below is an AI-generated summary of a Network ACL rule set for a database subnet. The AI
claims it "correctly locks the database down to internal traffic only, with a deny-all as a
safety net." Find the planted flaw and explain, in plain English, what actually happens when an
external IP tries to reach the database on port 5432.

```
Rule #10:  ALLOW  0.0.0.0/0       port 5432   (app tier can reach the DB — quick temporary rule)
Rule #20:  DENY   0.0.0.0/0       port 5432   (safety net: block everyone else from the DB port)
Rule #30:  ALLOW  10.0.2.0/24     port 5432   (the real app-tier CIDR, added properly later)
```

Hint: rule numbers are evaluated low-to-high, and evaluation **stops at the first match** —
walk through what happens to a request from an external IP, and separately what happens to a
request from `10.0.2.0/24`, rule by rule, in order. Does rule #30 ever get a chance to run for
either of them?

### 2c. EiPE (Explain-in-Plain-English)
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why does a
correct "deny everyone else" rule in your network ACL not help, if a broader rule with a lower
number already decided the outcome? Then give a teammate one sentence of advice: where should a
narrow, specific rule go, compared with a broad, catch-all one?

## Submit
Write your answers on the **Local07 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 07 (no PDF needed). AIR-Sec-arm students fill in Part 2: the 2a lab evidence
plus the 2b and 2c answers. Conventional-arm students fill in Part 1 only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
