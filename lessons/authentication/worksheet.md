# Worksheet 14 — User Authentication: the server sees your password (unless it can't)

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** NIST SP 800-63B · OWASP Authentication / Credential Stuffing Cheat Sheets · CWE-522 (Insufficiently Protected Credentials), CWE-532 (Sensitive Information in a Log File). The demo uses HTTP on an isolated Docker network; CWE-319 applies to that unencrypted transport, not to a server that receives the plaintext after TLS ends.
> **Kind:** Docker lab, step by step. No programming and no maths. The concept questions (TOTP, FIDO2, SSO) stay on paper this week.

> **Ethics note:** Only work on the containers on your own computer that this lab starts (a pretend login server and a pretend client). The lesson is "who gets to see your password?" Capturing other people's passwords on a system that is not yours and without permission is illegal.

## Read this first

**What you will do today:** When you log in to a website, your password travels to the **server**. HTTPS (TLS) hides it from people listening on the way, but the server is the end of that connection, so the server **decrypts it and can log it, store it or leak it**. We will start a pretend login server that does exactly that and watch it write your password in its log. Then we will switch on a **challenge-response** login, where the client proves it knows the password **without sending it**, and see that the login still works while the password is not in the server's log. Remember this: **HTTPS protects the password on the way, not from the server.**

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
- Then do **only your own form (40 marks)**. Look at the last digit of your student ID: **odd = Conventional (Part 2)**, **even = AIR-Sec (Parts 3–4)** (0 counts as even). Write your form in the Group box.
- You may answer in English or Thai. Short and clear is enough.
- **Answer sheet:** in Classroom → Week 14, open the file for your form (`Wk14_Answer_Sheet_Conventional` or `Wk14_Answer_Sheet_AIR-Sec`), choose Open with → Google Docs, type in the grey boxes, then choose File → Download → PDF.
- Submit one file named with your student ID, for example `Wk14_66990000.pdf` (do not type the `<` `>` signs), at `learn.zcr.ai/submit` with your Week 14 submission code from your KMITL email, by **Sunday 7 Feb 2027, 23:59**.
- Items marked *optional* have no marks. You can skip them.

| Part A | Marks | Steps to write in the answer sheet |
|---|---:|---|
| A1 — the server sees the password (plain login) | 20 | Steps 2, 3 |
| A2 — challenge-response: the password is never sent | 20 | Steps 5, 6 |
| A3 — where the difference is, and what the demo does not prove | 20 | Steps 7, 8, 9, 10 |

**Words you need to know**

| Word | Simple meaning |
|---|---|
| Terminal | A window where you type commands |
| Docker / container | A program that starts a small "pretend computer" on your computer. If you break it, delete it and start again |
| server | The computer you log in to. It checks your password and answers yes or no |
| log | A record of what a program did, which the system administrator can read |
| TLS (HTTPS) | Encrypts the connection between you and the server, but the server is the end of that connection, so it sees what you sent |
| nonce | A fresh random number that the server gives out **once**. It is different every time |
| proof | A short answer the client makes by mixing the nonce with something made from the password. The server can check it, but it is not the password |
| verifier | A scrambled version of the password that the server stores instead of the password itself |
| replay | Recording a login and sending it again later to log in as someone else |

**Questions people often ask**

- *Do I need to be good at maths?* No.
- *Do I need to write programs?* No. Copy the commands and paste them.
- *If I make a mistake, will my computer break?* No. Everything is inside containers. If you get confused, type the command in Step 11 and start again.
- *Can I skip understanding every line on the screen?* Yes. Only look at the lines the worksheet tells you to.
- *My nonce and proof letters are not the same as my friend's. Is that wrong?* No. They are random every time. Only the shape of the line must be the same.
- *How do I paste a command into the Terminal?* Copy the command from the worksheet, then Windows: press Ctrl+V or right-click · Mac: press Cmd+V, then press Enter.
- *How do I copy results from the Terminal?* Select the text with the mouse first, then Windows: press Ctrl+Shift+C · Mac: press Cmd+C. Or take a screenshot.

**If you see a message like this**

| Message on screen | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` or `error during connect` | Docker is not open | Open Docker Desktop and wait until it says Engine running |
| `no configuration file provided: not found` or `open docker-compose...yml: no such file` | The Terminal is not in the lab folder | Repeat Prep step 4 |
| There is no `LOGIN OK` line yet in the client's log | The client has not finished yet | Wait 5–10 seconds, then type the `logs client` command again |
| Results from the old mode are mixed in | You did not shut down the previous mode | Type the command in Step 11 and start again |

If you still cannot do it, ask a friend or your instructor.

---

## Before you start: set up your computer (at home, once)

If you already did Weeks 2–6 or 10–13, you have Docker and the ZIP file. Start at **Prep step 4**. But the ZIP must have the folder `week14-authentication`. If you cannot find it, download the ZIP again as in Prep step 2.

#### Prep step 1 — Open Docker Desktop

**What to do:** If you do not have it yet, install it from <https://www.docker.com/products/docker-desktop/> and leave the program open.

**You should see:** the Docker Desktop window says **Engine running**.

#### Prep step 2 — Download the lab files

**What to do:** Open <https://github.com/nutthakorn7/security-cryptography>, click the green **Code** button, and choose **Download ZIP**. You do not need a GitHub account and you do not need to fork.

#### Prep step 3 — Unzip the ZIP file

**What to do:** Windows: right-click the ZIP file and choose **Extract All** · Mac: double-click the ZIP file.

**You should see:** a folder called `security-cryptography-master`. Some computers make a folder with the same name inside it; open it until you can see the `labs` folder.

#### Prep step 4 — Open a Terminal inside the lab folder

**What to do:** Inside the `security-cryptography-master` folder, open `labs` and then open `week14-authentication`

- **Windows:** open the `week14-authentication` folder in File Explorer, right-click an empty spot, and choose **Open in Terminal** (if you do not see it, hold Shift, right-click, and choose **Open PowerShell window here**)
- **Mac:** open the Terminal app, type `cd` and one space, drag the `week14-authentication` folder into the window, then press Enter

Check that you are in the right place with this command:

```bash
ls
```

**You should see:** `client.py` and `docker-compose.vulnerable.yml` in the list.

#### Prep step 5 — Build the lab image

**Type:**

```bash
docker compose -f docker-compose.vulnerable.yml build
```

**You should see:** a line ending in `Built` or `Building ... done`. The first time you need the internet and it may take several minutes. Do not close the window while you wait.

---

## Part A — The lab (both forms, 60 points)

There are two characters (programs in Docker). Do A1 → A2 → A3 one after the other:

| Character | What it does |
|---|---|
| **Server** | The login server. It knows one account, `alice`. It writes what it receives to its log (lines starting with `SERVER SAW`) |
| **Client** | Logs in as `alice` with the password `correct-horse-battery` (a pretend password that is the same for everyone) and prints `LOGIN OK` when it succeeds |

> **If you really cannot use Docker:** tell your instructor, then copy the example lines in the worksheet into your answer sheet and write "from the worksheet example" next to them. You can answer Steps 3, 6, 8, 9 and 10 by reading the worksheet.

### A1 — The server sees the password (plain login) (20 points)

#### Step 1 — Read: the first mode sends the password

**What to do:** Just read. You do not need to type anything.

In this first mode the client logs in the way most websites do: it puts the **actual password** in the login request. The server receives it, checks it, and (like a server that logs too much, or one that has been hacked) writes it in its log. HTTPS would hide the request from people on the network, but the server is the end of the connection, so it still sees the password.

#### Step 2 — Run the plain login and see what the server sees

**What to do:** Start the server and the client, let the client log in, then look at the server's log and the client's log.

**Type** one line at a time:

```bash
docker compose -f docker-compose.vulnerable.yml up -d --build
docker compose -f docker-compose.vulnerable.yml logs server
docker compose -f docker-compose.vulnerable.yml logs client
```

**You should see:** the first command prints lines with `Started`. Find these lines in the logs (the server's log has other lines mixed in)

```
week14-server  | SERVER SAW PASSWORD: correct-horse-battery
week14-client  | LOGIN OK
```

**Means:** the server's log contains the **password in plaintext** (`SERVER SAW PASSWORD: correct-horse-battery`), and the login worked (`LOGIN OK`). Anyone who can read the server's log, or who runs the server, now has the password.

**✍️ Write in the answer sheet (Step 2):** copy the two lines above from your own screen

#### Step 3 — Summarise in your own words

**What to do:** Fill in the blanks.

> The line `SERVER SAW PASSWORD` was printed by the ________ (Choose: `server` / `client`). Even if the connection used TLS, this line would ________ (Choose: `still appear` / `disappear`), because the server is the ________ of the TLS connection (Choose: `end point` / `go-between`)

**✍️ Write in the answer sheet (Step 3):** write the full sentence

### A2 — Challenge-response: the password is never sent (20 points)

#### Step 4 — Read: the second mode proves it without sending

**What to do:** Just read. You do not need to type anything.

In the second mode the client first asks the server for a **nonce** (a fresh random number). Then the client mixes the nonce with a scrambled version of the password (made on its own computer) and sends back only the nonce and the result, called the **proof**. The server never receives the password. It stores only the scrambled version, the **verifier**, mixes it with the same nonce itself, and checks that its answer is the same as the proof.

#### Step 5 — Run the challenge-response login and see what the server sees

**What to do:** Start the new mode, then look at the server's log and the client's log.

**Type** one line at a time (if the first mode is still running, just carry on; Docker will switch for you):

```bash
docker compose -f docker-compose.fixed.yml up -d --build
docker compose -f docker-compose.fixed.yml logs server
docker compose -f docker-compose.fixed.yml logs client
```

**You should see:** in the server's log a `SERVER SAW:` line with a nonce and a proof (your letters and numbers will not be the same as the example), and in the client's log `LOGIN OK`

```
week14-server  | SERVER SAW: nonce=cafdff0da9a153f6929987166fb305c8 proof=e2c3481fe4a6405455ed194bc4cb4f053b094a4123875054069de40b71df4e08
week14-client  | LOGIN OK
```

**Means:** the login worked (`LOGIN OK`), but this time the server saw only a nonce and a proof. Read through the **server's** lines: you must **not** find `correct-horse-battery` or `SERVER SAW PASSWORD` anywhere. (That this run's log has no password does not by itself prove that the password was never sent. Step 7 will let you check the client's code.)

**✍️ Write in the answer sheet (Step 5):** copy the two lines above from your own screen, and write whether the server's log contains the password or not

#### Step 6 — Answer the two questions

**What to do:** Fill in the blanks in both items (hint: Step 4 and the result in Step 5).

> a) In this mode the client sends the nonce and a ________ (Choose: `proof` / `password`) instead of the password.
>
> b) Someone who records this exchange cannot use it to log in again later, because the next login uses a new ________ (Choose: `nonce` / `username`).

**✍️ Write in the answer sheet (Step 6):** write both sentences in full

### A3 — Where the difference is, and what the demo does not prove (20 points)

#### Step 7 — Find the lines that differ in the client's code

**What to do:** Look at the two lines where the client builds the login request.

**Type:**

```bash
docker compose -f docker-compose.fixed.yml run --rm --entrypoint grep client -n "USERNAME," client.py
```

**You should see:** two lines (the line numbers may differ a little)

```
85:    status, body = _post_json("/login", {"username": USERNAME, "password": PASSWORD})
111:        {"username": USERNAME, "nonce": nonce.hex(), "proof": proof.hex()},
```

**Means:** in the first line (the first mode) the client puts the **password** in the request. In the second line (the second mode) it puts the **nonce and the proof** and no password. The difference is in what the client sends.

**✍️ Write in the answer sheet (Step 7):** copy the two lines that appear on the screen

#### Step 8 — Summarise in your own words

**What to do:** Look at the result of Step 7 and fill in the blanks.

> In the first mode the login request contains the ________ (Choose: `password` / `proof`). In the second mode it contains the ________ and the nonce (Choose: `proof` / `password`)

**✍️ Write in the answer sheet (Step 8):** write the full sentence

#### Step 9 — What this demo does not prove

**What to do:** Read, then fill in the blanks.

This second mode is a **simplified** challenge-response. It shows only that the login request does not carry the password. It is **not a real PAKE** (a protocol designed for password logins). Three limits:

- The verifier that the server stores works like a password: someone who **steals the verifier** can make a correct proof and log in as Alice.
- Someone who records a nonce and proof, and knows the salt, can **guess passwords offline** and check each guess.
- The client never checks that it is talking to the real server (there is no mutual authentication).

> If a thief steals the server's stored verifier, they ________ (Choose: `can` / `cannot`) log in as `alice`, because the verifier is enough to make a correct ________ (Choose: `proof` / `nonce`)

**✍️ Write in the answer sheet (Step 9):** write the full sentence

#### Step 10 — What does a real PAKE add?

**What to do:** Read, then answer in 1–2 sentences.

A real PAKE (for example OPAQUE, [RFC 9807](https://www.rfc-editor.org/rfc/rfc9807.html)) is built so that the two sides end up with a **shared key** and **both** are sure who they are talking to, and so that watching the exchange does not let an attacker test guesses offline.

> Name **one** thing a real PAKE gives that this demo does not (hint: Step 9). Say in your own words why the demo does not have it.

**✍️ Write in the answer sheet (Step 10):** write your answer

#### Step 11 — Shut down the lab and check your answer sheet

**What to do:** Do this after you have copied all the results. Both modes belong to one lab, so one command removes everything.

**Type:**

```bash
docker compose -f docker-compose.fixed.yml down
```

**You should see:** lines ending in `Removed`. (If you stopped in the middle of the first mode and never started the second, type the same command with `docker-compose.vulnerable.yml`.) Then check that your answer sheet has everything: Steps 2, 3 (A1), Steps 5, 6 (A2), Steps 7, 8, 9, 10 (A3). Then do the part for your own form: odd IDs do Part 2; even IDs do Parts 3 and 4.

---

## Part 1 — Student Information

| Name | Student ID | Date | Group (your form) | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

## Part 2 — Conventional form (40 points; only if Conventional is your assigned form)

Answer each item in 2–3 sentences. You may answer in English or Thai. In this part **answer by yourself**, without using AI to answer.

**Q1 (10). TLS is not enough.** Answer all three of these (1–2 sentences each):

- In Step 2 the connection could have used TLS. Why would the server still print the password? (hint: Steps 1 and 3)
- Name **three different ways** the plaintext password can be exposed once the server has it.
- What does TLS protect the password from, and what does it not protect it from?

**Q2 (10). What does challenge-response do differently?** Answer all three of these (1–2 sentences each):

- What travels in the login request in each mode? (hint: Steps 2, 5 and 7)
- Why can an attacker who records one nonce and proof not use them to log in again later? (hint: Step 6)
- How does the server decide that the proof is right, without having the password? (hint: Step 4)

**Q3 (10). The limits of the demo.** Answer all three of these (1–2 sentences each):

- Why is a stolen verifier a problem in this demo, and why can a recorded exchange still allow offline guessing? (hint: Step 9)
- Name two things a real PAKE adds that this demo does not.
- Does a PAKE such as OPAQUE make offline guessing impossible if the **whole server** is hacked? Explain what it does and does not promise ([RFC 9807, Sections 1 and 10.11](https://www.rfc-editor.org/rfc/rfc9807.html#section-10.11)).

**Q4 (10). Phishing and the second factor.** Answer both of these (2–3 sentences each): how does TOTP (an authenticator app) work, and why can a lookalike website relay a TOTP code to the real site? Why does a correctly built FIDO2 / WebAuthn sign-in resist this kind of phishing? (hint: what the user types, and what each method is bound to)

### Going further (optional — no marks)

- **Q5 — The three factors.** What is the difference between something you *know*, *have* and *are*? Give one example and one weakness of each.
- **Q6 — Credential stuffing.** What is it, which single control most reduces the damage, and why does it help even when the leaked passwords are correct?
- **Q7 — Storing passwords (Week 2).** Why should the server store a slow, salted hash (bcrypt or argon2) and not a fast hash? What does the salt stop, and what does the slow work stop? (Note: this lab uses a fast salted hash only to keep the demo short.)
- **Q8 — SSO.** What does signing in through an identity provider (OpenID Connect) give you, and what new risk does it create? How is OpenID Connect different from OAuth 2.0?

---

## Part 3 — AIR-Sec form: Audit the AI (AIR-Sec only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

An AI wrote a login handler "with good logging for debugging". It logs users in correctly, and the way it checks the password (`bcrypt.checkpw` against `pw_hash`) is **correct**. The flaw is somewhere else.

> **AI's answer:**
>
> ```python
> import logging
> logging.basicConfig(level=logging.INFO)
> log = logging.getLogger("auth")
>
> @app.post("/login")
> def login():
>     body = request.get_json(force=True)
>     # Log the full request so we can debug failed logins in production.
>     log.info("login attempt: %s", body)           # <-- (A)
>     user = users.get(body["username"])
>     if user and bcrypt.checkpw(body["password"].encode(), user.pw_hash):
>         log.info("login OK for %s", body["username"])
>         return {"status": "ok"}
>     log.warning("login FAILED for %s (pw=%s)", body["username"], body["password"])  # <-- (B)
>     return {"status": "denied"}, 401
> ```
>
> — end of AI answer —

1. **Find what's wrong (10).** Name the flaw (and its CWE if you can). Point to lines (A) and (B): what is written to the logs, and who can read production logs? (hint: Step 2)
2. **Fix it (10).** Rewrite the two logging lines so you can still tell **that** a login failed and **for which username**, without logging the password or the raw body. Then say in one sentence how this is the same mistake as the first mode of the lab. (hint: Step 3)

> Disclose any other AI use in the Part 1 table. This task counts toward the **Audit the AI** row.

---

## Part 4 — Comprehension & Prompt (AIR-Sec only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** In the second mode the client proves it knows the password **without sending it**. Explain this to someone who has never taken a crypto course, in 4–6 sentences, **without difficult words**: how can you convince a doorman you know the day's password without saying it out loud? Why can the server check your answer without storing the password, and why can a recording not be used tomorrow? Then name **one** thing a real PAKE protects against that this demo does not.

**B. Prompt Problem (10).** Use any AI you like and do this:

1. Write **one** prompt like: "How should I securely handle user login so the server never learns the user's password?"
2. Copy the AI's answer into your answer sheet.
3. Check: (a) does it say HTTPS is not enough because the server still sees the plaintext? (b) does it name a real mechanism (SRP, OPAQUE, WebAuthn) without making up a protocol or an RFC? (c) does it avoid calling client-side hashing a PAKE, and avoid saying a fully hacked server can never test guesses? (d) does it say to store a slow, salted hash?
4. In your answer sheet, tick **pass / fail** for each item with a one-sentence reason, then say in one sentence whether you would trust this AI's answer, and why.

Submit **your prompt + the AI's answer + your check table with your own reasons**.

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "In the first mode the server prints the password. If the whole connection had been wrapped in TLS, would that line still appear? Why, or why not?"
2. "In the second mode the server never has the password. Walk me through how it decides the login is valid. What does it compare?"
3. "A friend says the second mode is a real PAKE. Is it? Give me one situation where this demo fails and a real PAKE would not."

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — the server sees the password (plain login) | 20 | 20 |
| A2 — challenge-response, the password is not sent | 20 | 20 |
| A3 — the difference and the limits + reasoning | 20 | 20 |
| Conventional written questions (Q1–Q4) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- Put your name, student ID and date in the answer sheet, and copy the commands and results from **your own** computer. The password in this lab is the same for everyone (it is a fixed value of the lab). What makes the work yours is the results copied from your own computer. It is normal that your nonce and proof letters are not the same as a friend's. Do not submit a friend's results as your own.
- **Explain in your own words** (marks are given for the reasoning): for the fill-in-the-blank items that give you a word bank (Steps 3, 6, 8, 9) you may use the words given. The short answer in Step 10 and the written part of your own form must be in your own words (who ended up with the plaintext password and why TLS did not prevent it, what the client sent instead of the password and why a recording cannot be replayed, and what the demo does not prove). You do not need to write anything more than that.

**Deadline and late submission:** Submit by 23:59 (Thai time) on **Sunday 7 Feb 2027** (KOSEN rule: before the next class). A late submission loses 10% of this worksheet's marks for each day late (a part day counts as a day), down to 0. Uploading or replacing a file after the deadline counts the whole submission as late. Submit the common 60 marks and **one** form of your own only; doing both forms gives no extra marks. The viva is used to check understanding and has no separate marks.
