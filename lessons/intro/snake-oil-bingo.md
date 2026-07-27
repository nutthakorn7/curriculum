# 🐍 Snake Oil Bingo — Week 1

> **Course:** Security & Cryptography (KOSEN69) · **Week 1** — Security Mindset &
> Threat-Modelling a Cryptographic System
> **Play:** in table groups, during the lecture
> **Cards:** A–F — everyone gets a copy; each table plays one letter between them

*Snake oil* is the trade's name for a security claim that sounds authoritative and means
nothing. This card holds 24 of them. Every phrase on it is the kind of thing real vendor pages,
real blog posts and real colleagues actually say.

## How to play

1. **Everyone gets a card; your table plays one letter.** All copies at your table carry the
   same letter, and neighbouring tables get a different one — the arrangements differ, so a line
   on your card is not a line on theirs.
2. **Mark a square** the moment its myth surfaces — in the Exhibit as it is read aloud, or in
   the discussion that pulls the Exhibit apart. The wording will not match your card exactly;
   you are listening for the *claim*, not the phrasing.
3. **A marked square only counts once your table can state the one-line _technical_ reason the
   claim is wrong.** This is the whole game. "That sounds like marketing," "that's obviously
   false," and "our lecturer said so" are not reasons.
4. **The instructor verifies.** Call them over, give the reason out loud, in one sentence, with
   no notes. If it holds, the square is yours. If it doesn't, the square stays open and you can
   try again later.
5. **BINGO** = five verified squares in a straight line — any row, any column, or either
   diagonal. The **FREE** centre square counts as already verified.
6. **First verified BINGO wins.** Shout it. The instructor will re-check every square in the
   line before it counts, so do not claim a line you cannot defend.

**Tip:** scribble your reason next to the square as soon as you agree on it. You will be asked
to say it out loud, and a reason that felt obvious four minutes ago has a way of evaporating.

## The myth pool

All 24 myths appear on every card — only the arrangement changes.

| # | The claim |
|---|---|
| 1 | "Military-grade encryption." |
| 2 | "It's encrypted, so nobody can change it." |
| 3 | "The key is in a private repository, so it isn't exposed." |
| 4 | "We seed the random number generator from the system clock, so every install is different." |
| 5 | "We check the token with a normal comparison — either it matches or it doesn't." |
| 6 | "Unbreakable 256-bit security." |
| 7 | "We're on HTTPS, so the data is end-to-end encrypted." |
| 8 | "The key is hardcoded, but the app is compiled — nobody can read it out." |
| 9 | "Our session tokens are randomly generated, so they can't be guessed." |
| 10 | "We use a standard crypto library, so implementation bugs aren't our problem." |
| 11 | "It's quantum-proof, because the key is long enough." |
| 12 | "Passwords are hashed with SHA-256, so a database leak is harmless." |
| 13 | "The key is stored in the same database as the data it encrypts." |
| 14 | "Detailed error messages help our users; they don't give anything away." |
| 15 | "The IV isn't secret, so it doesn't need to be random." |
| 16 | "Our encryption algorithm is proprietary, so attackers have nothing to analyse." |
| 17 | "We moved from AES-128 to AES-256, so we're twice as secure." |
| 18 | "We use the same key in dev, staging and production — it's the same application." |
| 19 | "The mobile client skips the certificate check, but the traffic is still encrypted." |
| 20 | "The nonce isn't secret, so reusing it doesn't hurt." |
| 21 | "Side-channel attacks need physical access to the machine, so they don't apply to us." |
| 22 | "It's FIPS-validated, so our cryptography is secure." |
| 23 | "We follow current NIST key-length guidance, so our use of cryptography is fine." |
| 24 | "That key has never leaked, so we've never needed to rotate it." |

Squares on the cards below carry the number and a short label; the table above is the full
wording.

## The cards

### Card A

| B | I | N | G | O |
|---|---|---|---|---|
| **11.** Quantum-proof: long key | **4.** Seeded from the clock | **1.** Military-grade encryption | **14.** Detailed errors leak nothing | **20.** Nonce not secret; reuse ok |
| **9.** Our tokens are random | **18.** Same key in dev and prod | **3.** Key's in a private repo | **24.** Never leaked, never rotated | **19.** Skips cert check, still TLS |
| **22.** FIPS-validated, so secure | **13.** Key stored beside the data | **FREE** | **2.** Encrypted, so unchangeable | **23.** On NIST sizes, so fine |
| **21.** Side channels need physical | **6.** Unbreakable 256-bit | **12.** SHA-256 password hashes | **10.** Library, so no impl bugs | **8.** Compiled app hides the key |
| **15.** IV is public, so needn't be random | **7.** HTTPS means end-to-end | **5.** It matches or it doesn't | **17.** AES-256 = twice AES-128 | **16.** Secret in-house algorithm |

### Card B

| B | I | N | G | O |
|---|---|---|---|---|
| **8.** Compiled app hides the key | **3.** Key's in a private repo | **12.** SHA-256 password hashes | **21.** Side channels need physical | **6.** Unbreakable 256-bit |
| **11.** Quantum-proof: long key | **9.** Our tokens are random | **15.** IV is public, so needn't be random | **24.** Never leaked, never rotated | **10.** Library, so no impl bugs |
| **7.** HTTPS means end-to-end | **16.** Secret in-house algorithm | **FREE** | **23.** On NIST sizes, so fine | **18.** Same key in dev and prod |
| **14.** Detailed errors leak nothing | **5.** It matches or it doesn't | **22.** FIPS-validated, so secure | **20.** Nonce not secret; reuse ok | **13.** Key stored beside the data |
| **2.** Encrypted, so unchangeable | **4.** Seeded from the clock | **19.** Skips cert check, still TLS | **17.** AES-256 = twice AES-128 | **1.** Military-grade encryption |

### Card C

| B | I | N | G | O |
|---|---|---|---|---|
| **19.** Skips cert check, still TLS | **23.** On NIST sizes, so fine | **8.** Compiled app hides the key | **9.** Our tokens are random | **10.** Library, so no impl bugs |
| **14.** Detailed errors leak nothing | **2.** Encrypted, so unchangeable | **1.** Military-grade encryption | **11.** Quantum-proof: long key | **3.** Key's in a private repo |
| **20.** Nonce not secret; reuse ok | **6.** Unbreakable 256-bit | **FREE** | **18.** Same key in dev and prod | **13.** Key stored beside the data |
| **5.** It matches or it doesn't | **12.** SHA-256 password hashes | **15.** IV is public, so needn't be random | **17.** AES-256 = twice AES-128 | **21.** Side channels need physical |
| **24.** Never leaked, never rotated | **22.** FIPS-validated, so secure | **4.** Seeded from the clock | **16.** Secret in-house algorithm | **7.** HTTPS means end-to-end |

### Card D

| B | I | N | G | O |
|---|---|---|---|---|
| **16.** Secret in-house algorithm | **15.** IV is public, so needn't be random | **24.** Never leaked, never rotated | **8.** Compiled app hides the key | **17.** AES-256 = twice AES-128 |
| **19.** Skips cert check, still TLS | **18.** Same key in dev and prod | **14.** Detailed errors leak nothing | **10.** Library, so no impl bugs | **13.** Key stored beside the data |
| **4.** Seeded from the clock | **21.** Side channels need physical | **FREE** | **20.** Nonce not secret; reuse ok | **1.** Military-grade encryption |
| **7.** HTTPS means end-to-end | **23.** On NIST sizes, so fine | **3.** Key's in a private repo | **11.** Quantum-proof: long key | **22.** FIPS-validated, so secure |
| **2.** Encrypted, so unchangeable | **9.** Our tokens are random | **5.** It matches or it doesn't | **12.** SHA-256 password hashes | **6.** Unbreakable 256-bit |

### Card E

| B | I | N | G | O |
|---|---|---|---|---|
| **2.** Encrypted, so unchangeable | **13.** Key stored beside the data | **4.** Seeded from the clock | **12.** SHA-256 password hashes | **16.** Secret in-house algorithm |
| **23.** On NIST sizes, so fine | **17.** AES-256 = twice AES-128 | **6.** Unbreakable 256-bit | **11.** Quantum-proof: long key | **24.** Never leaked, never rotated |
| **10.** Library, so no impl bugs | **15.** IV is public, so needn't be random | **FREE** | **22.** FIPS-validated, so secure | **5.** It matches or it doesn't |
| **7.** HTTPS means end-to-end | **8.** Compiled app hides the key | **19.** Skips cert check, still TLS | **9.** Our tokens are random | **3.** Key's in a private repo |
| **21.** Side channels need physical | **18.** Same key in dev and prod | **1.** Military-grade encryption | **20.** Nonce not secret; reuse ok | **14.** Detailed errors leak nothing |

### Card F

| B | I | N | G | O |
|---|---|---|---|---|
| **10.** Library, so no impl bugs | **5.** It matches or it doesn't | **15.** IV is public, so needn't be random | **22.** FIPS-validated, so secure | **20.** Nonce not secret; reuse ok |
| **1.** Military-grade encryption | **7.** HTTPS means end-to-end | **11.** Quantum-proof: long key | **18.** Same key in dev and prod | **23.** On NIST sizes, so fine |
| **3.** Key's in a private repo | **9.** Our tokens are random | **FREE** | **16.** Secret in-house algorithm | **2.** Encrypted, so unchangeable |
| **6.** Unbreakable 256-bit | **24.** Never leaked, never rotated | **13.** Key stored beside the data | **21.** Side channels need physical | **4.** Seeded from the clock |
| **14.** Detailed errors leak nothing | **17.** AES-256 = twice AES-128 | **19.** Skips cert check, still TLS | **12.** SHA-256 password hashes | **8.** Compiled app hides the key |
