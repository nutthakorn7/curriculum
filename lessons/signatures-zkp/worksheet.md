# Worksheet 11 — Digital Signatures: the "twin" signature that pays the bank twice

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Kind:** Docker lab, step by step. No programming and no maths (the Schnorr/ZKP part is read as an explanation).

> **Ethics note:** Only work on the 2 pretend banks on your own computer that this lab starts (ports 8102 and 8103). Sending forged or repeated signatures to a real payment system, trading board or blockchain that is not yours, without permission, is illegal. Keep the flag inside this lab only.

## Read this first

**What you will do today:** An ECDSA digital signature is two numbers `(r, s)`. Strangely, if `(r, s)` is valid, then there is a **"twin signature" `(r, n−s)`** that is valid in the same way, for the same message and the same key. A pretend bank uses the **hash of the signature** as the transaction number, so it sees the twin as a "new transaction", even though the owner allowed the withdrawal only **once**. You will withdraw again with the twin signature, and then see how the other bank, which accepts only one form of signature, stops it. Remember this: **a valid signature does not always mean the same transaction.**

**Every step is written the same way:**

| Heading | Meaning |
|---|---|
| **What to do** | Says what this step does |
| **Type** | Copy the whole line, paste it into the Terminal, and press Enter |
| **You should see** | The screen should look roughly like this (the signature numbers will be different from the example, and that is normal) |
| **Means** | What the result means |
| **Write in the answer sheet** | What to copy or write in your answer sheet |

**Marks**

- Everyone does **Part A (60 marks)**, which is the same for both forms.
- Then do **only your own form (40 marks)**. Look at the last digit of your student ID: **odd = Conventional (Part 2)**, **even = AIR-Sec (Parts 3–4)** (0 counts as even). Write your form in the Group box.
- You may answer in English or Thai. Short and clear is enough.
- **Answer sheet:** in Classroom → Week 11, open the file for your form (`Wk11_Answer_Sheet_Conventional_odd_ID` or `Wk11_Answer_Sheet_AIR-Sec_even_ID`), choose Open with → Google Docs, type in the grey boxes, then choose File → Download → PDF.
- Submit one file named with your student ID, for example `Wk11_66990000.pdf` (do not type the `<` `>` signs), at `learn.zcr.ai/submit` with your Week 11 submission code from your KMITL email, by **Sunday 17 Jan 2027, 23:59**.
- Items marked *optional* have no marks. You can skip them.

| Part A | Marks | Steps to write in the answer sheet |
|---|---:|---|
| A1 — A signature and its twin | 20 | Steps 2, 3 |
| A2 — Withdrawing twice at the vulnerable bank | 20 | Steps 5, 6 |
| A3 — The fixed bank refuses the twin signature | 20 | Steps 7, 8, 9, 10 |

**Words you need to know**

| Word | Simple meaning |
|---|---|
| Terminal | A window where you type commands |
| Docker / container | A program that starts a small "pretend computer" on your computer. If you break it, delete it and start again |
| digital signature | A number that proves that this message was signed with the owner's private key. Anyone who has the public key can check it |
| ECDSA | One way to sign. The signature is two numbers `(r, s)` |
| twin signature | `(r, n−s)`: a signature that is valid in the same way as `(r, s)` for the same message and key, but is a different set of numbers |
| low-S / high-S | `s` is in the lower half (low) or the upper half (high) of the range of numbers. In a pair of twins, only one of them is low-S |
| txid | The transaction number, which the bank uses to stop a transaction being processed twice |
| replay | Sending the very same transaction again, character for character |
| malleability | The signature can be changed into another form that is still valid, without needing a key |
| flag | A prize message in the form `FLAG{...}`, which is proof that you succeeded |

**Questions people often ask**

- *Do I need to be good at maths?* No. The script works out the twin signature for you.
- *Do I need to write programs?* No. Copy the commands and paste them (except for the Prompt task of the AIR-Sec form).
- *If I make a mistake, will my computer break?* No. Everything is inside containers. If you get confused, type `docker compose down` and start again from Prep step 5 (the banks' withdrawn totals go back to 0).
- *Can I skip understanding every number on the screen?* Yes. Only look at the lines the worksheet tells you to.
- *My signature numbers are not the same as my friend's. Is that wrong?* No. The signatures are random every time. But the status codes (200 / 403 / 409), the totals and the flag must be the same, and you must always copy from your own computer.
- *How do I paste a command into the Terminal?* Copy the command from the worksheet, then Windows: press Ctrl+V or right-click · Mac: press Cmd+V, then press Enter.
- *How do I copy results from the Terminal?* Select the text with the mouse first, then Windows: press Ctrl+Shift+C · Mac: press Cmd+C. Or take a screenshot.

**If you see a message like this**

| Message on screen | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` or `error during connect` | Docker is not open | Open Docker Desktop and wait until it says Engine running |
| `no configuration file provided: not found` | The Terminal is not in the lab folder | Repeat Prep step 4 |
| `service "vulnerable" is not running` | The lab is not started | Do Prep steps 5 and 6 |
| `Cannot reach the ... bank` | The lab has not finished starting | Wait a moment, then repeat Prep step 6 |
| `No signature saved yet` | You have not typed the `sign` command yet | Type the `sign` command of that bank first |
| `bad signature` | The bank was started again, but the saved signature belongs to the old key | Type the `sign` command again |
| `can't open file '/lab/bank.py'` | The ZIP you downloaded is old and has no `bank.py` | Download a new ZIP as in Prep step 2 |

If you still cannot do it, ask a friend or your instructor.

---

## Before you start: set up your computer (at home, once)

If you already did Weeks 2–6 or 10, you have Docker and the ZIP file. Start at **Prep step 4**. But the ZIP must be a recent one that has the file `bank.py` in the folder `week11-signatures-zkp`. If you cannot find it, download the ZIP again as in Prep step 2.

**If you turned your computer off and came back:** repeat Prep steps 1, 4, 5 and 6.

#### Prep step 1 — Open Docker Desktop

**What to do:** If you do not have it yet, install it from <https://www.docker.com/products/docker-desktop/> and leave the program open.

**You should see:** the Docker Desktop window says **Engine running**.

#### Prep step 2 — Download the lab files

**What to do:** Open <https://github.com/nutthakorn7/security-cryptography>, click the green **Code** button, and choose **Download ZIP**.

You do not need a GitHub account and you do not need to fork.

#### Prep step 3 — Unzip the ZIP file

**What to do:** Windows: right-click the ZIP file and choose **Extract All** · Mac: double-click the ZIP file. Put it somewhere easy to find, such as the Desktop.

**You should see:** a folder called `security-cryptography-master`. Some computers make a folder with the same name inside it; open it until you can see the `labs` folder.

#### Prep step 4 — Open a Terminal inside the lab folder

**What to do:** Open the `labs` folder inside `security-cryptography-master`, then open `week11-signatures-zkp`.

- **Windows:** open the `week11-signatures-zkp` folder in File Explorer, right-click an empty spot, and choose **Open in Terminal** (if you do not see it, hold Shift, right-click, and choose **Open PowerShell window here**)
- **Mac:** open the Terminal app, type `cd` and one space, drag the `week11-signatures-zkp` folder into the window, then press Enter

Check that you are in the right place with this command:

```bash
ls
```

**You should see:** `docker-compose.yml` and `bank.py` in the list.

#### Prep step 5 — Start the lab

**Type:**

```bash
docker compose up -d
```

**You should see:** two lines ending in `Started` (if the lab was already running you may see `Running`). **You need the internet every time you start this lab**, because the containers install packages each time they start. The first time it may take several minutes. Do not close the window while you wait.

#### Prep step 6 — Check that the lab is ready

**Type** (Mac):

```bash
docker compose logs | grep "Running on"
```

**Type** (Windows):

```powershell
docker compose logs | findstr /C:"Running on"
```

**You should see:** find these two lines. You must see **both of them**

```
vulnerable-1  |  * Running on http://127.0.0.1:8102
fixed-1       |  * Running on http://127.0.0.1:8103
```

If you do not see both, wait a moment and type the command again. If it still fails after 2 minutes, type `docker compose ps -a`, take a screenshot, and send it to your instructor.

---

## Part A — The lab (both forms, 60 points)

There are two pretend banks. They allow one withdrawal of 100, use the signature of the same message, and differ only in how they stop repeated transactions. Do all the steps with a lab that you start once, without a break (do not start it again in the middle, because the signatures and the withdrawn totals would be reset):

| Bank | Port | Stops repeats with | Twin signature `(r, n−s)` |
|---|---|---|---|
| `vuln` (vulnerable_app.py) | `:8102` | the hash of the signature | **accepted**: pays again |
| `fixed` (fixed_app.py) | `:8103` | the hash of the signature, and **refuses high-S signatures** | **refused** (403) |

> **If you really cannot use Docker:** tell your instructor, then open **<https://learn.zcr.ai/sim/ecdsa-malleability>** (a simulator, not a real bank), press the buttons on that page, and take a screenshot of the result instead of Steps 5 and 7. For Steps 2 and 9, copy the examples in the worksheet and write "from the worksheet example" next to them. You can answer the other steps by reading the worksheet.

### A1 — A signature and its twin (20 points)

#### Step 1 — Read: what is a twin signature?

**What to do:** Just read. You do not need to type anything.

The account owner signs the message `withdraw 100 to attacker` once. The signature `(r, s)` is checked by the bank and is valid. In the maths of ECDSA, the numbers `(r, n−s)` (take `s` away from the constant `n`) **also pass the check**, without needing any key. This is called the **twin signature**. It is a different set of numbers, but it confirms the same message from the same person. A bank that uses the hash of the signature as the transaction number (the txid) sees these two signatures as two different transactions.

#### Step 2 — Ask for a signature and look at its twin

**What to do:** Let the script ask the vulnerable bank for a signature and work out the twin signature for you (you do not calculate anything).

**Type:**

```bash
docker compose exec vulnerable python bank.py vuln sign
```

**You should see:** four lines. Your numbers, and the words low-S / high-S, may be different from the example

```
bank: vuln (port 8102)   message: withdraw 100 to attacker
signature (r, s)   : s = 7998957137... (77 digits)   high-S
twin (r, n-s)      : n-s = 3580251786... (77 digits)   low-S
txid of (r, s) = 417a2e19   txid of the twin = e66a7f5b   (different)
```

**Means:** You got the signature `(r, s)` and the twin signature `(r, n−s)`. The transaction numbers (txid) of the two are **different**, and only **one of** the two is low-S.

**✍️ Write in the answer sheet (Step 2):** copy the last three lines (`signature`, `twin`, `txid`) from your own screen.

#### Step 3 — Summarise in your own words

**What to do:** Fill in the blanks.

> The txid of the signature and the txid of the twin are ________. (Choose: `the same` / `different`) Of the two signatures, ________ is low-S. (Choose a number: `1` / `2`)

**✍️ Write in the answer sheet (Step 3):** write the full sentence.

### A2 — Withdrawing twice at the vulnerable bank (20 points)

#### Step 4 — Read: how does the bank stop repeats?

**What to do:** Just read. You do not need to type anything.

The vulnerable bank remembers the txid of every transaction it has done. If you send **the same signature again**, the txid is the same, so the bank answers `409 replay` and does not pay twice. But the twin signature has a **new** txid, so the bank thinks it is a new transaction, even though the owner allowed only one withdrawal (100). If more than 100 is withdrawn, the bank shows a flag.

#### Step 5 — Withdraw with the signature, send it again, then withdraw with the twin

**What to do:** Withdraw with the original signature, then send the original signature again, then send the twin signature.

**Type** one line at a time (straight after Step 2, without starting the lab again, and do not skip the first line):

```bash
docker compose exec vulnerable python bank.py vuln pay original
docker compose exec vulnerable python bank.py vuln pay original
docker compose exec vulnerable python bank.py vuln pay twin
```

**You should see:** two lines each time. Look at the `answer:` line (your txid numbers will be different from the example)

```
answer: HTTP 200 {"amount":100,"status":"processed","total_withdrawn":100,"txid":"417a2e19..."}
answer: HTTP 409 {"error":"replay: txid already processed","txid":"417a2e19..."}
answer: HTTP 200 {"amount":100,"double_spend_detected":true,"flag":"FLAG{ecdsa_malleable_double_spend}","status":"processed","total_withdrawn":200,"txid":"e66a7f5b..."}
```

**Means:** The first time, 100 is withdrawn. Sending the same signature again is caught (`409`). But **the twin signature passes**: the bank pays another 100, the total becomes **200** although the owner allowed it once, and the bank answers `double_spend_detected` with a flag.

**✍️ Write in the answer sheet (Step 5):** copy the three `answer:` lines from your own screen.

#### Step 6 — Answer the two questions

**What to do:** Fill in the blanks in both items (hint: Step 4 and the result in Step 5).

> a) The vulnerable bank sees the twin signature as a ________ transaction (Choose: `old` / `new`) because the transaction number comes from the ________ (Choose: `signature` / `message`).
>
> b) The total withdrawn after sending the twin signature is ________ although the owner allowed 100. (Choose: `100` / `200`)

**✍️ Write in the answer sheet (Step 6):** write both sentences in full.

### A3 — The fixed bank refuses the twin signature (20 points)

#### Step 7 — Try the fixed bank

**What to do:** Ask the fixed bank for a signature (this bank has its own key, so you must ask again), withdraw with that signature, and then try the twin signature.

**Type** one line at a time:

```bash
docker compose exec vulnerable python bank.py fixed sign
docker compose exec vulnerable python bank.py fixed pay original
docker compose exec vulnerable python bank.py fixed pay twin
```

**You should see:** look at the `answer:` line of the last two commands (a signature from the fixed bank is always low-S)

```
answer: HTTP 200 {"amount":100,"status":"processed","total_withdrawn":100,"txid":"d807dd34..."}
answer: HTTP 403 {"error":"non-canonical signature: s must be <= n/2 (BIP-62 low-S)"}
```

**Means:** The fixed bank lets the normal low-S signature withdraw (the total is 100 and there is no flag), but it **refuses the twin signature**, which is high-S (`403`), so it cannot be used to withdraw again.

**✍️ Write in the answer sheet (Step 7):** copy the two `answer:` lines from your own screen.

#### Step 8 — Summarise in your own words

**What to do:** Look at the result of Step 7, then fill in the blanks.

> The fixed bank answers ________ to the twin signature (Choose: `200` / `403`) because it accepts only signatures that are ________. (Choose: `low-S` / `high-S`)

**✍️ Write in the answer sheet (Step 8):** write the full sentence.

#### Step 9 — Find the lines that differ in the code

**What to do:** Find which bank's code checks for low-S.

**Type:**

```bash
docker compose exec vulnerable grep -n "is_low_s" vulnerable_app.py fixed_app.py
```

**You should see:** a match only in the file `fixed_app.py` (line 48 is the function and line 106 is where it is used to check). There is no match from the file `vulnerable_app.py`

```
fixed_app.py:48:def is_low_s(s: int) -> bool:
fixed_app.py:106:    if not is_low_s(s):
```

**Means:** The difference is the single `is_low_s` check. The vulnerable bank does not check it, so it accepts the high-S twin signature.

**✍️ Write in the answer sheet (Step 9):** copy the two lines that show on your screen.

#### Step 10 — How far does the low-S check go?

**What to do:** Read, then answer in 1–2 sentences.

The fixed bank stops **this twin**, but it **still stops repeats with the hash of the signature**. If someone gets the same message signed again, they get a new, different low-S signature. (Optional, you can try it: type `fixed sign` again, then `fixed pay original`. The fixed bank counts it as a new transaction and the total becomes 200.)

> Why does the low-S check stop the repeated withdrawal with the twin signature, and what should a better transaction number come from, instead of the hash of the signature? (hint: Step 6 and Step 9)

**✍️ Write in the answer sheet (Step 10):** write your answer.

#### Step 11 — Shut down the lab and check your answer sheet

**What to do:** Do this after you have copied all the results.

**Type:**

```bash
docker compose down
```

**You should see:** a line ending in `Removed`. Then check that your answer sheet has everything: Steps 2, 3 (A1), Steps 5, 6 (A2), Steps 7, 8, 9, 10 (A3). Then do the part for your own form: odd IDs do Part 2, even IDs do Part 3 and Part 4.

---

## Part 1 — Student Information

| Name | Student ID | Date | Group (your form) | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

## Part 2 — Conventional form (40 points; only if Conventional is your assigned form)

Answer each item in 2–3 sentences. You may answer in English or Thai. In this part **answer by yourself**, without using AI to answer.

**Q1 (10). Digital signature and MAC.** Answer all three of these (1–2 sentences each):

- Which key makes the signature and which key checks it, compared with a MAC (a MAC uses the same key on both sides)?
- Who can check a signature, compared with a MAC?
- Why can a public system (for example a certificate on a website) use digital signatures but not a MAC?

**Q2 (10). The repeated withdrawal.** Answer all three of these (1–2 sentences each):

- What is the twin signature `(r, n−s)`, and why does the vulnerable bank accept it? (hint: Step 1)
- Why is the same signature sent again caught (`409`) but the twin signature passes? (hint: Step 4 and 5)
- How many times did the owner allow a withdrawal, and how many times did the bank pay? (look at the total in Step 5)

**Q3 (10). The fix, and what is still left.** Answer all three of these (1–2 sentences each):

- What does the fixed bank use to fix it, and why is the twin signature refused? (hint: Step 7 and 9)
- If the bank still stops repeats with the hash of the signature, what weakness is left? (hint: Step 10)
- What should a better transaction number come from?

**Q4 (10). Proving you know a secret without telling it (Schnorr).** Answer both of these (2–3 sentences each): How does Peggy prove to Victor that she knows a private key, **without sending the key**? (tell it in words: she sends a starting value, gets a new random challenge, and sends back an answer) And why can someone who listened and recorded the conversation not use it to log in as Peggy?

### Going further (optional — no marks)

- **Q5 — RSA, ECDSA, EdDSA.** Compare the three on the hard problem they use, how easy they are to write correctly, and where the risks are (for example the risk of the nonce `k` in ECDSA), and say why new systems prefer EdDSA (Ed25519).
- **Q6 — Substitution attacks.** How can a signature still verify even though the public key or the message has been swapped?
- **Q7 — Malleability in history.** MtGox and the evidence of Decker and Wattenhofer ([paper](https://arxiv.org/abs/1403.6676)), and how SUF-CMA differs from EUF-CMA, with at least two ways to defend against it.
- **Q8 — Fiat–Shamir.** Replace the random challenge with a hash and you get a proof that needs no interaction (this works for Schnorr, not for every kind of signature).
- **Extension — why `(r, n−s)` is valid (for those who are curious).** When an ECDSA signature is checked, changing `s` to `n−s` makes the point that is computed on the curve become the opposite point, which has the same x-coordinate, and `r` stores only the x-coordinate, so it still matches.

---

## Part 3 — AIR-Sec Arm: Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

An AI wrote a function that "stops the same transaction being processed twice" for a developer. It looks professional, but it has **the same mistake that this lab attacks**.

> **AI's answer:**
>
> ```python
> seen = set()
>
> def process(tx):
>     sig = encode_sig(tx["r"], tx["s"])
>     if not tx["pubkey"].verify(sig, tx["message"]):
>         raise ValueError("bad signature")
>     txid = hashlib.sha256(f'{tx["r"]}:{tx["s"]}'.encode()).hexdigest()
>     if txid in seen:
>         raise ValueError("duplicate transaction")
>     seen.add(txid)
>     apply_transaction(tx)
> ```
>
> "Safe: the signature is verified first, and the txid comes from the signature, so you get idempotency for free. This is better than hashing the message."
>
> — end of AI answer —

1. **Find what's wrong (10).** Copy the wrong line or sentence and write 1–2 sentences on why it is wrong (hint: Step 5)
2. **Fix it (10).** What should the txid be made from instead (for example the message together with the public key, or a sequence number **inside the signed message**), and why does the original code process **the same transaction twice** even though every signature is valid?

> Disclose any other AI use in the Part 1 table. This task counts toward the **Audit the AI** row.

---

## Part 4 — Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** A friend asks: *"How can you prove that you know a password without sending the password?"* Explain in 3–5 sentences, **without difficult words** (sending a starting value, getting a random challenge, sending back an answer, why a recording cannot be used again).

**B. Prompt Problem (10).** Use any AI you like and do this:

1. Write **one** prompt asking the AI to explain why an ECDSA signature can have a "twin" `(r, n−s)`, but EdDSA (Ed25519) cannot.
2. Copy the AI's answer into your answer sheet.
3. Check: (a) does it say that `(r, n−s)` is also valid for the same message and key? (b) does it say that EdDSA checks that `S` is in the standard form (RFC 8032), instead of saying "it is not affected because it is newer"? (c) does it say anything wrong or make anything up (for example mixing this up with reusing a nonce, or a wrong BIP number; the right ones are BIP-62 / BIP-146)?
4. In the table in your answer sheet, tick **pass / fail** for each item with a one-sentence reason, then finish with one sentence saying whether you would trust this AI's answer, and why.

Submit **your prompt + the AI's answer + your check table with your own reasons**.

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "In Step 5, sending the same signature again was caught (`409`) but the twin signature passed. Why, and what does the bank use as the transaction number?"
2. "In Step 7, why did the fixed bank refuse the twin signature, and why is only one of the two signatures low-S?"
3. "Is the low-S check alone enough to stop paying twice? If not, what should be added?"

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — a signature and its twin | 20 | 20 |
| A2 — repeated withdrawal at the vulnerable bank | 20 | 20 |
| A3 — fixed bank + reasoning | 20 | 20 |
| Conventional written questions (Q1–Q4) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- Put your name, student ID and date in the answer sheet, and copy the commands and results from **your own** computer. It is normal that your random signature numbers are not the same as a friend's. Your flag may be the same as a friend's. This week there is no personal flag. Do not submit a friend's results as your own.
- **Explain in your own words** (marks are given for the reasoning): for the fill-in-the-blank items that give you a word bank (Steps 3, 6, 8) you may use the words given. The short answer in Step 10 and the written part of your own form must be in your own words (why the twin signature can be used to withdraw again, and how far the low-S check goes). You do not need to write anything more than that.

**Deadline and late submission:** Submit by 23:59 (Thai time) on **Sunday 17 Jan 2027** (KOSEN rule: before the next class). A late submission loses 10% of this worksheet's marks for each day late (a part day counts as a day), down to 0. Uploading or replacing a file after the deadline counts the whole submission as late. Submit the common 60 marks and **one** form of your own only; doing both forms gives no extra marks. The viva is used to check understanding and has no separate marks.
