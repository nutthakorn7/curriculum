"""
Deliberately INSECURE sample for Week 2 scanning practice.
Do NOT copy these patterns into real code. Find them with SAST + secret scanning.
"""
import sqlite3, hashlib, subprocess
from flask import Flask, request

app = Flask(__name__)

# CWE-798: hardcoded credentials / secret  (Gitleaks should flag this)
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DB_PASSWORD = "SuperSecret123!"

@app.route("/user")
def user():
    name = request.args.get("name", "")
    con = sqlite3.connect("app.db")
    # CWE-89: SQL injection (string formatting into query)
    q = "SELECT * FROM users WHERE name = '%s'" % name
    return str(con.execute(q).fetchall())

@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # CWE-78: OS command injection (shell=True with user input)
    return subprocess.check_output("ping -c 1 " + host, shell=True)

def store_password(pw):
    # CWE-327: weak hash for passwords
    return hashlib.md5(pw.encode()).hexdigest()

if __name__ == "__main__":
    app.run(debug=True)  # CWE-489: debug mode in production
