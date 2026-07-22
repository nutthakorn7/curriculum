# Worksheet — {{ slot_label }}: Load Balancing & Auto-Scaling Under Load

Section is assigned Block 1 = AIR-Sec or Block 2 = Conventional per `course-plan.md`'s block
table — complete only the part assigned to you this block.

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. In your own words, describe how a **load balancer**, a **target group**, and an
   **Auto Scaling Group** relate to each other. If a load balancer routes traffic directly to
   instances with no target group in between, what capability do you lose?
2. What is the purpose of an Auto Scaling Group's **minimum** capacity setting? What is the
   purpose of its **maximum** capacity setting? Give one concrete failure scenario each setting
   protects against.
3. A team removes the maximum-capacity cap on their Auto Scaling Group "to make sure we never
   run out of capacity during a traffic spike." What new risk does this introduce, and how is
   that risk different from the original problem (running out of capacity) they were trying to
   solve?
4. Describe, in your own words, what a "Denial of Wallet" (economic denial-of-service) attack
   is, and how it differs from a traditional denial-of-service attack that aims to make a
   service unavailable.
5. This lesson's lab endpoint scales up in response to *any* incoming request, with no check on
   who is calling or how often. Name two different, complementary controls that could each
   independently reduce this endpoint's exposure, and explain why relying on only one of them is
   weaker than using both together.

## Part 2 — AIR-Sec arm

### 2a. The lab
Run the "Generate Load" exercise (`README.md`). Record:
- The exact request pattern (endpoint, method, headers-or-lack-thereof) you used against the
  vulnerable app, and roughly how many calls it took to reach `current_instances = 6`.
- The captured flag.
- The exact request you tried against the fixed app, and the response you got instead (including
  what happened when you tried with a *valid* API key repeatedly).

### 2b. Explain-in-Plain-English (EiPE)
A teammate says: "We don't need rate limiting on `/generate-load` — I already added an API key
requirement, so it's authenticated now, and only people we trust have the key." In 3-4 sentences
a non-technical stakeholder could understand, explain why authentication alone does not fully
close this vulnerability, and why "just add more instances to handle whatever load shows up"
is not, by itself, a security fix either.

### 2c. Short-answer
Suppose an attacker obtains one valid API key (e.g., it was accidentally committed to a public
repository). Using this lesson's fixed app as the reference design, what is the worst-case
number of scaling-relevant calls that leaked key can make before being cut off, and why does
that number matter for limiting the "blast radius" of a single leaked credential?

## Submit
Part 1 (Conventional) or Part 2a/2b/2c (AIR-Sec) + flag (AIR-Sec only) → Classroom.
