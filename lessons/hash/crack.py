#!/usr/bin/env python3
"""Week 2 hash lab -- crack the leaked, unsalted MD5 store with the wordlist ("guess and hash").

The attacker never reverses MD5. They hash every word in wordlist.txt once, then look each leaked
hash up in that table. With no salt, one table checks every row of the leak at the same time.

Run it inside the lab container:  docker compose exec vulnerable python crack.py
"""
import csv
import hashlib
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "users_vulnerable.csv"), newline="") as f:
    leaked = {row["username"]: row["md5hex"].strip() for row in csv.DictReader(f)}
with open(os.path.join(HERE, "wordlist.txt")) as f:
    words = [line.strip() for line in f if line.strip()]

start = time.perf_counter()
table = {hashlib.md5(w.encode()).hexdigest(): w for w in words}  # hash every guess once
cracked = {user: table[h] for user, h in leaked.items() if h in table}
ms = (time.perf_counter() - start) * 1000

print(f"Hashed {len(words)} guesses with MD5 and checked {len(leaked)} leaked rows in {ms:.2f} ms")
for user in leaked:
    print(f"  {user:<6} -> {cracked.get(user, '(not in the wordlist)')}")
print(f"Cracked {len(cracked)} of {len(leaked)} users with ONE list (no salt, so every row is checked at once)")
