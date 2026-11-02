# Worksheet — {{ slot_label }}: EC2 Instance Roles, Lambda Basics, Elastic Beanstalk

This lesson is **Block 1** per `course-plan.md`'s block table. Section A = Block 1 **AIR-Sec**;
Section B = Block 1 **Conventional**. Complete only the part assigned to your section this block.

**Language:** you may answer in Thai or English. Keep AWS names (EC2, IAM, IMDS, Lambda) in
English. Short, clear answers are enough: 2–4 sentences per question.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. **Access key or instance role?** An app on EC2 needs to read files from S3. Option A: paste an
   IAM user's access key into the app's code. Option B: attach an IAM instance role to the EC2
   instance. Which option is safer, and why?
2. **What is IMDS?** What does the Instance Metadata Service give to programs running on an EC2
   instance? Why can only programs on that same instance reach it, not anyone on the internet?
3. **A "fetch this URL" feature.** A web app on EC2 has a "preview this link" feature: you type a
   URL and the server downloads that page for you. How could an attacker use this feature to get
   the instance role's credentials, without reaching the metadata service themselves? What is
   this kind of attack called?
4. **Two defenses.** Name two ways to stop the attack in Q3. Blocking only the exact text
   `169.254.169.254` does not count as one of them.
5. **EC2 or Lambda?** What is one big difference between running code on an EC2 instance you
   manage yourself and running the same code as a Lambda function? Name one security concern
   that changes (for better or worse) when you move from EC2 to Lambda.
6. **One bug, many servers.** Elastic Beanstalk can run your app on many EC2 instances behind a
   load balancer (an auto-scaling group). If the app has the instance-role problem from this
   lesson, why is it a bigger problem on many instances than on one?

## Part 2 — AIR-Sec arm

### 2a. The lab (flag capture)
Follow **Step-by-step** in `README.md` and copy its commands; each step shows what you should
see. Write down:
- The request body you sent to the vulnerable app (`:8104`) that returned your flag.
- Your flag.
- The same request sent to the fixed app (`:8117`), and the response you got (the HTTP code and
  the `reason`).

### 2b. EiPE (Explain-in-Plain-English)
In 3–4 short sentences that someone without IT knowledge (a parent, say) could follow: why does a
"fetch this URL for me" feature on a cloud server give an attacker a way to steal that server's
cloud credentials? And why is blocking only the address `169.254.169.254` not enough? (Hint: the
server can also reach itself by other names, such as `localhost`.)

### 2c. Viva spot-check
Be ready to answer out loud, without notes, in under 2 minutes:
- The metadata route did exactly what it is supposed to do for the server. So where is the real
  bug?
- If you could change one line in `vulnerable_app.py` to fix it, what would you add? Is that
  check an allowlist, a blocklist or a login check?
- Why would adding a login to `/fetch-preview` (with no check on the URL) not fix the problem?

## Submit
Flag + Part 2a request/response pair + Part 2b answer → Classroom. Viva (2c) is a live spot-check
during lab time or office hours, not a written submission. Conventional-arm students submit
Part 1 only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
