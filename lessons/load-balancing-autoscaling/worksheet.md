# Worksheet — {{ slot_label }}: Load Balancing & Auto-Scaling Under Load

This lesson is **Block 1** per `course-plan.md`'s block table. Section A = Block 1 **AIR-Sec**;
Section B = Block 1 **Conventional**. Complete only the part assigned to your section this block.

**Language:** you may answer in Thai or English. Keep AWS names (load balancer, target group, Auto
Scaling Group) and the endpoint names (`/generate-load`, `X-Api-Key`) in English. Short, clear
answers are enough: 2–4 sentences per question.

## Part 1 — Conventional arm (short answers)

Answer in your own words (no AI-resilience layer, no flag — graded on the writing itself):

1. **Three parts that work together.** What does each of these do: a **load balancer**, a
   **target group** and an **Auto Scaling Group**? How do they work together? If the load
   balancer sent traffic straight to a fixed list of servers, with no target group in between,
   what would you lose?
2. **Minimum and maximum.** An Auto Scaling Group has a **minimum** and a **maximum** number of
   instances. What is each one for? Give one example of a problem that each setting prevents.
3. **An excessively high maximum.** A team raises its Auto Scaling Group maximum far above the
   expected demand, saying "so we never run out of capacity during a traffic spike." What cost
   risk does this create if unwanted traffic triggers scaling? How is it different from running
   out of capacity? A maximum size is still configured; this is not an unlimited-scaling setting.
4. **Denial of Wallet.** What is a "Denial of Wallet" attack? How is it different from a normal
   denial-of-service attack, which tries to make a service stop working?
5. **Two controls.** This lesson's endpoint adds servers for *any* request, without checking
   who is calling or how often. Name two different controls that would each reduce this risk.
   Why is using only one of them weaker than using both?

## Part 2 — AIR-Sec arm

The Docker lab needs no personal `.env`. Any `FLAG{…}` shown is a shared demo marker. Grading
uses your complete commands, before/after responses, explanation, and a live spot-check.

### 2a. The lab
Do the lab with the **Step-by-step** section of `README.md`. Write down:
- The loop command you sent to the vulnerable app (`:8109`, step 4), and the call number at
  which `current_instances` reached 6.
- The vulnerable response body and HTTP status code; the shared demo marker is not identity evidence.
- The same request sent to the fixed app with no key (`:8110`, step 6): the HTTP code and the
  error you got.
- The fixed app with the valid API key (step 7): how many calls were accepted before the first
  `429`, and the message the `429` gave.

### 2b. Explain-in-Plain-English (EiPE)
A teammate says: "We don't need rate limiting on `/generate-load` — I already added an API key,
so only people we trust can call it." In 3–4 short sentences that someone without IT knowledge (a
parent, say) could follow: why does the API key alone not fully fix the problem? And why is "just
add more instances to handle whatever load comes" not a security fix either?

### 2c. Short-answer
An attacker gets one valid API key (for example, someone pushed it to a public GitHub repo by
mistake). With this lesson's fixed app, what is the largest number of `/generate-load` calls that
leaked key can make before it is cut off? Why does that number limit the damage ("blast
radius") one leaked key can do?

## Submit
Write your answers on the **Local05 Answer Sheet** that Classroom copies for you, then click
**Turn in** on Local 05 (no PDF needed). AIR-Sec-arm students fill in Part 2: the 2a lab
evidence, plus the 2b and 2c answers. Conventional-arm students fill in Part 1
only.

- **Due:** before the start of the next week's class (the due date on the Classroom assignment).
- **Late:** −10% of the score you earned for every 24 hours after the due time, down to 0 after
  10 days. Late work is marked only after a short viva. Full rules in SUBMISSION.md.
