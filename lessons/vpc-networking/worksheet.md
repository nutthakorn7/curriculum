# Worksheet — {{ slot_label }}: VPC Networking

Section is assigned Block 1 = AIR-Sec or Block 2 = Conventional per `course-plan.md`'s block
table — complete only the part assigned to you this block.

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. What is the difference between a **security group** and a **network ACL** in a VPC? Address
   both: (a) stateful vs. stateless, and (b) what "stateful" and "stateless" actually mean for a
   response packet, using a concrete example (e.g., an inbound rule that allows traffic to a
   web server on port 443).
2. Security groups only support **allow** rules; network ACLs support both **allow** and
   **deny**. What does this difference in expressive power mean for how you'd use each one? Why
   might you want an explicit deny at the subnet level even when your security groups are
   already "allow-only, default-deny everything else"?
3. Explain, in your own words, why AWS evaluates network ACL rules **in ascending rule-number
   order and stops at the first match** — what would go wrong (or what would simply be
   different) if instead it evaluated *all* rules and picked the most specific one, or picked
   "deny wins if any rule denies"?
4. What is the purpose of a **NAT gateway**, and why does it live in a **public** subnet even
   though the instances that use it are in a **private** subnet? Explain what "outbound only"
   means here in plain terms — what request would succeed and what request would fail.
5. Describe one real-world consequence of a public-facing database or internal service that was
   reachable from the internet because of a misconfigured network boundary (you may reference a
   real incident you're aware of, or reason from first principles).

## Part 2 — AIR-Sec arm

### 2a. The lab
Run the "The Deny Rule That Never Runs" exercise (`README.md`). Record:
- The exact request (`source_ip`, `port`) that got you the flag on the vulnerable app.
- The captured flag.
- The exact same request against the fixed app, and the response you got instead.
- The output of `GET /rules` on both apps — specifically, which rule number matched first in
  each case.

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
In 3–4 sentences a non-technical stakeholder could understand: why doesn't it help to have a
correct "deny everyone else" rule in your network ACL if a broader rule with a lower number
already decided the outcome? What's the one-sentence rule of thumb you'd give a teammate about
where to place a narrow, specific rule relative to a broad, catch-all one?

## Submit
Flag + Part 2a request/response pair + Part 2b/2c answers → Classroom. Conventional-arm students
submit Part 1 only.
