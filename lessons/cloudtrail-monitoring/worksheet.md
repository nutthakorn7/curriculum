# Worksheet — {{ slot_label }}: CloudTrail + CloudWatch + EventBridge Monitoring

This topic is **Block 2** per `course-plan.md`'s block table (the IAM topic earlier in this
same lesson is Block 1; this monitoring topic is Block 2 — the two topics of Lesson 7
deliberately split across blocks). Section A = Block 2 Conventional; Section B = Block 2
AIR-Sec (reversed from Block 1). Complete only the part assigned to you this block.

## Part 1 — Conventional arm (essay)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. In a real AWS monitoring pipeline for failed console logins, what distinct role does each of
   the following play: **CloudTrail**, **CloudWatch** (metric filters/alarms), and
   **EventBridge**? Answer as if explaining the pipeline stage-by-stage to someone who has never
   seen it.
2. What is an "aggregation key" in the context of a CloudWatch metric filter that counts failed
   login events? Give an example of two different aggregation keys you could choose for the
   same raw log data, and explain how the choice changes what the resulting metric actually
   counts.
3. Describe the difference between a **password-spray** attack pattern (many different
   usernames, one or a few source IPs, only a handful of failed attempts per username) and a
   **classic brute-force** attack pattern (one username, many failed attempts, from one source).
   Why do both patterns produce "many failed logins" in the raw log, yet require different
   aggregation logic to detect reliably?
4. Suppose a detective control is built to alert after 3+ failed logins **from the same
   username**, regardless of source IP. Would that control catch a password-spray attack from a
   single IP rotating through 20 usernames? Would it catch someone credential-stuffing one
   compromised username from 20 different IPs? Explain both answers.
5. Why is it not enough for a detective control to simply "run without crashing" and "produce
   some alerts sometimes"? What makes an aggregation-key choice a **security** bug rather than
   just a tuning/false-positive-rate issue?

## Part 2 — AIR-Sec arm

### 2a. The lab
Run the "The Spray That Never Alerts" exercise (`README.md`). Record:
- The exact request sequence (method, URL, JSON body) you sent to the vulnerable app, and
  confirm — after how many total attempts — that it still had not alerted.
- The exact request sequence you sent to the fixed app, the attempt number the alert fired on,
  and the captured flag.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 sentences a non-technical stakeholder could understand: why does tracking failed logins
per `(source_ip, username)` pair let a password-spray attacker "hide in plain sight," and what
is the general principle a defender should apply — beyond this one lab — when choosing what to
group log events by before setting an alert threshold?

## Submit
Flag + Part 2a request/response pair + Part 2b answer → Classroom. Conventional-arm students
submit Part 1 only.
