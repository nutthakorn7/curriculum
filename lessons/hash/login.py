#!/usr/bin/env python3
"""Week 2 hash lab -- log in as admin with the password you cracked, then ask for the flag.

Request 2 reuses the login session (its cookie), so it gets the flag. Request 3 starts a new
session with no cookie, so the server answers 403.

Run it inside the lab container:  docker compose exec vulnerable python login.py <password>
"""
import sys

import requests

BASE = "http://localhost:8094"

if len(sys.argv) != 2:
    sys.exit("usage: python login.py <the admin password you cracked>")

s = requests.Session()  # keeps the login cookie between requests
r = s.post(f"{BASE}/login", json={"username": "admin", "password": sys.argv[1]}, timeout=5)
print("1) POST /login as admin               ->", r.status_code, r.json())
r = s.get(f"{BASE}/admin", timeout=5)
print("2) GET /admin, same session           ->", r.status_code, r.json())
r = requests.get(f"{BASE}/admin", timeout=5)
print("3) GET /admin, new session, no cookie ->", r.status_code, r.json())
