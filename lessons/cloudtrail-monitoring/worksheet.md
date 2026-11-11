# Worksheet — {{ slot_label }}: CloudTrail + CloudWatch + EventBridge Monitoring

This topic is **Block 2** per `course-plan.md`'s block table (blocks follow the half of term, so
the IAM topic of this same lesson is Block 2 as well). Section A = Block 2 Conventional; Section B =
Block 2 AIR-Sec (reversed from Block 1). Complete only the part assigned to you this block.

**Language:** you may answer in Thai or English. Keep AWS names (CloudTrail, CloudWatch,
EventBridge, metric filter) and terms such as aggregation key, password spray and `source_ip` in
English. Short, clear answers are enough: 2–4 sentences per question.

**Weekly scope:** Week 17 class uses AWS Academy Module 6 and Lab 6.1. The lab's
security-group monitoring example is different from this worksheet's failed-login case.
After the AWS lab, read the **Week 17 concept bridge** in `README.md` and complete only
your room's Part outside class. C5R2 answers Part 1 without Docker; C5R1 runs the local
simulation for Part 2 on their own computer. Submit the Local09 Answer Sheet by the due date
below. The AWS Course Assessment and Module 8 bridge work are separate LMS tasks.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. **Detection and event paths.** In a real AWS setup that watches for failed console logins,
   explain the roles of CloudTrail, CloudWatch Logs metric filters and alarms, and EventBridge.
   Describe a log-to-metric alarm path and an event-routing path. Do all three services have to
   form one serial pipeline?
2. **Aggregation key.** What is an "aggregation key" in a CloudWatch metric filter that counts
   failed logins? Give two different aggregation keys you could choose for the same log data, and
   explain how the choice changes what the metric really counts.
3. **Spray or brute force?** What is the difference between a **password spray** (many different
   usernames, one or a few source IPs, only a few failed attempts per username) and a **classic
   brute force** (one username, many failed attempts, from one source)? Both produce "many failed
   logins" in the log. Why does each one need different counting logic to be detected reliably?
4. **One rule, two attackers.** Assume a detective control alerts after 3 or more failed logins
   for the same username within its evaluation period, regardless of source IP. Would one failed
   attempt for each of 20 different usernames from one IP trigger it? Would 20 failed attempts
   for one username from 20 different IPs trigger it? Explain both answers and why failed-login
   counts alone do not establish whether credentials were stolen.
5. **Running is not enough.** Why is it not enough for a detective control to just "run without
   crashing" and "produce some alerts sometimes"? What makes a wrong aggregation key a
   **security** bug, not just a tuning or false-positive problem?

## Part 2 — AIR-Sec arm

The Docker lab needs no personal `.env`. Any `FLAG{…}` shown is a shared demo marker. Grading
uses your complete commands, before/after responses, explanation, and a live spot-check.

### 2a. The lab
Do the lab with the **Step-by-step** section of `README.md` ("The Spray That Never Alerts").
Write down:
- The loop command you sent to the vulnerable app (`:8111`, step 3), which shows the method, URL
  and JSON body, and after how many attempts in total it had still not alerted.
- The loop command you sent to the fixed app (`:8112`, step 4), the attempt number on which the
  alert first fired, and the complete alert response.

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why does
counting failed logins per `(source_ip, username)` pair let a password-spray attacker "hide in
plain sight"? And what general rule should a defender follow, beyond this one lab, when choosing
what to group log events by before setting an alert threshold?

## Submit
Write your answers on the **Local09 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 09 (no PDF needed). AIR-Sec-arm students fill in Part 2: the 2a lab evidence
plus the 2b answer. Conventional-arm students fill in Part 1 only.

- **Due:** Mon 1 Mar 2027, 23:59 (Asia/Bangkok), as on the Classroom assignment.
- **Late:** −10% of the score you earned for every 24 hours (or part) after the due time. Late
  submissions close Mon 8 Mar 2027, 23:59 (Asia/Bangkok). Late work is marked only after a short
  viva, arranged outside class if needed. Full rules in SUBMISSION.md.
