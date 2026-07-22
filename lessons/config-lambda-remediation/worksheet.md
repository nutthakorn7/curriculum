# Worksheet — {{ slot_label }}: AWS Config + Lambda Auto-Remediation

Section is assigned Block 1 = AIR-Sec or Block 2 = Conventional per `course-plan.md`'s block
table — complete only the part assigned to you this block. ({{ slot_label }} falls in Block 2.)

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. In your own words, what does an **AWS Config rule** do? Describe the difference between a
   resource being evaluated as **COMPLIANT** and **NON_COMPLIANT**.
2. Explain, conceptually, how a **Lambda-based auto-remediation** action fits into this picture —
   what triggers it, and what does it typically do once triggered (you do not need AWS API call
   names, just the general flow: detect → decide → act).
3. This lab's remediation function is supposed to implement an **allowlist**: keep only inbound
   rules on approved ports (80, 443), revoke everything else. Explain the difference between
   **allowlist** thinking ("deny by default, permit specific things") and **denylist** thinking
   ("permit by default, deny specific things") for security group rules. Which is generally
   considered safer, and why?
4. The vulnerable version of this lab's remediation function has its condition inverted: it keeps
   the *disallowed* rules and revokes the *allowed* ones. Explain why this kind of bug is
   especially dangerous compared to a remediation function that simply crashes or does nothing —
   consider what a monitoring dashboard or on-call engineer would see in each case.
5. Describe one real-world consequence of an inbound rule for SSH (port 22) or RDP (port 3389)
   left open to `0.0.0.0/0` on a production security group (you may reference a real incident you
   are aware of, or reason from first principles about what an attacker would do next).

## Part 2 — AIR-Sec arm

### 2a. The lab
Run the "The Inverted Allowlist" exercise (`README.md`). Record:
- The exact request sequence (`/reset`, `/remediate`, `/security-group`) you ran against the
  vulnerable app.
- The captured flag and the security-group state it came from (which rules survived, which were
  removed).
- The same sequence against the fixed app, and the resulting security-group state instead.

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
In 3–4 sentences a non-technical stakeholder could understand: why did a remediation function
that runs without any errors, and reports "success," still leave the network exposed — and why
is that scarier than the automation simply failing loudly?

## Submit
Flag + Part 2a request/response evidence + Part 2b/2c answers → Classroom. Conventional-arm
students submit Part 1 only.
