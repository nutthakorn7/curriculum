# {{ slot_label }} — PQC: Harvest Now, Decrypt Later + Hybrid KEM

**Topic:** Post-quantum cryptography — the *confidentiality* migration: harvest-now-decrypt-later
(HNDL), crypto agility, and **hybrid key exchange** (classical + PQC KEM) · **Kind:** LAB
**Concepts:** KEM, the quantum threat to key exchange (Shor), HNDL, ML-KEM (Kyber), hybrid mode,
crypto-agility · **Analogous CWE:** CWE-327 (Use of a Broken or Risky Cryptographic Algorithm)

> **Companion to** the Lamport OTS lab in `../` (the parent `{{ labname }}/` directory). That lab is
> the *signature* half of PQC; this one is the *confidentiality* half — the part the {{ slot_label }}
> "quantum readiness" picture puts at its centre (hybrid mode, harvest-now-decrypt-later). Run
> either or both.

## This week — what to do

1. **Before class** — Docker Desktop working; skim {{ ref('key-exchanges') }} (Key Exchanges) and {{ ref('secure-transport') }} (TLS) —
   this lab is the "what happens to those key exchanges under quantum" sequel.
2. **Lecture (part of the 120-min PQC block)** — why Shor breaks RSA/ECC key exchange outright;
   "harvest now, decrypt later" and why it makes migration urgent *today*; ML-KEM (Kyber) as the
   NIST KEM; **hybrid mode** (deploy classical + PQC together so breaking one is not enough);
   crypto-agility as the real engineering lesson.
3. **Lab** — `docker compose up`, then play the game below: **harvest** a session transcript,
   break its classical KEM **offline**, decrypt it and capture your flag; then watch the *same*
   attack fail against the **hybrid** channel. Complete **Worksheet** (`worksheet.md`).
4. **Submit** — worksheet PDF + flag → Classroom · exploit run/output → GitHub. (How:
   [SUBMISSION.md](../../../SUBMISSION.md).)

## Objectives

- Explain **harvest-now-decrypt-later**: why an adversary records encrypted traffic *today* to
  decrypt it once the key-exchange primitive falls to a quantum computer — and why "the traffic is
  encrypted" is not the same claim as "the traffic is *safe long-term*".
- Show that a session's confidentiality rests on its **KEM**, not its bulk cipher: AES-GCM is fine;
  the break is in the key exchange that produced the AES key.
- Explain **hybrid mode**: a session key derived from two independent shared secrets (classical +
  ML-KEM) stays secret as long as *either* KEM holds — the deployable mitigation available now.
- Recognise the classic wrong "fix" — *"just use a bigger RSA key"* — and why it does **not**
  address a quantum adversary (Shor scales past any RSA size; only a different, quantum-hard
  problem does).

## Run it

```bash
cd {{ labpath }}/hndl
docker compose up          # vulnerable :8120 · fixed :8121
```
Then, from another shell (or the course toolbox), harvest + break:
```bash
python exploit.py          # attacks :8120 (recovers the flag), then shows :8121 resists
```

## The game — "Harvest Now, Decrypt Later"

**Vulnerable channel (`:8120`).** `GET /capture` returns the transcript a passive eavesdropper on
the wire would see: the classical RSA-KEM public modulus, the encapsulated secret, and the
AES-GCM-sealed message. That is your *harvest*. The session key is **not** in the capture — but it
is fully recoverable, because the classical modulus is small enough to factor (your stand-in for
"a quantum computer runs Shor, later"). `exploit.py` factors it, re-derives the session key, and
decrypts the harvested message → **your flag**.

**Fixed channel (`:8121`).** Same `/capture`, but the session key is
`KDF(s_classical ‖ s_ml_kem)` — a **hybrid** of the same breakable RSA-KEM *and* real
**ML-KEM-512**. Run the same `exploit.py`: it still factors the classical half, but the KDF also
needs the ML-KEM secret, whose private key is never in the transcript. The derived key is wrong,
AES-GCM's authentication tag fails, and the flag stays confidential. **That is the fix.**

**Evidence artifact.** The attributable evidence is the flag recovered from the *vulnerable*
channel's harvested capture. The fixed channel never yields it. Submit the flag + your `exploit.py`
run output.

## Honest caveats — what is real and what is modelled (sandbox only)

- The **classical KEM is textbook RSA with a deliberately small (64-bit) modulus**. Real key
  exchange uses 256/3072-bit parameters no classical computer can break. We shrink it *only* so the
  "quantum breaks the classical half" step runs in under a second on a laptop today. The
  lesson — harvested traffic becomes readable once its KEM falls — is identical at real sizes; only
  the wall-clock of the break changes.
- The **PQC half is REAL ML-KEM-512** (NIST FIPS 203, via the pure-Python `kyber-py`), not a
  stand-in. Its lattice hardness is what keeps the hybrid capture confidential here.
- Everything runs against instructor-provided sandbox targets only. See
  [`../../../ETHICS.md`](../../../ETHICS.md).
