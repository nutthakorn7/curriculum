# Worksheet 5 — Key Exchange: Man-in-the-Middle (MITM) and Diffie-Hellman

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Kind:** Docker lab, step by step. No programming and no maths.

> **Ethics note:** Only work on the 3 containers (alice, bob, relay) on your own computer that this lab starts. No port is opened to the outside of your computer.
> Getting in the middle of a system that is not yours, without permission, is illegal.

## Read this first

**What you will do today:** Alice and Bob want a shared secret key over the open internet, so they use **Diffie-Hellman (DH)**. But a `relay` is hiding in the middle. You will watch two rounds: in the round with **no authentication**, the relay can read Alice's message and neither of them knows; in the round **authenticated with HMAC**, the relay fails. Remember this: **DH stops someone who only listens, but it does not stop someone who gets in the middle.**

**Every step is written the same way:**

| Heading | Meaning |
|---|---|
| **What to do** | Says what this step does |
| **Type** | Copy the whole line, paste it into the Terminal, and press Enter |
| **You should see** | The screen should look roughly like this |
| **Means** | What the result means |
| **Write in the answer sheet** | What to copy or write in your answer sheet |

**Marks**

- Everyone does **Part A (60 marks)**, which is the same for both forms.
- Then do **only your own form (40 marks)**. Look at the last digit of your student ID: **odd = AIR-Sec (Parts 3–4)**, **even = Conventional (Part 2)** (0 counts as even). Write your form in the Group box.
- You may answer in English or Thai. Short and clear is enough.
- **Answer sheet:** in Classroom → Week 05, open the file for your form (`Wk05_Answer_Sheet_Conventional` or `Wk05_Answer_Sheet_AIR-Sec`), choose Open with → Google Docs. If it says View only, choose File → Make a copy and work in your copy. Type in the grey boxes, then choose File → Download → PDF.
- Submit one file named with your student ID, for example `Wk05_66990000.pdf` (do not type the `<` `>` signs), at `learn.zcr.ai/submit` with your Week 5 submission code from your KMITL email, by **Sunday 6 Dec, 23:59**.
- Items marked *optional* have no marks. You can skip them.

| Part A | Marks | Steps to write in the answer sheet |
|---|---:|---|
| A1 — The relay can read the message | 20 | Steps 2, 3 |
| A2 — Check the key with HMAC and the relay fails | 20 | Steps 6, 7, 8 |
| A3 — Why HMAC stops it, and its limits | 20 | Steps 10, 11, 12 |

**Words you need to know**

| Word | Simple meaning |
|---|---|
| Terminal / Docker / container | A window where you type commands / a program that starts a small "pretend computer" on your computer. If you break it, delete it and start again |
| Diffie-Hellman (DH) | A way for two sides to get a shared secret by sending only "public values" over the internet. Someone who only listens sees the public values and cannot work out the secret |
| public value | A number each side sends so the other side can see it. It is not secret |
| shared secret | The result of DH, used to make the key that encrypts messages |
| relay / MITM | Something hiding in the middle that answers the DH handshake with both sides at once (man-in-the-middle) |
| HMAC / tag | A "seal" calculated with a secret key, used to check whether data was changed (learned in Week 3) |
| AUTH_KEY | A key that Alice and Bob both know in advance. The relay does not know it. It is used to calculate the tag |
| log | Text a program prints to tell you what it is doing |

**Questions people often ask**

- *Do I need to be good at maths?* No. There is no calculation today.
- *Do I need to write programs?* No. Copy the commands and paste them.
- *If I make a mistake, will my computer break?* No. Everything is inside containers. If you get confused, type `docker compose -f docker-compose.vulnerable.yml down` and `docker compose -f docker-compose.fixed.yml down` and start again.
- *The log is long and full of `CryptographyDeprecationWarning` warnings. Is that wrong?* No. It is a warning that this kind of DH is old. The worksheet filters the log down to just the lines you need.
- *How do I paste a command into the Terminal?* Copy the command from the worksheet, then Windows: press Ctrl+V or right-click · Mac: press Cmd+V, then press Enter.
- *How do I copy results from the Terminal?* Select the text with the mouse first, then Windows: press Ctrl+Shift+C · Mac: press Cmd+C. Or take a screenshot.

**If you see a message like this**

| Message on screen | Cause | Fix |
|---|---|---|
| `failed to connect to the docker API`, `Cannot connect to the Docker daemon` or `error during connect` | Docker is not open | Open Docker Desktop, wait until it says Engine running, then type the command again |
| `no configuration file provided: not found`, or `docker-compose...yml: no such file or directory` | The Terminal is not in the lab folder | Repeat Prep step 4 |
| Step 2 or 6 does not show everything | It has not finished running | Wait 10–15 seconds, then type the same command again |
| `RELAY: error handling connection` with `Connection refused`, or lines are still missing after one minute | Bob was not ready when relay tried to reach Bob | Type the `up -d` command again (Step 1 for the first round, Step 5 for the second), wait 15 seconds, then read the log again |
| Step 6 shows only one `AUTH FAILED` line | You read the screen too early, or Bob was not ready | Wait a moment and type the same command again. If there is still only one line, type the Step 5 command again, wait 15 seconds, then repeat Step 6. You must see two lines (alice and bob) |
| Windows: `grep` is not recognised | Windows has no `grep` | Use the `findstr` or PowerShell commands that the worksheet gives in each step |

If you still cannot do it, ask a friend or your instructor. If you really cannot use Docker, tell your instructor, then answer Steps 3 and 10–12 by reading the worksheet and the picture. For the other steps, write "did not run it myself".

---

## Before you start: set up your computer (at home, once)

If you already did Weeks 2–4, you have Docker and the ZIP file. Start at **Prep step 4**. If you cannot find the `week05-key-exchanges` folder, download the ZIP again as in Prep step 2.

**If you turned your computer off and came back:** repeat Prep steps 1 and 4.

#### Prep step 1 — Open Docker Desktop

**What to do:** If you do not have it yet, install it from <https://www.docker.com/products/docker-desktop/> and leave the program open. **You should see:** it says **Engine running**.

#### Prep step 2 — Download and unzip the lab files

**What to do:** Open <https://github.com/nutthakorn7/security-cryptography>, click the green **Code** button, and choose **Download ZIP** (you do not need a GitHub account), then unzip it (Windows: right-click and choose **Extract All** · Mac: double-click). **You should see:** a folder called `security-cryptography-master`. Some computers make a folder with the same name inside it; open it until you can see the `labs` folder.

#### Prep step 3 — Go into the lab folder

**What to do:** Go into `labs`, then into `week05-key-exchanges`.

#### Prep step 4 — Open a Terminal inside the lab folder

- **Windows:** open the `week05-key-exchanges` folder in File Explorer, right-click an empty spot, and choose **Open in Terminal** (if you do not see it, hold Shift, right-click, and choose **Open PowerShell window here**).
- **Mac:** open the Terminal app, type `cd` and one space, drag the `week05-key-exchanges` folder into the window, then press Enter.

Check that you are in the right place with this command (Windows: use `dir`):

```bash
ls
```

**You should see:** `docker-compose.vulnerable.yml` and `docker-compose.fixed.yml` in the list.

#### Prep step 5 — Build the lab (you need the internet)

**Type:**

```bash
docker compose -f docker-compose.vulnerable.yml build
```

**You should see:** the last line ends with `Built`. The first time it may take several minutes. Do not close the window while you wait. If you finish this at home, the lesson will start faster.

---

## Part A — The lab (both forms, 60 marks)

This lab has three characters: **Alice** sends a secret message to **Bob**, but Alice is set up to talk through the `relay` (she does not reach Bob directly). That is the real situation: whoever "picks up when we call Bob" may not be Bob.

![Picture: in the round with no authentication, Alice does a DH with the relay and gets one secret, and the relay does a DH with Bob and gets another secret. So the relay can decrypt Alice's message, read it, and encrypt it again to forward to Bob. Alice and Bob do not share a secret with each other directly. (The relay does one DH with Alice and another with Bob, so it can read and forward the message; Alice and Bob never share a secret with each other.)](img/w5-two-handshakes.svg)

### A1 — The relay can read the message (20 marks)

#### Step 1 — Start the round with no authentication

**What to do:** Start alice, bob and the relay in the round where nobody checks who they are talking to, then wait for it to finish running.

**Type:**

```bash
docker compose -f docker-compose.vulnerable.yml up -d
```

**You should see:** the word `Started` on about three lines. Wait about 15 seconds. This step has nothing to write in the answer sheet.

#### Step 2 — Read the log, only the lines you need

**What to do:** Look at the log, filtered to the lines from ALICE, BOB and RELAY.

**Type** (Mac):

```bash
docker compose -f docker-compose.vulnerable.yml logs | grep -E "ALICE|BOB|RELAY"
```

**Type** (Windows PowerShell):

```powershell
docker compose -f docker-compose.vulnerable.yml logs | findstr "ALICE BOB RELAY"
```

**You should see:** about 9 lines. Find **these four lines** (the order may be slightly different; the text after `from` is an address inside your computer, ignore it):

```
RELAY: completed independent DH handshake with Alice (posing as Bob)
BOB RECEIVED: the launch code is 4471
RELAY: completed independent DH handshake with Bob (posing as Alice)
RELAY INTERCEPTED: the launch code is 4471
```

**Means:** the relay did DH twice, separately. The first time with Alice (pretending to be Bob), the second time with Bob (pretending to be Alice). Then it decrypted Alice's message and could read it (`INTERCEPTED`), while Bob also received the message normally (`BOB RECEIVED`). So neither of them noticed. The message `the launch code is 4471` is a fixed message of the lab. It is not a personal code.

**✍️ Write in the answer sheet (Step 2):** copy the four lines above from your own screen.

#### Step 3 — Summarise in your own words

**What to do:** Look at the picture above and fill in the blanks.

> a) The relay shares a secret with Alice **and** a secret with Bob, so there are ________ secrets in total (1 / 2). Alice and Bob (have / do not have) a secret directly between them.
>
> b) The relay can read the message because it (decrypted it with a secret it holds itself / solved the very hard DH equation).

**✍️ Write in the answer sheet (Step 3):** write both sentences in full.

#### Step 4 — Shut down the first round

**Type:**

```bash
docker compose -f docker-compose.vulnerable.yml down
```

**You should see:** a line ending in `Removed`. This step has nothing to write in the answer sheet.

### A2 — Check the key with HMAC and the relay fails (20 marks)

#### Step 5 — Start the round "authenticated with HMAC"

**What to do:** In this round Alice and Bob attach a tag (an HMAC made with AUTH_KEY) to their own public value. The relay does not know AUTH_KEY.

**Type:**

```bash
docker compose -f docker-compose.fixed.yml up -d
```

**You should see:** the word `Started`. Wait about 15 seconds. This step has nothing to write in the answer sheet.

#### Step 6 — Read the log of the second round

**Type** (Mac):

```bash
docker compose -f docker-compose.fixed.yml logs | grep -E "ALICE|BOB|RELAY|AUTH"
```

**Type** (Windows PowerShell):

```powershell
docker compose -f docker-compose.fixed.yml logs | findstr "ALICE BOB RELAY AUTH"
```

**You should see:** find **these four lines** (the relay still tries to insert its own value, but both alice and bob notice and cancel):

```
RELAY: (fixed mode) attempted DH substitution with Alice (posing as Bob)
RELAY: (fixed mode) attempted DH substitution with Bob (posing as Alice)
AUTH FAILED - ABORTING      (from bob)
AUTH FAILED - ABORTING      (from alice)
```

**Means:** the relay uses almost the same code and still inserts its own value, but it cannot make a correct tag for that value, because it does not have AUTH_KEY. Both sides noticed and stopped, before sending any secret message.

**✍️ Write in the answer sheet (Step 6):** copy the four lines above (so that one `AUTH FAILED` line comes from alice and one from bob).

#### Step 7 — Count how many times the relay could read the message

**Type** (Mac):

```bash
docker compose -f docker-compose.fixed.yml logs | grep -c "RELAY INTERCEPTED"
```

**Type** (Windows PowerShell):

```powershell
(docker compose -f docker-compose.fixed.yml logs | Select-String -SimpleMatch "RELAY INTERCEPTED" | Measure-Object).Count
```

**You should see:** `0`

**Means:** in this round there is no `RELAY INTERCEPTED` line at all. (This number only says that the relay did not read the message. It does not prove that Alice and Bob talked successfully.)

**✍️ Write in the answer sheet (Step 7):** write the number you got.

#### Step 8 — Summarise in your own words

**What to do:** Fill in the blanks.

> The relay cannot make a correct ________ for its own public value, because it does not have the ________. (Choose: `tag` / `AUTH_KEY`; the second blank is `AUTH_KEY`)

**✍️ Write in the answer sheet (Step 8):** write the full sentence.

#### Step 9 — Shut down the second round

**Type:**

```bash
docker compose -f docker-compose.fixed.yml down
```

**You should see:** a line ending in `Removed`. This step has nothing to write in the answer sheet.

### A3 — Why HMAC stops it, and its limits (20 marks)

#### Step 10 — Look at the code that makes the tag

**What to do:** Read these two lines from `common.py` (you do not need to type anything). The first function calculates the tag from the public value and AUTH_KEY. The second checks whether the tag that arrived matches the one it calculated itself.

```python
return hmac.new(auth_key, pubkey_bytes, hashlib.sha256).digest()      # make the tag
return hmac.compare_digest(expected, tag)                            # check the tag
```

> The tag is calculated from ________ and ________. (Choose: `the public value` / `AUTH_KEY` / `the secret message`)

**✍️ Write in the answer sheet (Step 10):** write the full sentence.

#### Step 11 — Why still do a fresh DH every time?

**What to do:** Read, then answer in 1–2 sentences. Alice and Bob already know AUTH_KEY together. Why not just use AUTH_KEY as the key to encrypt the messages? (Hint: if AUTH_KEY leaks next year, what happens to the messages somebody recorded today? What if each round's key was made by a new DH whose secrets were thrown away?)

**✍️ Write in the answer sheet (Step 11):** write your answer.

#### Step 12 — The limit of this method

**What to do:** Answer in 1–2 sentences. This method works because of one condition: Alice and Bob must share AUTH_KEY **in advance** and keep it secret. If the relay got AUTH_KEY too, what would happen? And by what route should AUTH_KEY be shared between them?

**✍️ Write in the answer sheet (Step 12):** write your answer.

#### Step 13 — Check before you go on

Check that your answer sheet has everything: Steps 2, 3 (A1), Steps 6, 7, 8 (A2), Steps 10, 11, 12 (A3). Then do your own form: odd IDs do Parts 3 and 4; even IDs do Part 2.

---

## Part 1 — Student Information
| Name | Student ID | Date | Group (your form) | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

## Part 2 — Conventional form (40 marks; only if Conventional is your assigned form)

Answer each in 2–3 sentences. You may answer in Thai. In this part you must **answer yourself** and not use AI. There is no calculation.

**Q1 (10). Why not send the AES key straight over the internet.** If the key were sent straight over the internet, what would someone who only listens get, and what does DH let Alice and Bob do instead? (Hint: public value)

**Q2 (10). How does the relay read it.** In the round with no authentication, who shares a secret with Alice and who shares one with Bob? How can the relay read the message without solving any hard problem? (Hint: Steps 2 and 3)

**Q3 (10). What does HMAC stop.** Plain DH stops someone who only listens, but the relay can insert its own value. What does the HMAC in the second round stop, and what one condition does this method need? (Hint: Steps 6 and 12)

**Q4 (10). Why still do a fresh DH.** Why does the second round still make a new key with DH, instead of using AUTH_KEY to encrypt the messages? If AUTH_KEY leaks later, what happens to messages recorded earlier? (Hint: Step 11)

### Going further (optional — no marks)

- Why use a large, well-known DH group (RFC 3526)? What if a peer's public value is not validated?
- How do ECDH and X25519 differ from this finite-field demo?
- Authenticated DH needs a trusted way to share the key or certificate first. What is that "trust bootstrap" in TLS?

---

## Part 3 — AIR-Sec Arm: Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

A friend asked an AI how to stop a man-in-the-middle in DH. The AI answered as below (in English; you do not need to translate every word):

> **AI's answer:**
> "Alice and Bob can run plain DH, derive a fresh session key, and then authenticate every message with HMAC under that derived key. A MITM cannot know the session key, so a valid message HMAC proves Bob's identity. No certificate or pre-shared key is needed."
>
> — end of AI answer —

Do this (use what you saw in the lab):

1. **Find what's wrong.** Copy the sentence that is wrong, then write 1–2 sentences on why it is wrong (hint: in Step 2 the relay already has a "session key" of its own with Alice).
2. **Write the corrected version.** Write a correct explanation in 2–3 sentences, saying what is needed that the relay does not have (hint: Steps 6 and 12).

> Disclose any other AI use in the Part 1 table. This task counts toward the **Audit the AI** row.

---

## Part 4 — Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** Explain to a friend who has never studied DH, in 2–4 sentences, **without difficult words**: in the first round, who shares a secret with Alice, who shares one with Bob, and why can the relay read and forward the message? (Hint: look at the picture and Step 3, and use your own words)

**B. Prompt Problem (10).** Use any AI you like and follow these steps:

1. Write **one** prompt, for example *"Explain why authenticated Diffie-Hellman prevents a man-in-the-middle attack"*
2. Copy the AI's answer into your answer sheet.
3. Check the AI's answer against what you learned, one point at a time, and tick **Pass / Fail** with a one-sentence reason for each:

- Does the AI separate "stops eavesdroppers" (plain DH already does this) from "confirms who is on the other end" (plain DH does not)?
- Does the AI say how the public value is tied to an identity (for example a tag, a signature, a certificate), and that the key or certificate has to reach each side safely first?
- Does the AI make anything up or say something wrong? (Does it make anything up?) For example, naming a method that does not exist.

Hand in the **prompt + the AI's answer + the check table with your own reasons**.

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "In Step 2 the relay did DH twice before it printed `RELAY INTERCEPTED`. Why twice? What would happen if it did it only once?"
2. "In Step 6 the relay still inserted its own value, with almost the same code. Why did it fail this time?"
3. "Alice and Bob already share AUTH_KEY. Why not use it directly as the encryption key? (Step 11)"

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — relay reads the message | 20 | 20 |
| A2 — HMAC check stops relay | 20 | 20 |
| A3 — why it works + limits | 20 | 20 |
| Conventional written questions (Q1–Q4) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- Put your name, student ID and the date in the answer sheet, and copy the commands and results from **your own** computer. The line `the launch code is 4471` is a fixed message of the lab, the same for everyone. It is not a personal flag. You must not submit a friend's results as your own.
- **Explain in your own words** (marks are given for the reasoning): for the fill-in-the-blank steps (Steps 3, 8, 10) you can use the words given. The short answers in Steps 11 and 12 and the written parts of your own form must be in your own words.

**Deadline and late work:** submit by 23:59 (Thai time) on **Sunday 6 Dec**. Late work loses 10% of this worksheet's marks per day (a part day counts as a day), down to 0. Uploading or replacing a file after the deadline counts as late for the whole submission. Submit the common 60 marks and **one** form of your own only; doing both forms gives no extra marks. The viva checks your understanding and has no separate marks.
