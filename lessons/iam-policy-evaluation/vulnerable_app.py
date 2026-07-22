import os
import secrets

from flask import Flask, jsonify, request

from policy_engine import BUCKETS_VULNERABLE as BUCKETS
from policy_engine import is_allowed

app = Flask(__name__)

FLAG_IAM = os.environ.get("FLAG_IAM", "FLAG{wildcard_principal_grants_the_world}")

KNOWN_ROLES = {"devuser", "BucketsAccessRole"}
ISSUED_TOKENS = {}
OBJECTS = {name: {} for name in BUCKETS}


def principal_from_request():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[len("Bearer ") :]
        role = ISSUED_TOKENS.get(token)
        if role:
            return role
    return "anonymous"


@app.route("/assume-role", methods=["POST"])
def assume_role():
    role = (request.get_json(silent=True) or {}).get("role")
    if role not in KNOWN_ROLES:
        return jsonify({"error": f"unknown role '{role}'"}), 400
    token = secrets.token_hex(16)
    ISSUED_TOKENS[token] = role
    return jsonify({"token": token, "role": role})


@app.route("/bucket/<name>/object/<path:filename>", methods=["PUT"])
def put_object(name, filename):
    principal = principal_from_request()
    if not is_allowed(BUCKETS, principal, name, "put"):
        return jsonify({"error": "AccessDenied", "principal": principal, "bucket": name}), 403
    content = (request.get_json(silent=True) or {}).get("content", "")
    OBJECTS.setdefault(name, {})[filename] = content
    resp = {"status": "uploaded", "principal": principal, "bucket": name, "key": filename}
    if name == "bucket3":
        resp["flag"] = FLAG_IAM
    return jsonify(resp)


@app.route("/bucket/<name>/object/<path:filename>", methods=["GET"])
def get_object(name, filename):
    principal = principal_from_request()
    if not is_allowed(BUCKETS, principal, name, "get"):
        return jsonify({"error": "AccessDenied", "principal": principal, "bucket": name}), 403
    if filename not in OBJECTS.get(name, {}):
        return jsonify({"error": "NoSuchKey"}), 404
    return jsonify({"bucket": name, "key": filename, "content": OBJECTS[name][filename]})


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "mode": "vulnerable"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
