# Worksheet 10 — Hybrid Encryption: lock the key with RSA, lock the messages with AES-GCM

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Kind:** Docker lab, step by step. No programming and no maths (the AIR-Sec form has a short scripting task in Part 3).

> **Ethics note:** Only work on the demo code in the container on your own computer that this lab starts. There is no real server and no port is opened to the outside of your computer. Reusing a nonce on a real system that is not yours, without permission, is illegal.

## Read this first

**What you will do today:** RSA cannot encrypt big files well (it is slow, and it can only take short data). So real systems use **hybrid encryption**: Bob makes **one AES key**, locks that key with **Alice's public key**, and sends it once. Then he encrypts every message with the AES key using AES-GCM, which uses a **nonce** (a number used once) for each message. Today you will watch Bob send messages to Alice, and then see what happens if Bob **reuses a nonce**: a listener (Eve) can read the secret message without any key. Remember this: **however strong the key is, it does not help if the nonce is reused.**

**Every step is written the same way:**

| Heading | Meaning |
|---|---|
| **What to do** | Says what this step does |
| **Type** | Copy the whole line, paste it into the Terminal, and press Enter |
| **You should see** | The screen should look roughly like this (the hex numbers of the nonce will be different from the example, and that is normal) |
| **Means** | What the result means |
| **Write in the answer sheet** | What to copy or write in your answer sheet |

**Marks**

- Everyone does **Part A (60 marks)**, which is the same for both forms.
- Then do **only your own form (40 marks)**. Look at the last digit of your student ID: **odd = Conventional (Part 2)**, **even = AIR-Sec (Parts 3–4)** (0 counts as even). Write your form in the Group box.
- You may answer in English or Thai. Short and clear is enough.
- **Answer sheet:** in Classroom → Week 10, open the file for your form (`Wk10_Answer_Sheet_Conventional_odd_ID` or `Wk10_Answer_Sheet_AIR-Sec_even_ID`), choose Open with → Google Docs, type in the grey boxes, then choose File → Download → PDF.
- Submit one file named with your student ID, for example `Wk10_66990000.pdf` (do not type the `<` `>` signs), at `learn.zcr.ai/submit` with your Week 10 submission code from your KMITL email, by the deadline in the email and in the Classroom post.
- Items marked *optional* have no marks. You can skip them.

| Part A | Marks | Steps to write in the answer sheet |
|---|---:|---|
| A1 — Bob sends messages to Alice (a new nonce every time) | 20 | Steps 2, 3 |
| A2 — Bob reuses a nonce, and Eve reads the secret | 20 | Steps 5, 6 |
| A3 — With a new nonce every time, Eve cannot read | 20 | Steps 7, 8, 9, 10 |

**Words you need to know**

| Word | Simple meaning |
|---|---|
| Terminal | A window where you type commands |
| Docker / container | A program that starts a small "pretend computer" on your computer. If you break it, delete it and start again |
| public key / private key | Alice's key pair: **anyone can lock with the public key, but only Alice can open with the private key** |
| RSA | A public-key way to encrypt. It is slow and takes only short data, so it is used only to lock the **AES key** |
| session key | The AES key that Bob makes new each time they start talking. It encrypts the real messages |
| AES-GCM | A fast way to encrypt messages that adds a tag to check whether the data was changed (learned in Weeks 4 and 6) |
| nonce | A number used together with the key when encrypting each message. It **must not repeat** with other messages under the same key. It can travel with the message and does not have to be secret |
| Eve | A listener who sees everything that travels on the network, but knows no key |
| flag | A prize message in the form `FLAG{...}`, which is proof that you succeeded |

**Questions people often ask**

- *Do I need to be good at maths?* No. There is no calculation today.
- *Do I need to write programs?* No. Copy the commands and paste them (except for the Audit task of the AIR-Sec form).
- *If I make a mistake, will my computer break?* No. Everything is inside a container. If you get confused, type `docker compose down` and start again from Prep step 5.
- *Can I skip understanding every character on the screen?* Yes. Only look at the lines the worksheet tells you to.
- *My nonce numbers are not the same as my friend's. Is that wrong?* No. The keys and nonces are random every time you run it. But the messages, the YES/NO results and the RESULT lines must be the same, and you must always copy from your own computer.
- *How do I paste a command into the Terminal?* Copy the command from the worksheet, then Windows: press Ctrl+V or right-click · Mac: press Cmd+V, then press Enter.
- *How do I copy results from the Terminal?* Select the text with the mouse first, then Windows: press Ctrl+Shift+C · Mac: press Cmd+C. Or take a screenshot.

**If you see a message like this**

| Message on screen | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` or `error during connect` | Docker is not open | Open Docker Desktop and wait until it says Engine running |
| `no configuration file provided: not found` | The Terminal is not in the lab folder | Repeat Prep step 4 |
| `service "lab" is not running` | The lab is not started | Do Prep steps 5 and 6 |
| `ModuleNotFoundError: No module named 'cryptography'` | The lab has not finished installing packages | Wait a moment, then repeat Prep step 6 |
| `can't open file '/lab/demo.py'` | The ZIP you downloaded is old and has no `demo.py` | Download a new ZIP as in Prep step 2 |
| The first thing on screen is a long explanation (`Week 10 helper: ...`) | You typed the command wrong or left a word out | Copy the command from the worksheet again, the whole line |

If you still cannot do it, ask a friend or your instructor.

---

## Before you start: set up your computer (at home, once)

If you already did Weeks 2–6, you have Docker and the ZIP file. Start at **Prep step 4**. But the ZIP must be a recent one that has the folder `week10-hybrid-encryption` and the file `demo.py`. If you cannot find them, download the ZIP again as in Prep step 2.

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

**What to do:** Open the `labs` folder inside `security-cryptography-master`, then open `week10-hybrid-encryption`.

- **Windows:** open the `week10-hybrid-encryption` folder in File Explorer, right-click an empty spot, and choose **Open in Terminal** (if you do not see it, hold Shift, right-click, and choose **Open PowerShell window here**)
- **Mac:** open the Terminal app, type `cd` and one space, drag the `week10-hybrid-encryption` folder into the window, then press Enter

Check that you are in the right place with this command:

```bash
ls
```

**You should see:** `docker-compose.yml` and `demo.py` in the list.

#### Prep step 5 — Start the lab

**Type:**

```bash
docker compose up -d
```

**You should see:** a line ending in `Started` (if the lab was already running you may see `Running`). **You need the internet every time you start this lab**, because the container installs packages each time it starts. The first time it may take several minutes. Do not close the window while you wait.

#### Prep step 6 — Check that the lab is ready

**Type** (Mac):

```bash
docker compose logs | grep "lab ready"
```

**Type** (Windows):

```powershell
docker compose logs | findstr /C:"lab ready"
```

**You should see:** a line that contains `week 10 lab ready`. If you see nothing, wait a moment and type the command again. If it still fails after 2 minutes, type `docker compose ps -a`, take a screenshot, and send it to your instructor.

---

## Part A — The lab (both forms, 60 points)

Bob sends two messages to Alice in one conversation (one session). The script `demo.py` can run in two ways. They differ only in how the nonce is chosen:

| Way | Nonce | What Eve can do |
|---|---|---|
| `good` | **a new nonce for every message** | Eve cannot read the message |
| `reuse` | **the same nonce** for both messages | Eve reads the secret message without the key |

> **If you really cannot use Docker:** tell your instructor, then follow the example results given in each step and write "from the worksheet example" next to them. Steps 6, 8 and 10 can be answered by reading the worksheet.

### A1 — Bob sends messages to Alice (a new nonce every time) (20 points)

#### Step 1 — Read: who holds what?

**What to do:** Just read. You do not need to type anything.

| Who | Holds what | Does what |
|---|---|---|
| **Alice** | A public key (given to everyone) and a private key (kept by her alone) | Opens the session key with her private key, then opens the messages |
| **Bob** | An AES key that he makes at random (the session key) | Locks the session key with **Alice's public key** and sends it once, then encrypts each message with the session key and a nonce |
| **Eve** | No keys at all | Sees only what travels on the network: the locked key, the nonces and the encrypted messages |

#### Step 2 — Watch Bob send two messages (a new nonce every time)

**What to do:** Let the script play Bob sending two messages to Alice, and Alice opening them.

**Type:**

```bash
docker compose exec lab python demo.py good
```

**You should see:** several lines. Find **these four lines** (your nonce numbers will be different from the example)

```
Bob made ONE session key (AES-256) and locked it with Alice's public key: 256 bytes, sent once.
message 1: nonce da87a4db6e7e0a5d6c5d2bea  ciphertext 35 bytes + 16-byte tag
message 2: nonce 83d9bf4841c7fb276580aab7  ciphertext 33 bytes + 16-byte tag
nonces equal? NO (a new nonce for every message)
```

**Means:** The session key was locked with RSA and sent once. The messages are encrypted with AES-GCM one by one, and each message has its own nonce, which are **not the same** (`NO`). Alice can open both messages (see the lines `message 1 ->` and `message 2 ->` in the full output).

**✍️ Write in the answer sheet (Step 2):** copy the four lines above from your own screen.

#### Step 3 — Summarise in your own words

**What to do:** Fill in the blanks.

> Bob locks the session key with Alice's ________ key, and Alice opens it with her own ________ key. (Choose: `public` / `private`) The messages themselves are encrypted with ________. (Choose: `RSA` / `AES`)

**✍️ Write in the answer sheet (Step 3):** write the full sentence.

### A2 — Bob reuses a nonce, and Eve reads the secret (20 points)

#### Step 4 — Read: what can Eve do?

**What to do:** Just read. You do not need to type anything.

AES-GCM uses the key and the nonce to make a "random strip" that covers the message. If the nonce is **the same**, the strip is **the same**. So two messages are covered by the same strip. Eve does not need the key. She only compares the two encrypted messages. If she already knows the first message (for example the greeting that Bob sends every time), she gets the second message out. The script does this step for her, so you do not calculate anything.

#### Step 5 — Let Bob reuse the nonce, then let Eve try

**What to do:** Run the `reuse` way to see that the nonce is the same but Alice can still read everything as normal, then let Eve try to read the second message.

**Type** one line at a time:

```bash
docker compose exec lab python demo.py reuse
docker compose exec lab python demo.py attack reuse
```

**You should see:** the first command prints several lines. Look at the two lines `message 1:` and `message 2:` and the line `nonces equal?`. The second command prints Eve's result.

```
message 1: nonce a3236abaf2924d9ec5591526  ciphertext 35 bytes + 16-byte tag
message 2: nonce a3236abaf2924d9ec5591526  ciphertext 33 bytes + 16-byte tag
nonces equal? YES (the same nonce was used twice)
Eve's reading of message 2: Secret: FLAG{same_nonce_leaks_it}
RESULT: Eve read message 2 WITHOUT the key.
```

**Means:** The two nonces are **exactly the same** (`YES`). Alice can still open the messages as normal, so nothing tells her there is a problem. But Eve reads the second message, which holds the flag, **without the key**. The line `Eve's reading` is the same on every computer.

**✍️ Write in the answer sheet (Step 5):** copy the five lines above from your own screen.

#### Step 6 — Answer the two questions

**What to do:** Fill in the blanks in both items (hint: Step 4 and the lines in Step 5).

> a) Eve (knows / does not know) the key, but she can still read the second message, because Bob used the same ________ twice. (Choose: `nonce` / `key`)
>
> b) Eve has to know the first message first (for example the greeting that Bob sends every time) to read the second message. (Choose: `true` / `false`)

**✍️ Write in the answer sheet (Step 6):** write both sentences in full.

### A3 — With a new nonce every time, Eve cannot read (20 points)

#### Step 7 — Let Eve try the "new nonce" session

**What to do:** Let Eve use the same method on the `good` session (a new nonce for every message).

**Type:**

```bash
docker compose exec lab python demo.py attack good
```

**You should see:** these three lines (the strange characters in the line `Eve's reading` will be different every time)

```
nonces equal? NO
Eve's reading of message 2: ?T(??J?m??w?o???J??p??q????W Ulk?
RESULT: Eve got nothing readable.
```

**Means:** The nonces are different, so the random strips are different, and Eve's method only gives mixed-up characters.

**✍️ Write in the answer sheet (Step 7):** copy the three lines above from your own screen.

#### Step 8 — Summarise in your own words

**What to do:** Look at the results of Step 5 and Step 7, then fill in the blanks.

> When the nonce is **different**, Eve reads the message ________. (Choose: `easily` / `not at all`) When the nonce is **reused**, Eve reads the message ________. (Choose: `easily` / `not at all`)

**✍️ Write in the answer sheet (Step 8):** write the full sentence.

#### Step 9 — Find the lines that differ in the code

**What to do:** Look at the two lines of code that choose the nonce.

**Type:**

```bash
docker compose exec lab grep -n "nonces = " demo.py
```

**You should see:**

```
40:        nonces = [os.urandom(12)] * 2                              # the SAME nonce for both messages
42:        nonces = [os.urandom(12), os.urandom(12)]                  # a NEW nonce for each message
```

**Means:** The first line makes one random number and uses it twice (`* 2`). The second line makes two new random numbers. A tiny difference in the code makes a huge difference in the result.

**✍️ Write in the answer sheet (Step 9):** copy the two lines that show on your screen.

#### Step 10 — Why is a repeated nonce dangerous?

**What to do:** Read, then answer in 1–2 sentences.

A nonce does **not have to be secret** (it can travel with the message), but it **must never repeat** with other messages under the same key. However strong the RSA that locks the session key is, it does not help if the nonce is reused.

> Why can Eve read the second message even though she does not know the key, and what should Bob do so that this does not happen? (hint: Step 5 and Step 9)

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

**Q1 (10). Why not use RSA for big files?** RSA cannot lock a whole video or PDF file well.

Answer both of these (1–2 sentences each):

- Why is public-key encryption (such as RSA) not good for big files? (hint: think about **speed** and **how much data it can take**)
- How do real systems solve this, and what do they use RSA for instead? (hint: the table in Step 1)

**Q2 (10). Bob sends messages to Alice.** Tell the steps of hybrid encryption from the beginning to the end.

Answer all three of these (1–2 sentences each):

- What key does Bob make, and what does he send to Alice once?
- What is encrypted with which key? (hint: the result of Step 2)
- How does Alice open the messages?

**Q3 (10). Why only Alice can read.** Alice gives her public key to everyone.

Answer all three of these (1–2 sentences each):

- Why can Bob (or anyone) lock a message for Alice with her public key?
- Why can only Alice open it? (hint: Step 3)
- What does Eve, who is listening, see, and why can she still not read the message?

**Q4 (10). The repeated nonce.** In the lab, Eve read the secret message without knowing the key.

Answer all three of these (1–2 sentences each):

- What did Bob do wrong? (hint: Step 5 and Step 9)
- Does a nonce have to be secret, and what property must it have?
- Does locking the session key with RSA help against this problem? Why? (hint: Step 10)

### Going further (optional — no marks)

- **Q5 — Key exchange.** How does Diffie-Hellman key exchange create a shared secret, and why can Eve, who sees both public values, still not work out the secret? (learned in Week 5)
- **Q6 — ECIES.** ECIES is hybrid encryption that uses elliptic-curve Diffie-Hellman. Explain how Alice and Bob can encrypt and decrypt without sending the AES key directly.
- **Extension — why a repeated nonce can be read (for those who are curious).** The random strip (keystream) covers the message: encrypted message = message ⊕ strip. If the strip repeats, then when you ⊕ the two encrypted messages together, the strip disappears and you are left with message 1 ⊕ message 2. If you then ⊕ that with the known first message, you get the second message.

---

## Part 3 — AIR-Sec Arm: Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

A friend asked an AI to write hybrid encryption code, which is in `audit_the_ai/broken_hybrid_encrypt.py`. It runs and gives the right result, and it looks careful, but it has one mistake that is similar to what we saw in Part A but hides in the code in a different way (the RSA-OAEP, the AES key and the tag check are correct). You can run it in the same container, for example `docker compose exec lab python audit_the_ai/broken_hybrid_encrypt.py`. More details are in `audit_the_ai/README.md`.

1. **Find what's wrong (7).** Copy the wrong line and write 1–2 sentences on why it is wrong.
2. **Prove it (7).** Write a short script that sends two messages in one session, and show what someone who sees only the encrypted messages can do (include the script and the result).
3. **Fix it (6).** Hand in `fixed_hybrid_encrypt.py` (the smallest change) and write 1–2 sentences on why the RSA/OAEP part does not need a fix.

> Disclose any other AI use in the Part 1 table. This task counts toward the **Audit the AI** row.

---

## Part 4 — Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** A friend who has never studied encryption asks: *"Why not encrypt everything with RSA? Why mix in AES?"* Explain in 3–5 sentences, **without difficult words** (hint: the table in Step 1).

**B. Prompt Problem (10).** Use any AI you like and do this:

1. Write **one** prompt asking the AI to write hybrid encryption in Python (Bob sends many messages to Alice).
2. Copy the AI's answer into your answer sheet.
3. Check: (a) does it use an AEAD (AES-GCM or ChaCha20-Poly1305)? (b) does it use a **new nonce for every message**? (c) does the AI say anything wrong or make anything up (for example "a nonce can repeat if the key is strong")?
4. In the table in your answer sheet, tick **pass / fail** for each item with a one-sentence reason, then finish with one sentence saying whether you would trust this AI's answer, and why.

Submit **your prompt + the AI's answer + your check table with your own reasons**.

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "In Step 5 Bob reused the nonce. Why did Alice not notice any problem, while Eve could read the secret message?"
2. "In Step 7 the nonces were different. What did Eve get, and why?"
3. "If Bob sent only one message per session and then threw the key away, would the `reuse` code still be dangerous? Why is it still a bad habit?"

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — hybrid flow, a new nonce every time | 20 | 20 |
| A2 — repeated nonce, Eve reads the secret | 20 | 20 |
| A3 — new nonce, Eve cannot read + reasoning | 20 | 20 |
| Conventional written questions (Q1–Q4) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- Put your name, student ID and date in the answer sheet, and copy the commands and results from **your own** computer. It is normal that your random nonce values are not the same as a friend's. This week there is no personal flag. Do not submit a friend's results as your own.
- **Explain in your own words** (marks are given for the reasoning): for the fill-in-the-blank items that give you a word bank (Steps 3, 6, 8) you may use the words given. The short answer in Step 10 and the written part of your own form must be in your own words (why Eve can read the secret message when the nonce is reused even though she does not know the key). You do not need to write anything more than that.

**Deadline and late submission:** Submit by 23:59 (Thai time) on the Sunday before the next class (KOSEN rule). The exact date is in the submission-code email and in this week's Classroom post. A late submission loses 10% of this worksheet's marks for each day late (a part day counts as a day), down to 0. Uploading or replacing a file after the deadline counts the whole submission as late. Submit the common 60 marks and **one** form of your own only; doing both forms gives no extra marks. The viva is used to check understanding and has no separate marks.
