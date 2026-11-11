import os

from flask import Flask, jsonify, request

from nacl_engine import NACL_RULES_FIXED as NACL_RULES
from nacl_engine import evaluate, valid_packet

app = Flask(__name__)

FLAG_NACL = os.environ.get("FLAG_NACL", "FLAG{low_numbered_allow_shadows_the_deny}")


@app.route("/check-access", methods=["POST"])
def check_access():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "JSON object required"}), 400
    source_ip = body.get("source_ip")
    port = body.get("port")
    if source_ip is None or port is None:
        return jsonify({"error": "source_ip and port are required"}), 400
    if not valid_packet(source_ip, port):
        return jsonify({"error": "source_ip must be IPv4 and port must be an integer from 0 to 65535"}), 400

    action, matched_rule_number = evaluate(NACL_RULES, source_ip, port)
    resp = {
        "action": action,
        "matched_rule_number": matched_rule_number,
        "source_ip": source_ip,
        "port": port,
    }
    # No flag here by design: this is the control app. The ordered NACL below makes
    # an external allow on 5432 unreachable, and the course rule is that the fixed app
    # never emits a flag at all. The shared demo marker is not identity
    # evidence; grade the submitted request, response and explanation.
    return jsonify(resp)


@app.route("/rules", methods=["GET"])
def list_rules():
    return jsonify(sorted(NACL_RULES, key=lambda r: r["rule_number"]))


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "mode": "fixed"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
