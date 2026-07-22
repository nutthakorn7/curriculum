"""FIXED — Week 2 hash lab. Same endpoints and same users/passwords as vulnerable_app.py,
but passwords are stored with bcrypt (users_fixed.csv: rows of `username,bcrypthash`).

bcrypt is a purpose-built password KDF: each hash embeds a per-user random SALT and a tunable
work factor (cost). Verification uses bcrypt.checkpw (which re-derives with the stored salt/cost
and compares in constant time). Two properties defeat the vulnerable app's attack:
  1. Per-user salt: no single precomputed table (e.g. a wordlist md5 table or a rainbow table)
     cracks all rows at once, and equal passwords no longer produce equal hashes.
  2. Slow-by-design cost: each guess costs ~10s of milliseconds, not microseconds, so a
     dictionary attack is orders of magnitude more expensive per candidate.
The stored hashes are bcrypt strings ($2b$...), NOT md5 hex, so the vulnerable app's fast
md5-precompute-over-the-wordlist technique finds NO match here. See exploit.py's fixed-store
check on :8095. (bcrypt slows an attack; it is not "uncrackable" — a weak password like the
admin's is still recoverable by a slow per-hash bcrypt dictionary, just at hugely higher cost.
The real fix pairs bcrypt with a strong-password policy.)

Endpoints:
  POST /login  {username, password}  -> if bcrypt.checkpw(password, stored) -> session login.
  GET  /admin                        -> if logged in as "admin", return the flag; else 403.
"""
import csv
import os

import bcrypt
from flask import Flask, request, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_KEY", "week2-demo-session-key")

FLAG_HASH = os.environ.get("FLAG_HASH", "FLAG{hash_crack_me}")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users_fixed.csv")


def load_users():
    users = {}
    with open(DB_PATH, newline="") as f:
        for row in csv.DictReader(f):
            users[row["username"]] = row["bcrypthash"].strip()
    return users


USERS = load_users()


@app.route("/")
def index():
    return (
        "Week 2 -- hash lab: leaked password DB (FIXED -- bcrypt, salted + slow)\n"
        "Password store: bcrypt with per-user salt + work factor (users_fixed.csv).\n"
        "Endpoints:\n"
        "  POST /login  {username,password}  verify bcrypt.checkpw(password, stored) -> session login\n"
        "  GET  /admin                       if logged in as 'admin' -> flag; else 403\n"
        "The md5-precompute technique that cracks :8094 finds NO match against these bcrypt hashes.\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    stored = USERS.get(username)
    if stored is None:
        return jsonify({"error": "no such user"}), 403

    # FIXED: bcrypt re-derives with the stored per-user salt + cost and compares in constant time.
    try:
        ok = bcrypt.checkpw(password.encode(), stored.encode())
    except ValueError:
        ok = False
    if ok:
        session["user"] = username
        return jsonify({"ok": True, "user": username})
    return jsonify({"error": "bad password"}), 403


@app.route("/admin")
def admin():
    if session.get("user") == "admin":
        return jsonify({"flag": FLAG_HASH})
    return jsonify({"error": "forbidden -- log in as admin first"}), 403


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8095, debug=False)
