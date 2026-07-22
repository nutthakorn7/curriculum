import os

from flask import Flask, jsonify, request

app = Flask(__name__)

FLAG_MONITOR = os.environ.get("FLAG_MONITOR")

ALERT_THRESHOLD = 3

# Simulates a CloudWatch metric-filter counter fed by CloudTrail login events.
# BUG: keyed by (source_ip, username) instead of source_ip alone. An attacker
# rotating usernames from one IP never pushes any single counter to threshold,
# even though the SAME ip is clearly the attacker across all of them.
FAILED_COUNTS = {}

EVENTS = []


@app.route("/login-attempt", methods=["POST"])
def login_attempt():
    body = request.get_json(silent=True) or {}
    username = body.get("username")
    success = bool(body.get("success"))
    source_ip = body.get("source_ip")

    if username is None or source_ip is None:
        return jsonify({"error": "username and source_ip are required"}), 400

    # This line simulates CloudTrail recording the console login event.
    EVENTS.append({"username": username, "success": success, "source_ip": source_ip})

    if success:
        # A successful login resets the per-key failure streak, same as a
        # real CloudWatch metric filter keyed on failed-login events only
        # would stop incrementing once a login succeeds for that key.
        FAILED_COUNTS.pop((source_ip, username), None)
        return jsonify({"status": "ok", "alert": False})

    key = (source_ip, username)
    FAILED_COUNTS[key] = FAILED_COUNTS.get(key, 0) + 1
    count = FAILED_COUNTS[key]

    if count >= ALERT_THRESHOLD:
        resp = {
            "status": "recorded",
            "alert": True,
            "reason": f"{count} failed attempts for username={username!r} from source_ip={source_ip!r}",
        }
        if FLAG_MONITOR:
            resp["flag"] = FLAG_MONITOR
        return jsonify(resp)

    return jsonify(
        {
            "status": "recorded",
            "alert": False,
            "count_for_key": count,
            "note": "counter tracked per (source_ip, username) pair",
        }
    )


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "mode": "vulnerable"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
