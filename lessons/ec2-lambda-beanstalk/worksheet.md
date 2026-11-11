# Worksheet — {{ slot_label }}: EC2 Instance Roles and SSRF

This lesson is **Block 1** per `course-plan.md`'s block table. Section A = Block 1 **AIR-Sec**;
Section B = Block 1 **Conventional**. Complete only the part assigned to your section this block.

**Language:** you may answer in Thai or English. Keep AWS names (EC2, IAM, IMDS) in
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
5. **Temporary credentials and least privilege.** Why must temporary EC2 instance-role
   credentials still be protected? Explain how limiting the role's permissions reduces the
   impact if credentials are exposed through the URL-fetch feature.
6. **Verifying a defense.** Describe two checks for the fixed URL-fetch feature: one that
   confirms an intended request still works, and one that confirms a metadata-shaped request
   is rejected. State the expected result and explain why both checks are needed. Use the
   supplied local scenario; do not probe real metadata endpoints or other systems.

## Part 2 — AIR-Sec arm

The Docker lab needs no personal `.env`. Any `FLAG{…}` shown is a shared demo marker. Grading
uses your complete commands, before/after responses, explanation, and a live spot-check.

### 2a. The lab (request and response evidence)
Follow **Step-by-step** in `README.md` and copy its commands; each step shows what you should
see. Write down:
- The request body you sent to the vulnerable app (`:8104`) that demonstrated the vulnerable result.
- The vulnerable response body and HTTP status code; the shared demo marker is not identity evidence.
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
Write your answers on the **Local02 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 02 (no PDF needed). AIR-Sec-arm students fill in Part 2: the 2a
request/response pair, plus the 2b answer. The viva (2c) is a live spot-check during lab time or
office hours, not a written answer. Conventional-arm students fill in Part 1 only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
