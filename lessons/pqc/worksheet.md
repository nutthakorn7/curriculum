# Worksheet 15 — Post-Quantum Cryptography: a one-time signature used twice

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Aligned to:** NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA / SPHINCS+) · CWE-323 is only an analogy here (reuse in encryption); this lab is about reusing a one-time signing key
> **Kind:** Docker lab, step by step. No programming and no maths. Everything runs inside Docker, so you do not need Python on your computer.

> **Ethics note:** Only work on the two containers on your own computer that this lab starts (`vulnerable` on port 8100 and `fixed` on port 8101). Forging signatures or tokens on systems that are not yours and without permission is illegal. Keep the flag inside this lab.

## Read this first

**What you will do today:** A quantum computer could break RSA and elliptic-curve signatures, so we study signatures that only rely on a **hash** (SHA-256). The simplest one is the **Lamport one-time signature**. Its private key is **two secret tokens for every bit of a message**: one token to use when the bit is 0, one when it is 1. To sign, you hand over **one token per bit**. One signature is safe, because half of the tokens stay secret. But the key may sign **only once**. We will look at a pretend server that forgets this rule: we ask it to sign a message **and its exact opposite**, and then the whole private key falls out and we can forge a signature on a message it refused to sign. Then we look at a fixed server that refuses the second signature.

**Every step is written the same way:**

| Heading | Meaning |
|---|---|
| **What to do** | Says what this step does |
| **Type** | Copy the whole line, paste it into the Terminal, and press Enter |
| **You should see** | The screen should look roughly like this (the letters and numbers after `=` are random and will not be the same as the example) |
| **Means** | What the result means |
| **Write in the answer sheet** | What to copy or write in your answer sheet |

**Marks**

- Everyone does **Part A (60 marks)**, which is the same for both forms.
- Then do **only your own form (40 marks)**. Look at the last digit of your student ID: **odd = AIR-Sec (Parts 3–4)**, **even = Conventional (Part 2)** (0 counts as even). Write your form in the Group box.
- You may answer in English or Thai. Short and clear is enough.
- **Answer sheet:** in Classroom → Week 15, open the file for your form (`Wk15_Answer_Sheet_Conventional` or `Wk15_Answer_Sheet_AIR-Sec`), choose Open with → Google Docs, type in the grey boxes, then choose File → Download → PDF.
- Submit one file named with your student ID, for example `Wk15_66990000.pdf` (do not type the `<` `>` signs), at `learn.zcr.ai/submit` with your Week 15 submission code from your KMITL email, by **Sunday 14 Feb 2027, 23:59**.
- Items marked *optional* have no marks. You can skip them.

| Part A | Marks | Steps to write in the answer sheet |
|---|---:|---|
| A1 — one signature hides half of the key | 20 | Steps 2, 3 |
| A2 — sign the opposite message, recover the key, forge the admin signature | 20 | Steps 4, 5, 6 |
| A3 — the fixed server refuses, and how far the fix goes | 20 | Steps 7, 8, 9, 10 |

**Words you need to know**

| Word | Simple meaning |
|---|---|
| Terminal | A window where you type commands |
| Docker / container | A program that starts a small "pretend computer" on your computer. If you break it, delete it and start again |
| hash (SHA-256) | A one-way fingerprint. Easy to compute from a token, but you cannot get the token back from the fingerprint |
| token (preimage) | A secret value in the private key. Its hash is published in the public key |
| public key | The list of hashes of all tokens. Anyone can use it to check a signature |
| signature | The tokens the signer hands over, one per bit of the message. Anyone can hash them and compare with the public key |
| one-time signature | A key that may sign **one** message only. The second signature gives away more tokens |
| forgery | A signature that checks out, on a message the key owner never approved |
| flag | A text such as `FLAG{...}` that the lab prints when you succeed |

**Questions people often ask**

- *Do I need to be good at maths?* No.
- *Do I need to write programs or install Python?* No. Copy the commands and paste them. Python runs inside Docker.
- *If I make a mistake, will my computer break?* No. Everything is inside containers. If you get confused, type the command in Step 11 and start again.
- *My letters and numbers are not the same as my friend's. Is that wrong?* No. The keys are random every time the lab starts. The words `True`, `False`, `PASS`, `403` and the flag are the same for everyone.
- *How do I paste a command into the Terminal?* Copy the command from the worksheet, then Windows: press Ctrl+V or right-click · Mac: press Cmd+V, then press Enter.
- *How do I copy results from the Terminal?* Select the text with the mouse first, then Windows: press Ctrl+Shift+C · Mac: press Cmd+C. Or take a screenshot.
- *Do I have to restart the lab in the middle?* No, and you should not. A restart gives both servers new keys, and the fixed server's one signature is used up by Step 7.

**If you see a message like this**

| Message on screen | Cause | Fix |
|---|---|---|
| `Cannot connect to the Docker daemon` or `error during connect` | Docker is not open | Open Docker Desktop and wait until it says Engine running |
| `no configuration file provided: not found` | The Terminal is not in the lab folder | Repeat Prep step 4 |
| `Bind for 127.0.0.1:8100 failed: port is already allocated` | Another program on your computer already uses port 8100 (or 8101) | Close that program (or its container) and type Prep step 5 again |
| `service "vulnerable" is not running` | The lab is not running (you typed Step 11, or the lab never started) | Type Prep step 5 again. You get new keys, so start again from Step 2 |
| `sig_00000000.json not found` | You have not done Step 2 yet | Do Steps 2 and 4 first, then repeat |
| Step 7 ends with `FAIL: first /sign unexpectedly refused by fixed app` | You typed Step 7 a second time, and the fixed server's one signature was already used | Type Step 11, then Prep step 5, and do Steps 2 to 7 again. Type Step 7 only once |

If you still cannot do it, ask a friend or your instructor.

---

## Before you start: set up your computer (at home, once)

If you already did Weeks 2–6 or 10–13, you have Docker and the ZIP file. Start at **Prep step 4**. But the ZIP must have the folder `week15-pqc` with the file `lamport.py` in it. If you cannot find it, download the ZIP again as in Prep step 2.

#### Prep step 1 — Open Docker Desktop

**What to do:** If you do not have it yet, install it from <https://www.docker.com/products/docker-desktop/> and leave the program open.

**You should see:** the Docker Desktop window says **Engine running**.

#### Prep step 2 — Download the lab files

**What to do:** Open <https://github.com/nutthakorn7/security-cryptography>, click the green **Code** button, and choose **Download ZIP**. You do not need a GitHub account and you do not need to fork.

#### Prep step 3 — Unzip the ZIP file

**What to do:** Windows: right-click the ZIP file and choose **Extract All** · Mac: double-click the ZIP file.

**You should see:** a folder called `security-cryptography-master`. Some computers make a folder with the same name inside it; open it until you can see the `labs` folder.

#### Prep step 4 — Open a Terminal inside the lab folder

**What to do:** Inside the `security-cryptography-master` folder, open `labs` and then open `week15-pqc`

- **Windows:** open the `week15-pqc` folder in File Explorer, right-click an empty spot, and choose **Open in Terminal** (if you do not see it, hold Shift, right-click, and choose **Open PowerShell window here**)
- **Mac:** open the Terminal app, type `cd` and one space, drag the `week15-pqc` folder into the window, then press Enter

Check that you are in the right place with this command (on Windows PowerShell you can also type `dir`):

```bash
ls
```

**You should see:** `docker-compose.yml` and `lamport.py` in the list.

#### Prep step 5 — Start the lab

**Type:**

```bash
docker compose up -d
```

**You should see:** lines ending in `Started` (one for `vulnerable`, one for `fixed`). The first time you need the internet and it may take several minutes. Do not close the window while you wait.

#### Prep step 6 — Check that the lab is ready

**What to do:** Wait about 30 seconds (the lab installs a small package when it starts), then type the command for your computer.

**Type** (Mac):

```bash
docker compose logs | grep "Running on"
```

**Type** (Windows):

```bash
docker compose logs | findstr /C:"Running on"
```

**You should see:** both of these (other `Running on` lines may be mixed in; ignore them):

```
vulnerable-1  |  * Running on http://127.0.0.1:8100
fixed-1       |  * Running on http://127.0.0.1:8101
```

If you do not see both, wait a little and type the command again. If it still fails after 2 minutes, type `docker compose ps -a`, take a screenshot, and send it to your instructor.

---

## Part A — The lab (both forms, 60 points)

There are two servers (programs in Docker). They use the same Lamport one-time signature and have the same endpoints. Do A1 → A2 → A3 one after the other, with the lab started **once** (do not restart it in the middle):

| Server | What it does | Does it let a second signature through? |
|---|---|---|
| `vulnerable` (port 8100) | Signs any message you ask for, again and again, with the **same** key. It only refuses one message: the reserved **admin message** `0xA5A5C3C3` | **Yes**: this is the bug |
| `fixed` (port 8101) | The same, but its key may sign **only once**. A second request is refused with `403` | **No** |

A message here is 32 bits, written as 8 hex digits (`00000000` is all zeros, `ffffffff` is all ones). The commands in this lab are `lamport.py` (a small helper we give you) and `exploit.py` (the supplied attack script). Both run inside the `vulnerable` container.

> **If you really cannot use Docker:** tell your instructor, then copy the example lines in the worksheet into your answer sheet and write "from the worksheet example" next to them. You can answer Steps 3, 9 and 10 by reading the worksheet.

### A1 — One signature hides half of the key (20 points)

#### Step 1 — Read: how a Lamport signature works

**What to do:** Just read. You do not need to type anything.

The private key has **two secret tokens for each of the 32 bits** of a message: one for "this bit is 0" and one for "this bit is 1". The public key is the **hash** of every token, and anyone can read it. To sign a message, the server hands over, for each bit, the token that matches that bit. Anyone can check a token by hashing it and comparing the result with the public key. After **one** signature, a stranger holds only one token per bit, so half of the private key is still secret. The vulnerable server signs again and again with the same key, and that is what we will exploit.

#### Step 2 — Get one signature and check one token

**What to do:** Ask the vulnerable server to sign the message `00000000` (all bits are 0). The helper then hashes the token for bit 0 and compares it with the two public-key entries for bit 0.

**Type:**

```bash
docker compose exec vulnerable python lamport.py sign 00000000
```

**You should see:** six lines like these (the letters after `=` will be different)

```
signed 0x00000000 on the vulnerable server (:8100): 32 preimages revealed
message bit 0 = 0
SHA256(sig[0])        = 6aa11b793227...
matches pk[0][0] (value 0): True
matches pk[0][1] (value 1): False
saved sig_00000000.json
```

**Means:** the message has bit 0 equal to 0, so the server revealed the **0-token** for that bit. Its hash matches the public-key entry for value 0 (`True`) and not the entry for value 1 (`False`). So this one signature shows one token per bit, but **not** the other token.

**✍️ Write in the answer sheet (Step 2):** copy the lines from `message bit 0` to `matches pk[0][1]` from your own screen

#### Step 3 — Summarise in your own words

**What to do:** Fill in the blanks.

> With this one signature we know ________ secret token(s) for each bit position (Choose a number: `1` / `2`), so ________ of the private key is still secret (Choose: `half` / `none`).

**✍️ Write in the answer sheet (Step 3):** write the full sentence

### A2 — Sign the opposite message, recover the key, forge the admin signature (20 points)

#### Step 4 — Get a second signature on the opposite message

**What to do:** Now ask for `ffffffff` (all bits are 1). This is the exact **opposite** of `00000000`: every single bit is different.

**Type:**

```bash
docker compose exec vulnerable python lamport.py sign ffffffff
```

**You should see:** the same six lines, but now bit 0 is 1 and the two `matches` answers are the other way round

```
signed 0xffffffff on the vulnerable server (:8100): 32 preimages revealed
message bit 0 = 1
SHA256(sig[0])        = fce7ac6eb14b...
matches pk[0][0] (value 0): False
matches pk[0][1] (value 1): True
saved sig_ffffffff.json
```

**Means:** the vulnerable server signed a second message with the same key. This time it revealed the **1-token** for every bit.

**✍️ Write in the answer sheet (Step 4):** copy the lines from `message bit 0` to `matches pk[0][1]` from your own screen

#### Step 5 — Put the two halves of one key position together

**What to do:** Take key position 0. The first signature gave you its 0-token and the second gave you its 1-token. The helper checks both against the public key.

**Type:**

```bash
docker compose exec vulnerable python lamport.py both 0
```

**You should see:** (your letters will be different)

```
key position 0
from sig_00000000.json (message bit = 0): preimage 0e780c6dd23e...  SHA256 matches pk[0][0]: True
from sig_ffffffff.json (message bit = 1): preimage f0528b580ef8...  SHA256 matches pk[0][1]: True
both secret halves of key position 0 are now known
```

**Means:** for position 0 you now hold **both** secret tokens, and each one hashes to its public-key entry. The two messages differ in every bit, so the same is true for **all 32 positions**: you hold the whole private key. (Optional: type the same command with `31` instead of `0`.)

**✍️ Write in the answer sheet (Step 5):** copy the three lines above from your own screen

#### Step 6 — Forge a signature on the admin message and get the flag

**What to do:** The admin message is `0xA5A5C3C3`. The server **refused** to sign it for you, but now you can build the signature yourself, offline: for each bit, pick the token that the admin message needs. The helper does this and sends the result to the server.

**Type:**

```bash
docker compose exec vulnerable python lamport.py forge
```

**You should see:** four lines like these (the flag is the same for everyone)

```
recovered both preimages for all 32 positions; every one hashes to the public key: True
admin message = 0xa5a5c3c3
wrote forged_admin.json (32 preimages)
POST /admin -> HTTP 200 {"flag": "FLAG{lamport_one_time_only}"}
```

**Means:** the server accepted a signature on a message it **never signed** for you, and gave you the flag. The server only checks that each revealed token hashes to the public key. It cannot tell that you assembled the signature from a key that leaked.

**✍️ Write in the answer sheet (Step 6):** copy the four lines above from your own screen, then write one sentence on why the server accepted the signature

### A3 — The fixed server refuses, and how far the fix goes (20 points)

#### Step 7 — Run the supplied attack against both servers (type it only once)

**What to do:** `exploit.py` repeats what you did by hand on the vulnerable server, and then runs the **identical** attack on the fixed server: sign `00000000`, then ask for `ffffffff`. Type it **once**: the fixed server can sign only once, and this run uses it up.

**Type:**

```bash
docker compose exec -e FIXED_HOST=fixed vulnerable python exploit.py
```

**You should see:** the first half is the vulnerable server again and ends with a `PASS` line and the flag. The second half is the fixed server. Find these lines (the first half has other lines mixed in)

```
PASS: fixed app REFUSED the 2nd /sign (status=403): 'one-time key already used' -- attacker gets only ONE preimage set
[*] Attacker can only supply a bogus forgery (16/32 admin bits have no known preimage); submitting it to /admin ...
PASS: fixed app correctly REJECTED the forgery (:8101) -- status=403, no flag

=== SUMMARY ===
  vulnerable (:8100) forgery succeeded  : True
  fixed      (:8101) attack defeated    : True
```

**Means:** the fixed server signed the first message, then **refused** the second one (`403`). So the attacker never gets the 1-tokens, cannot complete the key, and the forged admin signature is rejected. No flag.

**✍️ Write in the answer sheet (Step 7):** copy the two `PASS: fixed app` lines and the two lines under `SUMMARY` from your own screen

#### Step 8 — Find what only the fixed server has

**What to do:** The two servers are almost the same program. Look for the one thing that only the fixed server does: it remembers which message it has already signed (`_signed_message`).

**Type** one line at a time:

```bash
docker compose exec vulnerable grep -n "_signed_message" fixed_app.py
docker compose exec vulnerable grep -n "_signed_message" vulnerable_app.py
```

**You should see:** the first command prints five lines (the numbers at the start may differ if the file changes). The second command prints **nothing**

```
54:_signed_message = None  # the single message this key has signed (None until first use)
102:    global _signed_message
126:        if _signed_message is not None:
129:                "detail": f"this Lamport key already signed 0x{_signed_message:0{N // 4}x}; "
132:        _signed_message = message
```

**Means:** the fixed server stores the first message in `_signed_message` (line 132). On the next `/sign` it sees that something is stored (line 126) and refuses with `403`. The vulnerable server has no such line at all, so it signs every time.

**✍️ Write in the answer sheet (Step 8):** copy the two lines that contain `if _signed_message is not None:` and `_signed_message = message`, and write "nothing printed" for the second command

#### Step 9 — Summarise in your own words

**What to do:** Fill in the blanks (hint: Step 7).

> The fixed server refuses the ________ signature request (Choose: `first` / `second`) with status ________ (Choose: `200` / `403`). With only ONE signature the attacker knows ________ token(s) for each bit (Choose a number: `1` / `2`), so cannot forge the admin signature.

**✍️ Write in the answer sheet (Step 9):** write the full sentence

#### Step 10 — How far does the fix go?

**What to do:** Read, then answer in 1–2 sentences.

The fix adds **no new maths**: it only refuses to sign twice. A scheme can be secure on paper and still be used insecurely. Real hash-based signatures (XMSS, and SPHINCS+, which is standardised as FIPS 205) sign many messages by using a huge number of one-time keys and never reusing one. Look at this server: it refuses **every** second `/sign`, even for the **same** message.

> Would signing the same message again give away any new token? Why does this toy server still refuse it, and what should a real signer do when a client simply retries the same message? (hint: Step 1 and Step 8)

**✍️ Write in the answer sheet (Step 10):** write your answer

#### Step 11 — Shut down the lab and check your answer sheet

**What to do:** Type this command to stop and remove the containers. Then check that your answer sheet has everything.

**Type:**

```bash
docker compose down
```

**You should see:** a line ending in `Removed` for each container.

Check that your answer sheet has everything: Steps 2, 3 (A1), Steps 4, 5, 6 (A2), Steps 7, 8, 9, 10 (A3). Then do your own form: odd IDs do Parts 3 and 4; even IDs do Part 2.

---

## Part 1 — Student Information

| Name | Student ID | Date | Group (your form) | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

## Part 2 — Conventional form (40 points; only if Conventional is your assigned form)

Answer each item in 2–3 sentences. You may answer in English or Thai. In this part **answer by yourself**, without using AI to answer.

**Q1 (10). Shor and Grover.** Answer all three of these (1–2 sentences each):

- Which algorithm threatens RSA and elliptic-curve crypto, and what maths problem does it solve that makes those two schemes breakable?
- Does Grover's algorithm break AES the same way? How big is its speed-up?
- What is the cheap, practical defence for symmetric crypto and hashes?

**Q2 (10). Harvest now, decrypt later.** Answer all three of these (1–2 sentences each):

- What does an attacker do today to carry out "harvest now, decrypt later"?
- Why does that make migrating to post-quantum crypto urgent **today**, even though a large quantum computer does not exist yet?
- Give one kind of data for which this threat is real right now.

**Q3 (10). Why a reused Lamport key is catastrophic.** Answer all three of these (1–2 sentences each):

- What does one signature reveal about the private key? (hint: Step 2 and Step 3)
- Why does signing a message **and its exact opposite** reveal the whole private key? (hint: Step 4 and Step 5)
- How could the attacker sign a message that the server refused to sign? (hint: Step 6)

**Q4 (10). ML-KEM and ML-DSA.** Answer all three of these (1–2 sentences each):

- What is ML-KEM (FIPS 203) for, and what is ML-DSA (FIPS 204) for?
- What is the difference between a KEM (key encapsulation) and a signature?
- Name a protocol such as TLS and say where each one would fit.

### Going further (optional — no marks)

- **Q5 — The four families.** Name the four families of post-quantum cryptography (lattice, hash-based, code-based, multivariate), give one example scheme for each, and say which family this week's lab belongs to.
- **Q6 — Hash-based signatures.** What is a hash-based signature, which key-use rule matters in this lab, and what is its main practical limitation compared with RSA or ECDSA (signature size, the one-time-key rule)?
- **Q7 — Crypto-agility.** What is crypto-agility, and why is it the real engineering lesson of the post-quantum migration? Give two design practices that make a system crypto-agile.
- **Extension — the HNDL companion lab (no marks).** `labs/week15-pqc/hndl/` (its own `README.md` and `worksheet.md`) is about key exchange: harvest a session now, break its classical key exchange later, and see a hybrid classical + ML-KEM channel resist the same attack. It is optional, adds no points, and does not replace the Lamport lab.

---

## Part 3 — AIR-Sec form: Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's code.

A teammate asked an AI assistant to "write a helper that signs each outgoing message with our Lamport key." The AI produced the snippet below. It runs, it type-checks, and it produces signatures that verify. It also contains a **catastrophic, subtly-hidden flaw** of exactly the kind this week is about.

> **AI's answer — `lamport_signer.py`:**
> ```python
> import hashlib, os
>
> N = 256
>
> class LamportSigner:
>     """Signs messages with a Lamport one-time signature. Reuse the instance for all your
>     outgoing messages so you only pay key-generation cost once."""
>     def __init__(self):
>         # Generate the keypair ONCE at startup, then reuse it for the lifetime of the process.
>         self.sk = [(os.urandom(32), os.urandom(32)) for _ in range(N)]
>         self.pk = [(self._h(a), self._h(b)) for (a, b) in self.sk]
>
>     @staticmethod
>     def _h(x): return hashlib.sha256(x).digest()
>
>     def _bits(self, msg: bytes):
>         digest = hashlib.sha256(msg).digest()   # hash the message to 256 bits, then sign
>         return [(digest[i // 8] >> (i % 8)) & 1 for i in range(N)]
>
>     def sign(self, msg: bytes):
>         bits = self._bits(msg)
>         return [self.sk[i][bits[i]] for i in range(N)]   # reveal one preimage per bit
>
> # Usage: one signer, many messages.
> signer = LamportSigner()
> for m in outgoing_messages:          # <-- signs EVERY message with the SAME key
>     send(m, signer.sign(m))
> ```
> — end of AI answer —

1. **Find the catastrophic flaw (8).** Copy the exact line(s) and name the vulnerability. Explain, in terms of *tokens per bit* (the lab calls them preimages), what an attacker who collects a handful of these signatures can eventually do, and why the advice in the docstring ("reuse the instance … so you only pay key-generation cost once") is exactly backwards for this kind of key. (hint: Step 1 and Step 5)
2. **A mitigating detail — and why it does NOT save the design (6).** Unlike the lab, this snippet *hashes the message before signing* (`self._bits` hashes `msg`). Does hashing first stop the "message and its opposite" trick? Say what it **does** change (the attacker can no longer choose which key bits to reveal by choosing the message) and what it does **not** change (enough *different* messages still reveal both tokens at enough positions to forge: hashing controls *which* bits leak, not *whether* a reused key leaks). Roughly how many signatures before forging becomes feasible? (hint: Step 4)
3. **Write the corrected design yourself (6).** Say which control you added (one-time enforcement, or a many-time scheme such as XMSS or SPHINCS+) and why making the second `sign()` call **raise an error** is the *minimum* correct fix. (hint: Step 8)

> Disclose any other AI use in the Part 1 table. This task counts toward the **Audit the AI** row.

---

## Part 4 — AIR-Sec form: Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** Explain to a junior developer who knows what "hashing" is but has never heard of a "one-time signature" **why a Lamport key must never sign two different messages.** In 2–4 sentences: describe the private key as "two secret tokens per bit, and a signature hands over one token per bit," and explain why signing a second, different message hands over enough *extra* tokens that a stranger could build a signature for a message you never approved. Avoid difficult words ("Merkle tree", "preimage resistance"): explain the **mechanism**.

**B. Prompt Problem (10).** Use any AI you like and do this:

1. Write **one** prompt asking the AI to explain *why moving to post-quantum crypto is urgent even though large quantum computers do not exist yet*.
2. Copy the AI's answer into your answer sheet.
3. Check: (a) does it centre **"harvest now, decrypt later"** (attackers recording encrypted traffic today to decrypt it once quantum computers arrive), instead of only saying "quantum computers are coming"? (b) does it separate **Shor** (a real break of RSA and elliptic curves) from **Grover** (only a square-root speed-up for symmetric keys and hashes, handled with longer keys), instead of saying that quantum "breaks all crypto"? (c) does it say anything wrong or make anything up (for example a wrong NIST number: ML-KEM is **FIPS 203**, ML-DSA is **FIPS 204**, SLH-DSA / SPHINCS+ is **FIPS 205**; a claim that AES-256 is "broken" by quantum; or that a quantum computer has already broken deployed crypto)?
4. In the table in your answer sheet, tick **pass / fail** for each item with a one-sentence reason, then finish with one sentence saying whether you would trust this AI's answer, and why.

Submit **your prompt + the AI's answer + your check table with your own reasons**.

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "In Step 5, show me the two tokens for one key position and the two public-key entries they match. If you had signed only `00000000` and never `ffffffff`, which half would you be missing, and could you still forge the admin signature?"
2. "In Step 6, the server refused to sign `0xA5A5C3C3` when you asked, so how is your forged signature on that exact message accepted? What did the server never do, and what did you do instead?"
3. "In Step 8, which lines only the fixed server has? Why does that, with no new maths, defeat the whole attack? The fixed server also refuses a repeat of the same message: does a repeat give away anything new, and why does this server still refuse it?"

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — one signature hides half of the key | 20 | 20 |
| A2 — sign the opposite message, recover the key, forge | 20 | 20 |
| A3 — the fixed server refuses + how far the fix goes | 20 | 20 |
| Conventional written questions (Q1–Q4) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- Put your name, student ID and date in the answer sheet, and copy the commands and results from **your own** computer. It is normal that your random letters and numbers are not the same as a friend's. Your flag may be the same as a friend's. This week there is no personal flag. Do not submit a friend's results as your own.
- **Explain in your own words** (marks are given for the reasoning): for the fill-in-the-blank items that give you a word bank (Steps 3 and 9) you may use the words given. The short answers in Steps 6 and 10 and the written part of your own form must be in your own words (why the forged signature was accepted, and why the fix refuses a second signature even for the same message). You do not need to write anything more than that.

**Deadline and late submission:** Submit by 23:59 (Thai time) on **Sunday 14 Feb 2027** (KOSEN rule: before the next class). A late submission loses 10% of this worksheet's marks for each day late (a part day counts as a day), down to 0. Uploading or replacing a file after the deadline counts the whole submission as late. Submit the common 60 marks and **one** form of your own only; doing both forms gives no extra marks. The viva is used to check understanding and has no separate marks.
