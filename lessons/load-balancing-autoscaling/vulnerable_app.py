import os

from flask import Flask, jsonify

from scaler import MAX_INSTANCES, AutoScaler

app = Flask(__name__)

FLAG_SCALING = os.environ.get("FLAG_SCALING", "FLAG{denial_of_wallet_no_throttle}")

scaler = AutoScaler()


@app.route("/generate-load", methods=["POST"])
def generate_load():
    # BUG: no authentication check, no per-caller rate limit at all. Anyone,
    # anonymous, can call this in a tight loop and force the fleet to
    # max capacity almost instantly -- each simulated instance costs money,
    # so this is an economic ("denial of wallet") attack, not just a DoS.
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
    return jsonify({"status": "ok", "mode": "vulnerable"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
