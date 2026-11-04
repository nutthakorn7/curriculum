# Worksheet — {{ slot_label }}: AWS Config + Lambda Auto-Remediation

This lesson is **Block 2** per `course-plan.md`'s block table. Section A = Block 2 **Conventional**;
Section B = Block 2 **AIR-Sec** (reversed from Block 1). Complete only the part assigned to your
section this block. ({{ slot_label }} falls in Block 2.)

**Language:** you may answer in Thai or English. Keep AWS names (AWS Config, Lambda, security
group, COMPLIANT / NON_COMPLIANT) in English. Short, clear answers are enough: 2–4 sentences per
question.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. **What a Config rule does.** In your own words, what does an **AWS Config rule** do? What is the
   difference between a resource being **COMPLIANT** and **NON_COMPLIANT**?
2. **Where Lambda fits.** How does a **Lambda-based auto-remediation** fit into this picture? What
   starts it, and what does it usually do next? You don't need AWS API names, just the flow:
   detect → decide → act.
3. **Allowlist or denylist?** This lab's remediation function should use an **allowlist**: keep
   only inbound rules on approved ports (80, 443) and remove everything else. What is the
   difference between **allowlist** thinking ("deny by default, allow specific things") and
   **denylist** thinking ("allow by default, deny specific things") for security group rules?
   Which is usually safer, and why?
4. **Worse than crashing.** In the vulnerable version the condition is inverted: it keeps the
   *disallowed* rules and removes the *allowed* ones. Why is this kind of bug more dangerous than a
   remediation function that crashes or does nothing? Think about what a monitoring dashboard or
   an on-call engineer would see in each case.
5. **What could go wrong?** Give one real result of an inbound rule for SSH (port 22) or RDP (port
   3389) open to `0.0.0.0/0` on a production security group. You may name a real incident you know
   of, or explain what an attacker would do next.

## Part 2 — AIR-Sec arm

### 2a. The lab
Do the lab with the **Step-by-step** section of `README.md` ("The Inverted Allowlist"). Write down:
- The request sequence you ran against the vulnerable app (`:8115`, steps 3–5: `/reset`,
  `/remediate`, `/security-group`).
- Your flag, and the security-group state it came from: which rules survived and which were
  removed.
- The same sequence on the fixed app (`:8116`, step 6), and the security-group state you got
  instead.

### 2b. Audit-the-AI
Below is an AI-generated description of a Lambda auto-remediation function that the AI claims is
"a correct implementation of allowlist-based security group remediation." Find the planted flaw
and explain, in plain English, what the function actually does when it runs.

```python
def remediate(security_group_rules, allowed_ports):
    """Enforce the allowlist: only ports in `allowed_ports` should remain
    open after this function runs."""
    remaining_rules = []
    for rule in security_group_rules:
        if rule["port"] in allowed_ports:
            # keep this rule off the security group — it's on the allowlist
            # so we don't need to worry about it
            continue
        remaining_rules.append(rule)
    return remaining_rules
```

Hint: trace through the function by hand with `allowed_ports = {80, 443}` and a rule set
containing ports 80, 443, and 22. Which ports end up in `remaining_rules`? Is that the allowlist
being *enforced*, or something else?

### 2c. EiPE (Explain-in-Plain-English)
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why did a
remediation function that runs without any errors, and reports "success", still leave the
network exposed? And why is that scarier than the automation simply failing loudly?

## Submit
Write your answers on the **Local10 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 10 (no PDF needed). AIR-Sec-arm students fill in Part 2: the 2a lab evidence
and the flag, plus the 2b and 2c answers. Conventional-arm students fill in Part 1 only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
