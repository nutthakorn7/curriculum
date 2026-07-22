import os

from flask import Flask, jsonify, request

app = Flask(__name__)

FLAG_MONITOR = os.environ.get("FLAG_MONITOR")

ALERT_THRESHOLD = 3

# Fix: keyed by source_ip ALONE. The failed-login streak accumulates for the
# attacking IP regardless of which username it targets — matching the correct
# aggregation key for a password-spray / brute-force detective control.
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
        FAILED_COUNTS.pop(source_ip, None)
        return jsonify({"status": "ok", "alert": False})

    key = source_ip
    FAILED_COUNTS[key] = FAILED_COUNTS.get(key, 0) + 1
    count = FAILED_COUNTS[key]

    if count >= ALERT_THRESHOLD:
        resp = {
            "status": "recorded",
            "alert": True,
            "reason": f"{count} failed attempts from source_ip={source_ip!r} (usernames vary)",
        }
        if FLAG_MONITOR:
            resp["flag"] = FLAG_MONITOR
        return jsonify(resp)

    return jsonify(
        {
            "status": "recorded",
            "alert": False,
            "count_for_key": count,
            "note": "counter tracked per source_ip only",
        }
    )


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "mode": "fixed"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
