# Worksheet 13 — End-to-End Encryption: HTTPS is not enough

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** CWE-311 (Missing Encryption of Sensitive Data), CWE-532 (Sensitive Information in a Log File), CWE-312 (Cleartext Storage of Sensitive Information)
> **Kind:** Docker lab, step by step. No programming and no maths.

> **Ethics note:** Only work on the containers on your own computer that this lab starts (a pretend server, Alice and Bob). The lesson is "can the service provider read its users' messages?" Reading or storing other people's messages on a system that is not yours and without permission is illegal.

## Read this first

**What you will do today:** Almost every chat app uses HTTPS, so messages are encrypted on the way. But when a message reaches the **provider's server**, the server decrypts it, stores it, and can write it to a log. So the provider can read every message. We will look at a pretend server that does exactly this, and then at **end-to-end encryption (E2EE)**, where Alice encrypts the message **on her own computer** with Bob's public key, so the server sees only data it cannot read. Remember this: **HTTPS protects the message on the way, not from the provider.**

**Every step is written the same way:**

| Heading | Meaning |
|---|---|
| **What to do** | Says what this step does |
| **Type** | Copy the whole line, paste it into the Terminal, and press Enter |
| **You should see** | The screen should look roughly like this (the output has other Docker lines mixed in; only look at the lines the worksheet tells you to) |
| **Means** | What the result means |
| **Write in the answer sheet** | What to copy or write in your answer sheet |

**Marks**

- Everyone does **Part A (60 marks)**, which is the same for both forms.
- Then do **only your own form (40 marks)**. Look at the last digit of your student ID: **odd = AIR-Sec (Parts 3–4)**, **even = Conventional (Part 2)** (0 counts as even). Write your form in the Group box.
- You may answer in English or Thai. Short and clear is enough.
- **Answer sheet:** in Classroom → Week 13, open the file for your form (`Wk13_Answer_Sheet_Conventional` or `Wk13_Answer_Sheet_AIR-Sec`), choose Open with → Google Docs, type in the grey boxes, then choose File → Download → PDF.
- Submit one file named with your student ID, for example `Wk13_66990000.pdf` (do not type the `<` `>` signs), at `learn.zcr.ai/submit` with your Week 13 submission code from your KMITL email, by **Sunday 31 Jan 2027, 23:59**.
- Items marked *optional* have no marks. You can skip them.

| Part A | Marks | Steps to write in the answer sheet |
|---|---:|---|
| A1 — the server can read the message (HTTPS only) | 20 | Steps 2, 3 |
| A2 — encrypted on Alice's computer (E2EE), the server cannot read | 20 | Steps 5, 6 |
| A3 — where the difference is, and what the lab does not prove | 20 | Steps 7, 8, 9, 10 |

**Words you need to know**

| Word | Simple meaning |
|---|---|
| Terminal | A window where you type commands |
| Docker / container | A program that starts a small "pretend computer" on your computer. If you break it, delete it and start again |
| server (the provider) | The middle computer of a chat app. It receives a message from the sender, stores it, and passes it on to the receiver |
| plaintext / ciphertext | A message you can read / a message that has been encrypted and cannot be read |
| HTTPS (TLS) | Encrypts the connection between us and the server, but the server is the end of that connection, so it sees the message |
| E2EE (end-to-end) | The sender encrypts the message on their own computer, and only the receiver can decrypt it. The server sees only ciphertext |
| public key | Bob's key, which he can give to anyone. It locks a message for Bob, and only Bob can open it with his private key |
| log | A record of what a program did, which the system administrator can read |

**Questions people often ask**

- *Do I need to be good at maths?* No.
- *Do I need to write programs?* No. Copy the commands and paste them.
- *If I make a mistake, will my computer break?* No. Everything is inside containers. If you get confused, type the two commands in Step 11 and start again.
- *Can I skip understanding every line on the screen?* Yes. Only look at the lines the worksheet tells you to.
- *The base64 line is very long. Do I have to copy all of it?* No. Copy **about the first 60 characters** and add `...`
- *My base64 letters are not the same as my friend's. Is that wrong?* No. The keys are random every time, but the readable message in Bob's log must be the same.
- *How do I paste a command into the Terminal?* Copy the command from the worksheet, then Windows: press Ctrl+V or right-click · Mac: press Cmd+V, then press Enter.
- *How do I copy results from the Terminal?* Select the text with the mouse first, then Windows: press Ctrl+Shift+C · Mac: press Cmd+C. Or take a screenshot.

**If you see a message like this**

| Message on screen | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` or `error during connect` | Docker is not open | Open Docker Desktop and wait until it says Engine running |
| `no configuration file provided: not found` or `open docker-compose...yml: no such file` | The Terminal is not in the lab folder | Repeat Prep step 4 |
| There is no `BOB RECEIVED` / `BOB DECRYPTED` line yet in Bob's log | Bob is still waiting for the message | Wait 5–10 seconds, then type the `logs bob` command again |
| Results from the old mode are mixed in | You did not shut down the previous mode | Type the two commands in Step 11 and start again |

If you still cannot do it, ask a friend or your instructor.

---

## Before you start: set up your computer (at home, once)

If you already did Weeks 2–6 or 10–12, you have Docker and the ZIP file. Start at **Prep step 4**. But the ZIP must have the folder `week13-e2e-encryption`. If you cannot find it, download the ZIP again as in Prep step 2.

#### Prep step 1 — Open Docker Desktop

**What to do:** If you do not have it yet, install it from <https://www.docker.com/products/docker-desktop/> and leave the program open.

**You should see:** the Docker Desktop window says **Engine running**.

#### Prep step 2 — Download the lab files

**What to do:** Open <https://github.com/nutthakorn7/security-cryptography>, click the green **Code** button, and choose **Download ZIP**. You do not need a GitHub account and you do not need to fork.

#### Prep step 3 — Unzip the ZIP file

**What to do:** Windows: right-click the ZIP file and choose **Extract All** · Mac: double-click the ZIP file.

**You should see:** a folder called `security-cryptography-master`. Some computers make a folder with the same name inside it; open it until you can see the `labs` folder.

#### Prep step 4 — Open a Terminal inside the lab folder

**What to do:** Inside the `security-cryptography-master` folder, open `labs` and then open `week13-e2e-encryption`

- **Windows:** open the `week13-e2e-encryption` folder in File Explorer, right-click an empty spot, and choose **Open in Terminal** (if you do not see it, hold Shift, right-click, and choose **Open PowerShell window here**)
- **Mac:** open the Terminal app, type `cd` and one space, drag the `week13-e2e-encryption` folder into the window, then press Enter

Check that you are in the right place with this command:

```bash
ls
```

**You should see:** `alice.py` and `docker-compose.vulnerable.yml` in the list.

#### Prep step 5 — Build the lab image

**Type:**

```bash
docker compose -f docker-compose.vulnerable.yml build
```

**You should see:** a line ending in `Built` or `Building ... done`. The first time you need the internet and it may take several minutes. Do not close the window while you wait.

---

## Part A — The lab (both forms, 60 points)

There are three characters (programs in Docker). Do A1 → A2 → A3 one after the other:

| Character | What it does |
|---|---|
| **Alice** | The sender. She sends the secret message `meet at pier 39 at midnight` to Bob through the server |
| **Server** | The provider. It receives and stores the message, and writes what it received to its log as `SERVER SAW: ...`. The server's code is **the same in every mode** |
| **Bob** | The receiver. He fetches the message from the server |

> **If you really cannot use Docker:** tell your instructor, then copy the example lines in the worksheet into your answer sheet and write "from the worksheet example" next to them. You can answer Steps 3, 6, 8, 9 and 10 by reading the worksheet.

### A1 — The server can read the message (HTTPS only) (20 points)

#### Step 1 — Read: the first mode has no E2EE

**What to do:** Just read. You do not need to type anything.

In this first mode Alice sends the **readable message** to the server (like an app that uses HTTPS on the way). The server receives it, stores it, and writes it to its log, just as a real provider can, so it sees every message, whether or not the connection on the way is encrypted.

#### Step 2 — Run the HTTPS-only mode and see what the server sees

**What to do:** Start the server, Alice and Bob, let Alice send the message, then look at the server's log and Bob's log.

**Type** one line at a time:

```bash
docker compose -f docker-compose.vulnerable.yml up -d --build
docker compose -f docker-compose.vulnerable.yml logs server
docker compose -f docker-compose.vulnerable.yml logs bob
```

**You should see:** the first command prints three lines with `Started`. Find these two lines in the logs (the server's log has other lines mixed in)

```
week13-server  | SERVER SAW: meet at pier 39 at midnight
week13-bob  | BOB RECEIVED: meet at pier 39 at midnight
```

**Means:** the server sees the **readable** message (`SERVER SAW: meet at pier 39 at midnight`). Bob receives the same message. The provider (and anyone who can reach the server's log) can read the secret.

**✍️ Write in the answer sheet (Step 2):** copy the two lines above from your own screen

#### Step 3 — Summarise in your own words

**What to do:** Fill in the blanks.

> In this mode ________ can read the secret (Choose: `the server` / `only Bob`), and even if the connection uses HTTPS the answer does not change, because the server is the ________ of that connection (Choose: `end point` / `go-between`)

**✍️ Write in the answer sheet (Step 3):** write the full sentence

### A2 — Encrypted on Alice's computer (E2EE), the server cannot read (20 points)

#### Step 4 — Read: the E2EE mode

**What to do:** Just read. You do not need to type anything.

In the second mode Bob makes a key pair (a public key and a private key) and **gives the public key to the server to hand out**. Alice fetches Bob's public key and **encrypts the message on her own computer** before sending. The server sees only encrypted data (ciphertext). Bob uses his private key, which never leaves his computer, to decrypt the message. **The server's code did not change at all.** Only what Alice sends changed.

#### Step 5 — Run the E2EE mode and see what the server sees

**What to do:** Start the new mode, then look at the server's log and Bob's log.

**Type** one line at a time (if the first mode is still running, just carry on; Docker will switch for you):

```bash
docker compose -f docker-compose.fixed.yml up -d --build
docker compose -f docker-compose.fixed.yml logs server
docker compose -f docker-compose.fixed.yml logs bob
```

**You should see:** in the output, a `SERVER SAW:` line followed by very long letters (base64, unreadable) and Bob's line, which is readable (your base64 letters will not be the same as the example)

```
week13-server  | SERVER SAW: eyJlbmNfa2V5IjogIlFsUWxzL1dkbEcxT0RFUDNkVVN5YllHb2xsTVR3aVNtamg0Qm...
week13-bob  | BOB DECRYPTED: meet at pier 39 at midnight
```

**Means:** the server sees only unreadable data (there is no `meet at pier 39` in `SERVER SAW:`), but Bob decrypts it and gets the whole original message.

**✍️ Write in the answer sheet (Step 5):** copy the two lines above from your own screen (for the `SERVER SAW:` line, copy about the first 60 characters and add `...`)

#### Step 6 — Answer the two questions

**What to do:** Fill in the blanks in both items (hint: Step 4 and the result in Step 5).

> a) The message is encrypted on ________ (Choose: `Alice's computer` / `the server`) before it is sent.
>
> b) The server's log has no ________ (Choose: `readable message` / `encrypted message`), but Bob can still read the message, because he has a ________ (Choose: `private key` / `public key`) that never left his computer.

**✍️ Write in the answer sheet (Step 6):** write both sentences in full

### A3 — Where the difference is, and what the lab does not prove (20 points)

#### Step 7 — Find the lines that differ in Alice's code

**What to do:** Look at the two lines where Alice chooses what to send to the server.

**Type:**

```bash
docker compose -f docker-compose.fixed.yml run --rm --entrypoint grep alice -n "payload = " alice.py
```

**You should see:** two lines (the line numbers may differ a little)

```
72:        payload = hybrid_encrypt(bob_public_key, SECRET_MESSAGE.encode())
76:        payload = SECRET_MESSAGE
```

**Means:** in the first line (E2EE mode) Alice **encrypts with Bob's public key first** and then sends. The second line (the first mode) sends the **readable message** directly. The difference is on Alice's side, not on the server.

**✍️ Write in the answer sheet (Step 7):** copy the two lines that appear on the screen

#### Step 8 — Summarise in your own words

**What to do:** Look at the result of Step 7 and fill in the blanks.

> The server's code is ________ (Choose: `the same` / `different`) in the two modes. What is different is that Alice sends ________ (Choose: `the encrypted message` / `the readable message`) in the E2EE mode

**✍️ Write in the answer sheet (Step 8):** write the full sentence

#### Step 9 — What this lab does not prove

**What to do:** Read, then fill in the blanks.

In this lab Alice **trusts** that the public key the server gives her is really Bob's. If the server is dishonest, it can quietly swap in its own key, and Alice will encrypt the message so the **server** can read it, without knowing (like the fake certificate in Week 12). So this lab proves only that an **honest server** cannot read the message. It does not prove that the key you received really belongs to Bob.

> If the server swaps Bob's public key for its own, Alice's message can be read by ________ (Choose: `the server` / `nobody`). This problem is called verifying the ________ of the key (Choose: `owner` / `speed`)

**✍️ Write in the answer sheet (Step 9):** write the full sentence

#### Step 10 — How do you defend against it?

**What to do:** Read, then answer in 1–2 sentences.

Real apps such as Signal let users compare a **"safety number"** or scan each other's QR code, without going through the server, to confirm that the key belongs to the right person.

> Why does comparing a safety number outside the server help catch a server that swapped the key? (hint: Step 9)

**✍️ Write in the answer sheet (Step 10):** write your answer

#### Step 11 — Shut down the lab and check your answer sheet

**What to do:** Do this after you have copied all the results (these two commands remove the containers that are still running).

**Type** one line at a time:

```bash
docker compose -f docker-compose.vulnerable.yml down
docker compose -f docker-compose.fixed.yml down
```

**You should see:** a line ending in `Removed`. Then check that your answer sheet has everything: Steps 2, 3 (A1), Steps 5, 6 (A2), Steps 7, 8, 9, 10 (A3). Then do the part for your own form: odd IDs do Part 3 and Part 4, even IDs do Part 2.

---

## Part 1 — Student Information

| Name | Student ID | Date | Group (your form) | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

## Part 2 — Conventional form (40 points; only if Conventional is your assigned form)

Answer each item in 2–3 sentences. You may answer in English or Thai. In this part **answer by yourself**, without using AI to answer.

**Q1 (10). HTTPS is not enough.** Answer all three of these (1–2 sentences each):

- In Step 2 the connection may use HTTPS. Why can the server still read the message? (hint: Steps 1 and 3)
- Who does HTTPS protect the message from, and who does it not protect it from?
- Besides the log, where else can the provider read messages (for example the server's database), and what does the server do with the messages it receives?

**Q2 (10). How is E2EE different?** Answer all three of these (1–2 sentences each):

- What does Alice do before sending the message in the E2EE mode, and whose key does she use? (hint: Steps 4 and 7)
- Why can the server, which stores the messages and writes them to its log, still not read them? (hint: Step 5)
- Why can Bob still read it? (where is the private key?)

**Q3 (10). Is the key really Bob's?** Answer all three of these (1–2 sentences each):

- In the lab, where does Alice get Bob's public key from? (hint: Step 9)
- If the server is dishonest, what can it do with that key, and what is the result?
- Give one example of a defence (for example a safety number or a QR code compared outside the server) (hint: Step 10)

**Q4 (10). Where is Signal better than PGP?** Answer both of these (2–3 sentences each): why is PGP hard for ordinary people to use (for example it is hard to find the other person's key and you have to manage the keys yourself), and how does a Signal-style app help ordinary users (it manages the keys automatically, checks keys with a safety number, and keeps changing keys so old messages stay safe even if a new key leaks)

### Going further (optional — no marks)

- **Q5 — Why is encrypted email not widespread?** The limits of PGP/S/MIME (finding keys, the surrounding data that can still be seen), and what you would change if you designed email again
- **Q6 — Open problems of E2EE.** Choose one: group messaging, syncing keys across several devices, or Key Transparency, with the trade-offs between security and ease of use
- **Q7 — Double Ratchet.** What forward secrecy and post-compromise recovery are, and what their limits are (for example if the end device is seized)

---

## Part 3 — AIR-Sec Arm: Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

An AI wrote a "secure chat backend" for you. It looks professional, but it is **the first mode of this lab**.

> **AI's answer:**
>
> ```python
> @app.post("/send")                       # served over https://
> def send():
>     msg = request.json["message"]        # plaintext message from the sender
>     db.execute("INSERT INTO messages (sender, recipient, body) VALUES (?, ?, ?)",
>                (request.json["from"], request.json["to"], msg))
>     log.info("stored message from %s: %s", request.json["from"], msg)
>     return {"ok": True}
> ```
>
> "Secure: every request travels over HTTPS/TLS. Because we use industry-standard TLS, this is end-to-end encrypted."
>
> — end of AI answer —

1. **Find what's wrong (10).** Copy the wrong line and explain in 2–3 sentences who can read the message even though HTTPS is used (hint: Step 2)
2. **Fix it (10).** Why is the sentence "we use TLS, so it is end-to-end" wrong, and how would you change the design so that the provider cannot read the message? (hint: Step 7)

> Disclose any other AI use in the Part 1 table. This task counts toward the **Audit the AI** row.

---

## Part 4 — Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** A friend asks: *"My chat uses HTTPS, so my messages are already private. Why do I need end-to-end?"* Explain in 4–6 sentences, **without difficult words**: what HTTPS protects and does not protect, what E2EE adds, and the risk that is still left (a seized device).

**B. Prompt Problem (10).** Use any AI you like and do this:

1. Write **one** prompt asking the AI to explain the difference between an HTTPS chat and an end-to-end chat.
2. Copy the AI's answer into your answer sheet.
3. Check: (a) does it say correctly where the plaintext is in each kind? (b) does it say what each protects against: HTTPS stops people listening on the way, E2EE also stops the provider? (c) does it say anything wrong or make anything up (for example "HTTPS is already end-to-end")?
4. In the table in your answer sheet, tick **pass / fail** for each item with a one-sentence reason, then finish with one sentence saying whether you would trust this AI's answer, and why.

Submit **your prompt + the AI's answer + your check table with your own reasons**.

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "In Step 5 the server's code is exactly the same. Why is the message readable in the log of the first mode but not in the second? Where does the difference come from?"
2. "What key does Alice encrypt with, and why can the server, which hands out that key, still not decrypt it?"
3. "A friend says this lab proves that Alice is really talking to Bob. Is that true? What does the lab prove and what does it not prove?"

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — the server can read the message (HTTPS only) | 20 | 20 |
| A2 — E2EE, the server cannot read | 20 | 20 |
| A3 — the difference and the limits + reasoning | 20 | 20 |
| Conventional written questions (Q1–Q4) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- Put your name, student ID and date in the answer sheet, and copy the commands and results from **your own** computer. The secret message is the same for everyone (it is a fixed value of the lab). What makes the work yours is the results copied from your own computer. It is normal that your random base64 letters are not the same as a friend's. Do not submit a friend's results as your own.
- **Explain in your own words** (marks are given for the reasoning): for the fill-in-the-blank items that give you a word bank (Steps 3, 6, 8, 9) you may use the words given. The short answer in Step 10 and the written part of your own form must be in your own words (why the server can read the message even though HTTPS is used, why E2EE stops that, and what the lab does not prove). You do not need to write anything more than that.

**Deadline and late submission:** Submit by 23:59 (Thai time) on **Sunday 31 Jan 2027** (KOSEN rule: before the next class). A late submission loses 10% of this worksheet's marks for each day late (a part day counts as a day), down to 0. Uploading or replacing a file after the deadline counts the whole submission as late. Submit the common 60 marks and **one** form of your own only; doing both forms gives no extra marks. The viva is used to check understanding and has no separate marks.
