# Worksheet 15b — Harvest Now, Decrypt Later + Hybrid KEM

> **Course:** Security & Cryptography (KOSEN69) · **{{ slot_label }} (PQC), confidentiality companion**
> **Topic:** The quantum threat to *key exchange*: harvest-now-decrypt-later, and hybrid
> (classical + ML-KEM) key encapsulation as the deployable mitigation. (Written fresh for this
> course.)
> **Signature game:** "Harvest Now, Decrypt Later" — sniff a session today, break its classical
> KEM later, decrypt it; then watch the hybrid channel resist the same attack.

> **Ethics note:** Attack only the two local containers this lab spins up
> (`vulnerable_app.py` / `fixed_app.py`, ports 8120/8121). Recording and decrypting other people's
> traffic without authorization is illegal. Keep your `FLAG_HNDL` inside this lab environment.

## Part 1 — Student Information
| Name | Student ID | Date | Group | AI tools used (if any) |
|---|---|---|---|---|

---

## Part 2 — Conventional Arm: Written Questions

Answer each in your own words (4–8 sentences). **No AI-resilience layer applies to this part —
answer it yourself.**

**Q1. What "harvest now, decrypt later" actually means.** Define the HNDL threat. Why can an
adversary who *cannot* break today's key exchange still pose a real threat to data sent today?
Give one concrete category of data for which HNDL is a genuine risk *right now*.

**Q2. Where the break is.** In this lab the message is sealed with AES-256-GCM, which is not
broken. So *what* does the attacker break to read the message, and why does that suffice? Explain
the relationship between the KEM and the AES key in one or two sentences.

**Q3. Why "just use a bigger RSA key" is the wrong fix.** A colleague says "to be quantum-safe we
should move from RSA-2048 to RSA-8192." Explain precisely why increasing the RSA key size does
**not** defend against a quantum adversary, referencing the algorithm responsible.

**Q4. What hybrid mode buys you.** The fixed channel derives its session key as
`KDF(s_classical ‖ s_ml_kem)`. State the exact security property this gives: under what condition
does the harvested traffic stay confidential, and under what condition would it fall? Why is this
a sensible thing to deploy *now*, before PQC is universally trusted?

**Q5. KEM vs. signature; ML-KEM's job.** This lab uses **ML-KEM** (from Kyber). What is a KEM
*for*, and how does that differ from what **ML-DSA** (a signature scheme) does? Which of the two
is the right tool for the confidentiality problem in this lab, and why?

**Q6. Crypto-agility.** The fixed channel had to be *built* to carry two KEMs and combine them.
What is "crypto-agility," and why is a system's ability to swap/compose key-exchange algorithms —
not any single algorithm choice — the real engineering lesson here? Give two concrete design
practices that make a protocol crypto-agile.

---

## Part 3 — AIR-Sec Arm: Hands-on Lab

**Learning goals:** *experience* harvest-now-decrypt-later by doing it, then see a hybrid KEM
defeat the identical attack. The practical twin of Part 2's Q1–Q4.
**Prerequisites:** Docker; Python with `requests` on the host (or the course toolbox) to run
`exploit.py`.

**Environment setup**
```bash
cd {{ labpath }}/hndl
docker compose up -d          # vulnerable :8120, fixed :8121
curl localhost:8120/          # confirm it's up
curl -s localhost:8120/capture   # this is the "harvested" transcript — inspect its fields
```

**Task 0 — See what a passive eavesdropper gets (15 min).** *Goal:* understand the capture.
*Steps:* read `vulnerable_app.py`'s `_make_capture` and the `/capture` route. *Deliverable:* list
each field `/capture` returns and say, for each, whether it is a **public** value, a
**ciphertext**, or a **secret** — and confirm the session key and the RSA private key are **not**
in the capture. In one sentence: if the session key isn't in the capture, how can the message
ever be decrypted?

**Task 1 — Harvest, then break the classical KEM (25 min).** *Goal:* the core attack. *Steps:*
`python exploit.py`. Read `kemlib.rsa_break` — it factors `n`, recovers `d`, and decapsulates the
secret `s` (this is the "quantum runs Shor, later" step, modelled by factoring the small modulus).
*Deliverable:* the two prime factors your run printed for the vulnerable channel, and one sentence
stating what real-world step this factoring stands in for.

**Task 2 — Decrypt the harvested session, capture the flag (20 min).** *Goal:* finish the HNDL
attack. *Steps:* from the recovered `s`, `exploit.py` re-derives the session key
(`KDF(s)`) and AES-GCM-decrypts the harvested message. *Deliverable:* your flag, and one sentence
explaining why the attacker needed **nothing from the server** after the initial capture (why this
is "decrypt *later*").

**Task 3 — Watch the hybrid channel resist the same attack (25 min).** *Goal:* prove the fix,
don't just claim it. *Steps:* `exploit.py` then targets `:8121`. Observe that it **still** factors
the classical half and recovers `s_classical` — yet decryption **fails**. Read `fixed_app.py`'s
`_make_capture` and compare it with the vulnerable one. *Deliverable:* name the **one difference**
that defeats the attack (what the fixed KDF mixes in that the attacker cannot get), and quote the
line in `exploit.py`'s `attack_fixed` where the AES-GCM `unseal` raises. One sentence: why does
recovering *only* the classical half yield the wrong key?

**Task 4 — Explain why, precisely (25 min).** Answer in your own words: (a) The AES-GCM cipher is
identical on both channels — so why is one capture readable and the other not? (b) The fix adds no
new *bulk* cipher and does not make RSA stronger; it composes a second, independent KEM. What does
that tell you about *where* a session's long-term confidentiality actually lives? (c) Real
deployments (TLS 1.3 with X25519+ML-KEM) run the classical and PQC key exchanges **together**
rather than switching outright to PQC alone. Give one reason you'd keep the classical half at all,
given ML-KEM exists. *Deliverable:* 3 short paragraphs, one per sub-question.

---

## Evidence & Integrity (required)

- **Identity proof:** your terminal evidence for Tasks 1–3 must show your `whoami` / login email /
  student ID and a timestamp.
- **Personalized flag:** ____________________
  *Flags are unique per student (via the `FLAG_HNDL` env override — see README) — submitting
  another student's flag is a violation.*
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the decryption work** on `:8120`?
  2. **Why does the hybrid KEM stop it** on `:8121`? What exactly is the attacker missing, and why
     can't they get it from the capture?

---

## 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's advice.

A teammate asked an AI assistant: *"Our service uses RSA-2048 for key exchange. How do we make it
safe against future quantum computers?"* The AI replied:

> **AI's answer:**
> "Quantum computers threaten RSA because they can factor large numbers faster. The fix is
> straightforward: **increase your RSA key size**. Move from RSA-2048 to **RSA-15360**, which NIST
> rates at the 256-bit security level — that's an enormous modulus that would take even a quantum
> computer an impractically long time to factor. For extra safety, also rotate keys more often and
> enable perfect forward secrecy. With a 15360-bit RSA key you are quantum-safe and don't need to
> change your protocol or add any new libraries."
> — end of AI answer —

1. **Find the core error.** The AI's central claim is wrong. Explain precisely why making the RSA
   modulus larger does **not** defend against a quantum adversary — reference the algorithm
   responsible and how its cost scales with key size, versus how a *classical* factoring attack
   scales. Why is "256-bit *classical* security level" irrelevant to the quantum threat?
2. **Catch the half-truths.** Two pieces of the advice are individually reasonable but do **not**
   solve the stated problem. Identify them (hint: key rotation; perfect forward secrecy) and
   explain, for each, what it *does* help with and why it does **not** address a quantum adversary
   who has **harvested** your traffic. (Tie this back to Part 2 Q1.)
3. **Write the correct answer yourself.** Give the advice the AI should have given: name the
   category of algorithm actually needed, name the specific NIST KEM, and explain why a **hybrid**
   deployment (classical + PQC) — not a drop-in RSA-size bump, and not even PQC-only — is the right
   migration path today. Two short paragraphs.

> Disclose your AI use (if any, beyond this provided artifact) in the Part 1 table. This task
> counts toward your Defense + Reflection score.

---

## 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** Explain to a non-technical manager — who knows "we encrypt
our traffic" — **why data your company sends encrypted today could still be exposed in ten years**,
and what "harvest now, decrypt later" means for them. No jargon; one short paragraph. Then state,
in one sentence, the single action that reduces this risk *now*.

**B. Prompt Problem.** Write a prompt you could give an AI assistant that would get you a
*correct* answer to "how should we migrate our TLS key exchange to be quantum-resistant?" — one
that steers it away from the "just use a bigger RSA key" trap. Then explain in 2–3 sentences **why
your prompt works**: what constraint or framing you added that forces the model toward hybrid /
ML-KEM rather than the plausible-but-wrong size-bump answer.
