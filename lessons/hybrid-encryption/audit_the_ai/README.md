# Audit the AI — Hybrid Encryption

## The scenario

A teammate asked an AI assistant to implement **hybrid encryption** for a Bob-to-Alice
messaging feature: RSA-OAEP wraps a freshly generated AES-256 session key, and AES-GCM
encrypts the actual messages. The AI's answer is in [`broken_hybrid_encrypt.py`](broken_hybrid_encrypt.py).
It looks clean, it runs, and the round trip (`python broken_hybrid_encrypt.py`) succeeds —
Alice correctly decrypts everything Bob sends.

**Your teammate wants to ship this to production. Don't let them yet.**

## Your task

1. **Read the code before running anything.** Check the fundamentals a rushed reviewer checks:
   Is RSA-OAEP used (not raw/textbook RSA)? Is the AES key 256-bit and generated with a CSPRNG?
   Is AES-GCM used (authenticated, not plain CBC/ECB)? Is the auth tag actually checked on
   decrypt? — On all of these, this code is genuinely correct. Don't stop there.
2. **Run it.** `python broken_hybrid_encrypt.py` — confirm the round trip works. A round trip
   succeeding is *not* the same as the scheme being secure. Ask yourself: what would happen if
   Bob sent a *second* message in the same session?
3. **Find the one planted bug.** It is not in the RSA/OAEP code. Look specifically at how the
   AES-GCM **nonce** is chosen and where it's used — line it up against what NIST SP 800-38D
   requires of a GCM nonce, and against what happens when that requirement is violated.
4. **Prove it, don't just assert it.** Write a short script that uses `HybridEncryptor` to send
   two different messages in one session, and demonstrates a concrete consequence of the bug —
   something an attacker who only sees the two ciphertexts (not the key) could actually do.
   (Hint: XOR is your friend. What do you get if you XOR the two ciphertexts together?)
5. **Explain the attack in your own words.** What can a passive eavesdropper who records two or
   more of Bob's messages in a session learn? Does the fix depend on how many messages were
   sent, or is even the *second* message in a session already at risk?
6. **Fix it.** Produce a corrected version of the file (`fixed_hybrid_encrypt.py`) that closes
   the bug with the smallest possible change. State explicitly: what did you change, and why
   does the fix not require touching the RSA/OAEP code at all?

## Constraints on your fix

- Do not change the RSA key size, the OAEP padding scheme, or the AES key size — none of those
  are the problem.
- Your fix must still let Bob send *multiple* messages per session without re-wrapping the AES
  key for every single message (i.e. don't "fix" this by doing per-message RSA — that defeats
  the point of hybrid encryption and isn't what real protocols do).
- Whatever your fix needs beyond the AES key itself (to make each message's encryption unique)
  must travel with the ciphertext to the recipient, in the clear — Alice has to be able to
  decrypt using only what Bob sends her, plus her own private key.

## Deliverable

Submit, as part of Worksheet 10:

- The exact line(s) in `broken_hybrid_encrypt.py` where the bug lives, quoted.
- Your proof script + its output (the demonstrated consequence).
- 3–5 sentences: what the vulnerability is, the concrete attack it enables, and why the fix you
  chose (not some other fix) is the right one.
- `fixed_hybrid_encrypt.py` — the corrected implementation, still round-tripping correctly.

## Why this matters

Nonce reuse under AES-GCM is a real, recurring failure mode in production systems and in
AI-generated code specifically — LLMs are pattern-matching on "here is idiomatic AEAD code" and
will confidently produce a fixed or all-zero nonce, a nonce derived from something not actually
unique per message, or (worse) a correct-looking nonce that's silently reused across a whole
session or service restart. A reviewer who only checks "did they use OAEP" and "did they use
GCM" — the two things everyone remembers to check — will approve this file. That's the point of
this exercise: **AI-generated crypto code needs the same scrutiny as AI-generated code anywhere
else, and the failure is rarely in the primitive you already know to be suspicious of.**

## References

- NIST SP 800-38D, *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode
  (GCM) and GMAC* — §8.2, uniqueness requirement on the IV/nonce.
- https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- Joux, *Authentication Failures in NIST version of GCM* (2006) — the original forbidden-attack
  writeup for nonce reuse in GCM.
