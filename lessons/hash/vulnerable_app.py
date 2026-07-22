"""Deliberately INSECURE — Week 2 hash lab. Sandbox only; for authorized lab use.

Passwords are stored as UNSALTED MD5 (users_vulnerable.csv: rows of `username,md5hex`).
MD5 is fast and unsalted, so a leaked copy of this "database" is trivially cracked with a
dictionary: the attacker precomputes md5(word) for each word in a wordlist and looks for a
matching stored hash. No per-user salt means one precomputed table cracks every row at once,
and identical passwords produce identical hashes. See exploit.py for the crack + login.
Compare with fixed_app.py (bcrypt, salted + slow) on :8095.

Endpoints:
  POST /login  {username, password}  -> if md5(password) == stored hash, log the session in.
  GET  /admin                        -> if logged in as "admin", return the flag; else 403.
"""
import csv
import hashlib
import os

from flask import Flask, request, session, jsonify

app = Flask(__name__)
# Needed so Flask's signed session cookie works. Not the subject of this lab (it protects the
# SESSION, not the password store) — the vulnerability here is the MD5 password store below.
app.secret_key = os.environ.get("SESSION_KEY", "week2-demo-session-key")

FLAG_HASH = os.environ.get("FLAG_HASH", "FLAG{hash_crack_me}")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users_vulnerable.csv")


def load_users():
    users = {}
    with open(DB_PATH, newline="") as f:
        for row in csv.DictReader(f):
            users[row["username"]] = row["md5hex"].strip()
    return users


USERS = load_users()


@app.route("/")
def index():
    return (
        "Week 2 -- hash lab: leaked weakly-hashed password DB (VULNERABLE; sandbox only)\n"
        "Password store: UNSALTED MD5 (users_vulnerable.csv).\n"
        "Endpoints:\n"
        "  POST /login  {username,password}  verify md5(password) == stored hash -> session login\n"
        "  GET  /admin                       if logged in as 'admin' -> flag; else 403\n",
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

    # VULNERABLE: fast, unsalted MD5. A leaked `stored` is crackable offline in milliseconds.
    if hashlib.md5(password.encode()).hexdigest() == stored:
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
    app.run(host="0.0.0.0", port=8094, debug=False)
