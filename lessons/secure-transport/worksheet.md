# Worksheet 12 — Secure Transport (TLS): "encrypted" is not the same as "encrypted to the right person"

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** RFC 9846 (TLS 1.3), RFC 5280 (X.509), RFC 9525 (hostname verification) · CWE-295 (Improper Certificate Validation), CWE-300 (Channel Accessible by Non-Endpoint)
> **Kind:** Docker lab, step by step. No maths. There is a short code fix of **3 lines**, and an example of the right lines is given

> **Ethics note:** Only work on the containers on your own computer that this lab starts (Alice, Bob and the pretend impostor "Eve", who is simulated code). Listening in on, or pretending to be, a server on a real network that is not yours and that you have no permission to test is illegal.

## Read this first

**What you will do today:** Alice sends a secret to Bob over TLS (an encrypted connection), but someone in the middle (Eve) hands Alice a **fake certificate that claims to be "bob"**. If Alice **does not check the certificate**, she talks to Eve with perfect encryption, and Eve can read the secret. You will see Alice both without checking and with checking, and then **fix Alice's code yourself**. Remember this: **encrypted does not mean you are talking to the right person**.

**Every step is written the same way:**

| Heading | Meaning |
|---|---|
| **What to do** | Says what this step does |
| **Type** | Copy the whole line, paste it into the Terminal, and press Enter |
| **You should see** | The screen should look roughly like this (other Docker lines are mixed in; only look at the lines the worksheet tells you to) |
| **Means** | What the result means |
| **Write in the answer sheet** | What to copy or write in your answer sheet |

**Marks**

- Everyone does **Part A (60 marks)**, which is the same for both forms.
- Then do **only your own form (40 marks)**. Look at the last digit of your student ID: **odd = Conventional (Part 2)**, **even = AIR-Sec (Parts 3–4)** (0 counts as even). Write your form in the Group box.
- You may answer in English or Thai. Short and clear is enough.
- **Answer sheet:** in Classroom → Week 12, open the file for your form (`Wk12_Answer_Sheet_Conventional` or `Wk12_Answer_Sheet_AIR-Sec`), choose Open with → Google Docs, type in the grey boxes, then choose File → Download → PDF.
- Submit one file named with your student ID, for example `Wk12_66990000.pdf` (do not type the `<` `>` signs), at `learn.zcr.ai/submit` with your Week 12 submission code from your KMITL email, by **Sunday 24 Jan 2027, 23:59**.
- **This week you must also attach the commit link of `alice_student.py` on GitHub** (no separate marks). See the W12 section of `SUBMISSION.md` for how, and prepare your fork before class.
- Items marked *optional* have no marks. You can skip them.

| Part A | Marks | Steps to write in the answer sheet |
|---|---:|---|
| A1 — Alice does not check the certificate, so Eve reads the secret | 20 | Steps 2, 3 |
| A2 — Alice checks the certificate, so Eve cannot read it | 20 | Steps 5, 6 |
| A3 — Fix Alice's code yourself, and test it | 20 | Steps 7, 8, 9, 10 |

**Words you need to know**

| Word | Simple meaning |
|---|---|
| Terminal | A window where you type commands |
| Docker / container | A program that starts a small "pretend computer" on your computer. If you break it, delete it and start again |
| TLS | A way to encrypt a connection (the same as the https websites use) |
| certificate | A document from a server that says "I am bob" |
| CA (Certificate Authority) | An issuer that our computer **already trusts**. It signs to say that this certificate really belongs to bob |
| self-signed | A certificate that signs itself. No CA that we trust has signed it. Anyone can make one |
| MITM (man in the middle) | Someone in the middle of the path who pretends to be the destination (in this worksheet, Eve) |
| verify a certificate | Check that the certificate was signed by a CA we trust, and that the name in it matches the name we called |
| flag | A prize message (this week there is no flag, but there is a secret message `the vault code is 7731`) |

**Questions people often ask**

- *Do I need to be good at maths?* No.
- *Do I need to write programs?* You only fix **3 lines** of code, and the worksheet shows you the right lines (Step 7).
- *If I make a mistake, will my computer break?* No. Everything is inside containers. If you get confused, type the three commands in Step 11 and start again.
- *Can I skip understanding every line on the screen?* Yes. Only look at the lines the worksheet tells you to.
- *The container names and numbers on my screen are not the same as the example. Is that wrong?* No. The secret message and the important lines (`MITM INTERCEPTED`, `CERT VERIFICATION FAILED`) must be the same.
- *How do I paste a command into the Terminal?* Copy the command from the worksheet, then Windows: press Ctrl+V or right-click · Mac: press Cmd+V, then press Enter.
- *How do I copy results from the Terminal?* Select the text with the mouse first, then Windows: press Ctrl+Shift+C · Mac: press Cmd+C. Or take a screenshot.

**If you see a message like this**

| Message on screen | Cause | Fix |
|---|---|---|
| It has `Cannot connect to the Docker daemon` or `error during connect` | Docker is not open | Open Docker Desktop and wait until it says Engine running |
| `no configuration file provided: not found` or `open docker-compose...yml: no such file` | The Terminal is not in the lab folder | Repeat Prep step 4 |
| `NotImplementedError: TODO: build_client_context()` | You have not fixed `alice_student.py` yet, or you did not save the file | Do Step 8, then Save |
| `IndentationError` or `SyntaxError` | The lines you typed are not indented correctly | Every line must be indented **4 spaces**, the same as the other lines in the function |
| The result is still the old one even though you changed the file | You did not put `--build` in the command | Copy the command in Step 9 again, the whole line (it has `--build`) |
| `network ... has active endpoints` when you run `down` | A container is still left over | Type the commands in Step 11 again |

If you still cannot do it, ask a friend or your instructor.

---

## Before you start: set up your computer (at home, once)

If you already did Weeks 2–6 or 10–11, you have Docker and the ZIP file. Start at **Prep step 4**. But the ZIP must have the folder `week12-secure-transport`. If you cannot find it, download the ZIP again as in Prep step 2. This week you also need your own **GitHub fork** (see the W12 section of `SUBMISSION.md`)

#### Prep step 1 — Open Docker Desktop

**What to do:** If you do not have it yet, install it from <https://www.docker.com/products/docker-desktop/> and leave the program open.

**You should see:** In the Docker Desktop window it says **Engine running**

#### Prep step 2 — Download the lab files

**What to do:** Open <https://github.com/nutthakorn7/security-cryptography>, click the green **Code** button, and choose **Download ZIP** (or use `git clone` of your own fork if you know how)

#### Prep step 3 — Unzip the ZIP file

**What to do:** Windows: right-click the ZIP file and choose **Extract All** · Mac: double-click the ZIP file

**You should see:** A folder called `security-cryptography-master`. On some computers there is a folder with the same name inside it. Open it until you can see the `labs` folder

#### Prep step 4 — Open a Terminal inside the lab folder

**What to do:** In the folder `security-cryptography-master`, go into `labs`, then go into `week12-secure-transport`

- **Windows:** Open the folder `week12-secure-transport` in File Explorer, right-click an empty spot, and choose **Open in Terminal** (if you do not see this menu, hold Shift, right-click, and choose **Open PowerShell window here**)
- **Mac:** Open the Terminal app, type `cd` and one space, drag the folder `week12-secure-transport` into the window, then press Enter

Check that you are in the right place with this command:

```bash
ls
```

**You should see:** The names `alice_student.py` and `docker-compose.vulnerable.yml` are in the list

#### Prep step 5 — Build the lab image

**Type:**

```bash
docker compose -f docker-compose.vulnerable.yml build
```

**You should see:** A line ending in `Built` or `Building ... done`. The first time it needs the internet and may take several minutes. Do not close the window while it works

---

## Part A — The lab (both forms, 60 points)

There are three characters (programs in Docker):

| Character | What it does | Certificate |
|---|---|---|
| **Alice** | Sends the secret `the vault code is 7731` to "bob" | — (she must decide whether to trust the certificate) |
| **Bob** | The real server | The **real** certificate, signed by a CA |
| **Eve (mitm)** | Sits in the middle and pretends to be bob | A **fake** certificate that she signed herself, but with the name "bob" written in it |

Alice is set up to connect to Eve (because Eve is in the middle), believing that it is bob. Do A1 → A2 → A3 one after another, without shutting down the lab in between.

> **If you really cannot use Docker:** tell your instructor, then copy the example lines in the worksheet into your answer sheet and write "from the worksheet example" next to them. Steps 3, 6 and 10 can be answered by reading the worksheet (Step 8 needs code that you fixed yourself).

### A1 — Alice does not check the certificate, so Eve reads the secret (20 points)

#### Step 1 — Read: what does it mean that Alice does not check the certificate?

**What to do:** Just read. You do not need to type anything.

In this first mode, Alice is set up **not to check the certificate** of the other side (she does not look at who signed it, and she does not look at whether the name matches). So Eve's fake certificate that says "bob" is accepted. The result is that Alice opens a TLS connection with Eve and sends the secret. The data is really encrypted, but it is encrypted to **Eve**, who can decrypt it because she is the end of that connection.

#### Step 2 — Run Alice without checking, and see what Eve gets

**What to do:** Let Alice send the secret, then look at Eve's log.

**Type** one line at a time:

```bash
docker compose -f docker-compose.vulnerable.yml run --rm alice
docker compose -f docker-compose.vulnerable.yml logs mitm
```

**You should see:** The first command shows three lines from Alice. The second command shows Eve's lines. Find these important lines:

```
ALICE: TLS handshake succeeded WITHOUT verifying the server cert -- sending secret
week12-mitm  | MITM INTERCEPTED: the vault code is 7731
```

**Means:** Alice says herself that the TLS handshake **succeeded** (the connection is really encrypted), but she **did not check** the certificate. So Eve could read the secret (`MITM INTERCEPTED`).

**✍️ Write in the answer sheet (Step 2):** copy the two lines above from your own screen.

#### Step 3 — Summarise in your own words

**What to do:** Fill in the blanks.

> Alice's TLS handshake ________ (Choose: `succeeded` / `failed`) and the connection is really encrypted, but Eve could read the secret because Alice did not check the ________ of the other side. (Choose: `certificate` / `speed`)

**✍️ Write in the answer sheet (Step 3):** write the full sentence.

### A2 — Alice checks the certificate, so Eve cannot read it (20 points)

#### Step 4 — Read: Alice with checking

**What to do:** Just read. You do not need to type anything.

In the second mode, Alice loads the **CA that we trust** (the lab's CA) and checks two things: (1) was the certificate signed by that CA? (2) does the name in the certificate match "bob"? Eve's fake certificate has the name "bob" written correctly, but **no CA signed it** (she signed it herself), so it fails check (1) and Alice cuts the connection **before sending the secret**. The attacker and Eve's code did not change at all. Only Alice's side changed.

#### Step 5 — Run Alice with checking, and see what Eve gets

**What to do:** Run Alice with checking, then look at Eve's log.

**Type** one line at a time:

```bash
docker compose -f docker-compose.fixed.yml run --rm alice
docker compose -f docker-compose.fixed.yml logs mitm
```

**You should see:** Find these three lines. Eve's log also still shows the `MITM INTERCEPTED` line from Step 2 higher up (that is the old connection, so ignore it). The new connection must end with `intercepted NOTHING`:

```
CERT VERIFICATION FAILED - ABORTING
ALICE: (reason: self-signed certificate)
week12-mitm  | MITM: handshake aborted by client, intercepted NOTHING (SSLError)
```

**Means:** Alice rejected the certificate because it is **self-signed** (no CA that we trust signed it), even though the name is "bob", and Eve got **nothing at all** (`intercepted NOTHING`).

**✍️ Write in the answer sheet (Step 5):** copy the three lines above from your own screen.

#### Step 6 — Answer the two questions

**What to do:** Fill in the blanks in both items (hint: Step 4 and the result in Step 5).

> a) Eve's fake certificate was rejected because ________ (Choose: `the name does not match` / `no CA that we trust signed it`)
>
> b) Alice cut the connection ________ sending the secret (Choose: `before` / `after`), so nothing leaked.

**✍️ Write in the answer sheet (Step 6):** write both sentences in full.

### A3 — Fix Alice's code yourself, and test it (20 points)

#### Step 7 — Look at the right code

**What to do:** Look at the lines that make the checking Alice work correctly, in the file `alice.py`.

**Type:**

```bash
docker compose -f docker-compose.fixed.yml run --rm --entrypoint grep alice -n -A4 "FIXED: trust only" alice.py
```

**You should see:**

```
80:        # FIXED: trust only the demo CA, verify the chain and the hostname.
81-        ca_path = wait_for_ca_cert()
82-        ctx = ssl.create_default_context(cafile=ca_path)
83-        # create_default_context already sets check_hostname=True and
84-        # verify_mode=CERT_REQUIRED; we keep both.
```

**Means:** The two important lines are 81 and 82. The first finds the lab's CA file. The second builds a checker that trusts only that CA. It checks the chain of signatures and the name automatically.

**✍️ Write in the answer sheet (Step 7):** copy the lines `ca_path = ...` and `ctx = ...` that show on your screen.

#### Step 8 — Fix `alice_student.py` yourself (3 lines)

**What to do:** The file `alice_student.py` is the same as `alice.py` in everything except the function `build_client_context()`, which is not finished. Open the file with any text editor you have (Notepad, TextEdit or VS Code) and do this:

1. Find the function `def build_client_context()` and the line `raise NotImplementedError(` (and the two lines that follow it, up to the `)` sign). **Delete those three lines.**
2. Type these three lines in their place, indented **4 spaces** (the same as the line `# ====== YOUR TASK` above them):

```python
    ca_path = wait_for_ca_cert()
    ctx = ssl.create_default_context(cafile=ca_path)
    return ctx
```

3. Save the file (Save)

**Means:** `wait_for_ca_cert()` gives the location of the lab's CA file, and `create_default_context(cafile=...)` builds a checker that trusts **only that CA** and also checks the name `bob`. You do not need to write the checking yourself.

**✍️ Write in the answer sheet (Step 8):** paste the whole `build_client_context()` function that you fixed (the three lines above and the function heading line).

#### Step 9 — Test in two ways: the impostor, and the real Bob

**What to do:** Test the Alice you fixed against Eve (she must reject) and then against the real Bob (she must accept). If Alice rejects every certificate, she also passes the first test, so you must test with Bob too.

**Type** one line at a time (**you must have `--build`** in the first line, so that Docker uses the file you changed):

```bash
docker compose -f docker-compose.student-task.yml run --rm --build alice
docker compose -f docker-compose.student-task.yml up -d bob
docker compose -f docker-compose.student-task.yml run --rm --no-deps -e PEER_HOST=bob alice
```

**You should see:** The first command shows a rejection and the third command shows success. Find these lines:

```
CERT VERIFICATION FAILED - ABORTING
ALICE: TLS handshake succeeded -- sending secret
```

**Means:** With Eve (the fake certificate), Alice rejects. With Bob (the real certificate signed by the CA), Alice accepts and sends the secret. If you see `Traceback` instead, the code in Step 8 is not right yet. Look at the error table above.

**✍️ Write in the answer sheet (Step 9):** copy the two lines above from your own screen.

#### Step 10 — Why test both ways?

**What to do:** Read, then answer in 1–2 sentences.

The two results together prove that our Alice **accepts the right person** and **rejects the impostor**. But the limit that remains is this: if the CA that we trust signs a fake certificate (because it was hacked or is dishonest), Alice will believe it. This lab does not test that case.

> Why do we need to test both against Eve and against the real Bob, and in what case can an Alice who checks certificates still lose? (hint: Step 9)

**✍️ Write in the answer sheet (Step 10):** write your answer.

#### Step 11 — Shut down the lab and check your answer sheet

**What to do:** Do this after you have copied all your results (these three commands remove the containers and the demo certificates that are left over).

**Type** one line at a time:

```bash
docker compose -f docker-compose.vulnerable.yml down -v
docker compose -f docker-compose.fixed.yml down -v
docker compose -f docker-compose.student-task.yml down -v
```

**You should see:** Lines ending in `Removed`. Then check that your answer sheet has everything: Steps 2, 3 (A1), Steps 5, 6 (A2), Steps 7, 8, 9, 10 (A3). Then do your own form: odd IDs do Part 2; even IDs do Parts 3 and 4. And do not forget to attach the commit link of `alice_student.py` (see the W12 section of `SUBMISSION.md`)

---

## Part 1 — Student Information

| Name | Student ID | Date | Group (your form) | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

## Part 2 — Conventional form (40 points; only if Conventional is your assigned form)

Answer each item in 2–3 sentences. You may answer in English or Thai. In this part **answer by yourself**, without using AI to answer.

**Q1 (10). Encrypted, but Eve can still read it.** Answer all three of these (1–2 sentences each):

- Alice says the TLS handshake succeeded. Does that mean the connection is really encrypted? (hint: Step 2)
- If it is really encrypted, why can Eve still read the secret?
- What is the difference between "encrypting" and "talking to the right person"?

**Q2 (10). Certificates and CAs.** Answer all three of these (1–2 sentences each):

- Eve's certificate has the name "bob" written correctly. Why can anyone make a certificate like that? (hint: Step 4)
- What does a CA add when it signs the real Bob's certificate? (compare it with a trusted authority certifying an ID card)
- Why did the checking Alice reject Eve before sending the secret? (hint: Steps 5 and 6) And what two things does she check?

**Q3 (10). How does TLS stop a man in the middle?** Explain the three jobs of the TLS handshake and say what an attacker can do if any one of them is missing: (a) key exchange (b) proving the server's identity with a certificate (c) the server signing to confirm (`CertificateVerify`). Answer each in 1–2 sentences.

**Q4 (10). Forward secrecy.** Answer both of these (2–3 sentences each): what is forward secrecy (use simple words, for example "if the long-term key leaks in the future, data that someone secretly recorded in the past is still safe"), and how does ephemeral (EC)DHE key exchange in TLS 1.3 make that true (the temporary keys are thrown away every time).

### Going further (optional — no marks)

- **Q5 — SSL → TLS.** Why did the SSL family fail (weaknesses in security and in design), and how did TLS 1.3 fix them?
- **Q6 — 0-RTT.** The speed benefit and the risk (data can be sent again / replayed). Why should it be used only for work that is safe to repeat?
- **Q7 — Web PKI.** The risk of a hacked CA, and the protections: certificate pinning, revocation (CRL / OCSP) and Certificate Transparency
- **Q8 — TLS and Noise.** Compare flexibility and complexity, and say when Noise is the better choice

---

## Part 3 — AIR-Sec Arm: Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

The AI wrote a function that fetches JSON from an internal API over HTTPS. It runs and looks tidy, but it has **the same bug as the Alice who does not check**.

> **AI's answer:**
>
> ```python
> import requests
> import urllib3
> urllib3.disable_warnings()
>
> def fetch(url, token):
>     resp = requests.get(
>         url,
>         headers={"Authorization": f"Bearer {token}"},
>         verify=False,
>         timeout=10,
>     )
>     resp.raise_for_status()
>     return resp.json()
> ```
>
> "This is secure: HTTPS encrypts all traffic, including the token. verify=False just accepts our internal certificate; it does not weaken the encryption."
>
> — end of AI answer —

1. **Find what's wrong (10).** Copy the wrong line, and explain in 2–3 sentences what someone in the middle of the path can do, like what Eve did (hint: Step 2)
2. **Fix it (10).** How can it be fixed so that it checks without turning checking off? (hint: tell the code to trust the **internal CA**) And which sentence of the AI's is "true but misleading"?

> Disclose any other AI use in the Part 1 table. This task counts toward the **Audit the AI** row.

---

## Part 4 — Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** A friend asks, *"Eve's certificate has the name 'bob' written correctly. Why does the computer not trust it?"* Explain in 3–5 sentences, **without hard words** (anyone can make a certificate, what does a CA that we trust add by signing, compare it with an ID card), and finish with one sentence on what happens if a CA is not honest.

**B. Prompt Problem (10).** Use any AI, and do this:

1. Write **one** prompt asking for an HTTPS client in Python that uses an internal CA and resists a man in the middle.
2. Copy the AI's answer into your answer sheet.
3. Check: (a) does it keep certificate checking on and load the internal CA, or does it use the shortcut `verify=False` / `CERT_NONE`? (b) does it separate "encrypting" from "checking identity", or does it just conclude "we use HTTPS so it is secure"? (c) does it say anything wrong or make anything up?
4. In the table in the answer sheet, tick **pass / fail** for each item with a 1-sentence reason, and finish with 1 sentence on whether you would trust this AI's answer, and why.

Submit your **prompt + the AI's answer + the check table with your own reasons**.

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "In Step 2 Alice says TLS succeeded and the data is really encrypted, but Eve can read the secret. How is that possible?"
2. "In Step 5 Eve's code is exactly the same. What changed on Alice's side, and when did Alice reject?"
3. "The fake certificate has the name bob written correctly. Why is it still rejected, and what does the real certificate have that the fake one does not?"

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — Alice does not check, Eve reads the secret | 20 | 20 |
| A2 — Alice checks, Eve cannot read it | 20 | 20 |
| A3 — Fix the code yourself + test + reasoning | 20 | 20 |
| Conventional written questions (Q1–Q4) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- Put your name, student ID and date in the answer sheet, and copy the commands and results from **your own** computer. The secret message is the same for everyone (it is a fixed value of the lab). What makes the work yours is the results copied from your own computer and the code you fixed yourself. Do not submit a friend's results as your own.
- **The commit link of `alice_student.py` on GitHub (required, no separate marks):** follow the W12 section of `SUBMISSION.md`, then paste the link in the answer sheet.
- **Explain in your own words** (marks are given for the reasoning): for the fill-in-the-blank items that give you a word bank (Steps 3, 6) you may use the words given. The short answer in Step 10 and the written part of your own form must be in your own words (why Eve can read the secret even though the connection is really encrypted, and why checking the certificate stops it). You do not need to write anything more than that.

**Deadline and late submission:** Submit by 23:59 (Thai time) on **Sunday 24 Jan 2027** (KOSEN rule: before the next class). A late submission loses 10% of this worksheet's marks for each day late (a part day counts as a day), down to 0. Uploading or replacing a file after the deadline counts the whole submission as late. Submit the common 60 marks and **one** form of your own only; doing both forms gives no extra marks. The viva checks your understanding and has no separate marks.
