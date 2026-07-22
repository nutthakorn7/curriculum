import os
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

FLAG_EC2 = os.environ.get("FLAG_EC2", "FLAG{ssrf_steals_the_instance_role}")

FAKE_CREDENTIALS = {
    "Code": "Success",
    "LastUpdated": "2024-01-01T00:00:00Z",
    "Type": "AWS-HMAC",
    "AccessKeyId": "ASIAFAKEACCESSKEYID00",
    "SecretAccessKey": "fAkE/SecretAccessKey/ThatLooksReal000000",
    "Token": "FAKE.SESSION.TOKEN.FOR.TEACHING.PURPOSES.ONLY",
    "Expiration": "2024-01-01T06:00:00Z",
    "flag": FLAG_EC2,
}

# Hosts that must never be reachable via the fetch-preview feature: the
# link-local metadata address a real EC2 instance would see (169.254.169.254),
# plus loopback/self hosts an attacker could use to reach this same app's own
# metadata route instead (localhost/127.0.0.1/0.0.0.0), which is the form the
# self-contained version of this exploit actually takes.
BLOCKED_HOSTS = {"169.254.169.254", "localhost", "127.0.0.1", "0.0.0.0"}
BLOCKED_METADATA_PREFIX = "/latest/meta-data"


def is_blocked(url):
    try:
        parsed = urlparse(url)
    except ValueError:
        return True

    if parsed.scheme not in ("http", "https"):
        return True

    hostname = (parsed.hostname or "").lower()
    if hostname in BLOCKED_HOSTS:
        return True

    # Belt-and-suspenders: even if a caller reaches this app through some
    # other hostname/alias, never fetch a path that looks like the instance
    # metadata credentials tree.
    if parsed.path.startswith(BLOCKED_METADATA_PREFIX):
        return True

    return False


@app.route("/latest/meta-data/iam/security-credentials/AppRole")
def metadata_credentials():
    return jsonify(FAKE_CREDENTIALS)


@app.route("/fetch-preview", methods=["POST"])
def fetch_preview():
    url = (request.get_json(silent=True) or {}).get("url")
    if not url:
        return jsonify({"error": "missing 'url'"}), 400

    # FIX: reject link-local / loopback-adjacent internal targets and any
    # metadata-shaped path before ever making the outbound request.
    if is_blocked(url):
        return jsonify({"error": "blocked", "reason": "internal/metadata URL not allowed", "url": url}), 403

    try:
        upstream = requests.get(url, timeout=3)
    except requests.RequestException as exc:
        return jsonify({"error": "fetch failed", "detail": str(exc)}), 502

    return jsonify(
        {
            "status": "fetched",
            "url": url,
            "status_code": upstream.status_code,
            "body": upstream.text,
        }
    )


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "mode": "fixed"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
