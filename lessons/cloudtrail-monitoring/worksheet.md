# Worksheet — {{ slot_label }}: CloudTrail + CloudWatch + EventBridge Monitoring

This topic is **Block 2** per `course-plan.md`'s block table (blocks follow the half of term, so
the IAM topic of this same lesson is Block 2 as well). Section A = Block 2 Conventional; Section B =
Block 2 AIR-Sec (reversed from Block 1). Complete only the part assigned to you this block.

**Language:** you may answer in Thai or English. Keep AWS names (CloudTrail, CloudWatch,
EventBridge, metric filter) and terms such as aggregation key, password spray and `source_ip` in
English. Short, clear answers are enough: 2–4 sentences per question.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. **Three parts of one pipeline.** In a real AWS setup that watches for failed console logins,
   what does each of these do: **CloudTrail**, **CloudWatch** (metric filters and alarms) and
   **EventBridge**? Explain the pipeline step by step, as if to someone who has never seen it.
2. **Aggregation key.** What is an "aggregation key" in a CloudWatch metric filter that counts
   failed logins? Give two different aggregation keys you could choose for the same log data, and
   explain how the choice changes what the metric really counts.
3. **Spray or brute force?** What is the difference between a **password spray** (many different
   usernames, one or a few source IPs, only a few failed attempts per username) and a **classic
   brute force** (one username, many failed attempts, from one source)? Both produce "many failed
   logins" in the log. Why does each one need different counting logic to be detected reliably?
4. **One rule, two attackers.** A detective control alerts after 3 or more failed logins **from the
   same username**, whatever the source IP. Would it catch a password spray from one IP that tries
   20 usernames? Would it catch someone trying one stolen username from 20 different IPs
   (credential stuffing)? Explain both answers.
5. **Running is not enough.** Why is it not enough for a detective control to just "run without
   crashing" and "produce some alerts sometimes"? What makes a wrong aggregation key a
   **security** bug, not just a tuning or false-positive problem?

## Part 2 — AIR-Sec arm

### 2a. The lab
Do the lab with the **Step-by-step** section of `README.md` ("The Spray That Never Alerts").
Write down:
- The loop command you sent to the vulnerable app (`:8111`, step 3), which shows the method, URL
  and JSON body, and after how many attempts in total it had still not alerted.
- The loop command you sent to the fixed app (`:8112`, step 4), the attempt number on which the
  alert first fired, and your flag.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why does
counting failed logins per `(source_ip, username)` pair let a password-spray attacker "hide in
plain sight"? And what general rule should a defender follow, beyond this one lab, when choosing
what to group log events by before setting an alert threshold?

## Submit
Write your answers on the **Local09 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 09 (no PDF needed). AIR-Sec-arm students fill in Part 2: the 2a lab evidence
and the flag, plus the 2b answer. Conventional-arm students fill in Part 1 only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
