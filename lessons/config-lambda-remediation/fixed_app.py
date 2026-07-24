import os

from flask import Flask, jsonify

from remediation_engine import ALLOWED_PORTS, remediate_correct, seed_rules

app = Flask(__name__)

DANGEROUS_PORTS = {22, 3389}

security_group = {"rules": seed_rules()}


@app.route("/security-group", methods=["GET"])
def get_security_group():
    rules = security_group["rules"]
    dangerous = [r for r in rules if r["port"] in DANGEROUS_PORTS and r["cidr"] == "0.0.0.0/0"]
    # Control app: it NEVER emits FLAG_REMEDIATE. The flag is evidence of the vulnerable
    # app's inverted-remediation bug (a dangerous rule surviving a remediation attempt).
    # The correctly-fixed app has no such bug, so it has no flag to return — emitting one
    # here (even gated) would let a student harvest the evidence flag without exploiting
    # anything.
    return jsonify({"rules": rules, "dangerous_rules_present": bool(dangerous)})


@app.route("/reset", methods=["POST"])
def reset():
    security_group["rules"] = seed_rules()
    return jsonify({"status": "reset", "rules": security_group["rules"]})


@app.route("/remediate", methods=["POST"])
def remediate():
    before = security_group["rules"]
    # Correct logic: revoke any inbound rule whose port is NOT on the
    # allowlist, keeping only the allowed (80/443) rules.
    after = remediate_correct(before, ALLOWED_PORTS)
    security_group["rules"] = after
    return jsonify({"status": "remediated", "before": before, "after": after, "mode": "fixed"})


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "mode": "fixed"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
