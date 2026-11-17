---
marp: true
theme: default
paginate: true
header: "Software Security 2 · 02005094 · Week 9 · Midterm practical"
---

# Week 9 — Midterm individual practical
## Software Security 2 (02005094)
Individual work · revise Weeks 1–4 and 6

<!-- Instructor: use the current sitting pack and matching key, with dependencies checked beforehand. No hosted instance or personal flag is issued unless announced. -->

---

## Format and time

- **150 minutes in total:** 10 minutes briefing + 130 minutes on the tasks + 10 minutes to check your upload
- **Four stations × 25 points = 100 points**
- Each station is marked in two halves: **Basic 50 + Technical 50** in total
- The practical counts as **12%** of your course grade
- Leaderboards, "first blood", prizes and House XP give no course marks

---

## The four stations — 130 minutes

- **A · 35 minutes · 25 points** — Threat model and scanner triage (Weeks 1–2)
- **B · 35 minutes · 25 points** — Move old password records to Argon2id at login (Week 3)
- **C · 30 minutes · 25 points** — Parameterized SQL and a safe IPv4 ping (Week 4)
- **D · 30 minutes · 25 points** — Check the login token and who owns the order (Week 6)

Use only the starter files in the exam pack your instructor hands out.

---

## What earns marks

- Hand in the file you changed (or a diff), the exact command and what you saw
- Include one **positive test** (normal use still works) and one **negative test** (the attack is refused)
- Explain why the problem happened, why your fix works, and one limit of your test
- A flag on its own does not earn full marks

Each station: **Basic 12.5** (finding, explanation, reading your results) + **Technical 12.5** (your fix, your tests, repeatable results). Basic 50 + Technical 50 → 6 + 6 course marks.

---

## On the day

- Work only on the exam pack, on your own machine; never attack another system
- Use a hosted server only if your instructor gives you one
- Stop task work after 130 minutes; use the final 10 minutes to check your upload opens
- Individual work: one evidence file per student
- Date, room and permitted aids: see the official exam notice

[Read the full practical brief](../labs/week09-midterm-practical/ctf.md)
