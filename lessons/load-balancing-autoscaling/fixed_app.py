import os

from flask import Flask, jsonify, request

from scaler import MAX_INSTANCES, AutoScaler

app = Flask(__name__)

FLAG_SCALING = os.environ.get("FLAG_SCALING", "FLAG{denial_of_wallet_no_throttle}")
API_KEY = os.environ.get("API_KEY", "s3cret-scaling-key")
RATE_LIMIT_MAX_CALLS = int(os.environ.get("RATE_LIMIT_MAX_CALLS", "5"))

scaler = AutoScaler()

# Simplest possible per-caller throttle: a fixed lifetime call-count cap per
# API key, tracked in memory. This is defense in depth on top of auth -- an
# authenticated caller still cannot drive the fleet to max capacity, because
# RATE_LIMIT_MAX_CALLS (5) is far below the ~40 calls needed to reach
# MAX_INSTANCES at UNITS_PER_INSTANCE=10.
call_counts = {}


@app.route("/generate-load", methods=["POST"])
def generate_load():
    supplied_key = request.headers.get("X-Api-Key")
    if supplied_key != API_KEY:
        return jsonify({"error": "Unauthorized", "reason": "missing or invalid X-Api-Key"}), 401

    calls_so_far = call_counts.get(supplied_key, 0)
    if calls_so_far >= RATE_LIMIT_MAX_CALLS:
        return jsonify({
            "error": "TooManyRequests",
            "reason": f"rate limit of {RATE_LIMIT_MAX_CALLS} calls exceeded for this key",
        }), 429

    call_counts[supplied_key] = calls_so_far + 1

    state = scaler.generate_load()
    resp = {"status": "job-accepted", **state}
    if state["current_instances"] >= MAX_INSTANCES:
        resp["flag"] = FLAG_SCALING
    return jsonify(resp), 200


@app.route("/status")
def status():
    return jsonify(scaler.state())


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "mode": "fixed"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
