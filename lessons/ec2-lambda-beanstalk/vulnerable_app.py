import os

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

FLAG_EC2 = os.environ.get("FLAG_EC2", "FLAG{ssrf_steals_the_instance_role}")

# Simulates the fake temporary credentials AWS's real Instance Metadata
# Service (IMDS) would hand back for an EC2 instance's attached IAM instance
# role, at http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name>.
# On a real instance this link-local address is only reachable from processes
# running ON that instance — it is not a route that exists on the public
# internet or from another host. We can't simulate that network boundary with
# a plain Flask route reachable from the host, so the exploit for this lesson
# always goes THROUGH /fetch-preview (never a direct hit on this route) to
# keep the demonstrated attack path faithful to the real SSRF class: the
# attacker never talks to the metadata endpoint directly, they trick a
# server-side feature that already has access into fetching it on their
# behalf. See README.md's "Simulation limits" section.
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


@app.route("/latest/meta-data/iam/security-credentials/AppRole")
def metadata_credentials():
    """Stand-in for the real EC2 IMDS credentials endpoint for an attached
    IAM instance role named 'AppRole'. Legitimately, only code running on the
    instance itself should ever be able to reach this."""
    return jsonify(FAKE_CREDENTIALS)


@app.route("/fetch-preview", methods=["POST"])
def fetch_preview():
    """A 'link preview' / webhook-test style feature: fetch a user-supplied
    URL server-side and return its body. This is the SSRF-prone pattern —
    the server acts as an open proxy for whatever URL the caller names,
    including the app's own internal metadata route."""
    url = (request.get_json(silent=True) or {}).get("url")
    if not url:
        return jsonify({"error": "missing 'url'"}), 400

    # BUG: no validation at all — no allowlist, no blocklist. Any scheme,
    # any host, any path — including this same app's own metadata endpoint —
    # is fetched as-is. Compare fixed_app.py's is_blocked() check.
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
    return jsonify({"status": "ok", "mode": "vulnerable"})


if __name__ == "__main__":
    # threaded=True is required: /fetch-preview can call back into this same
    # process's /latest/meta-data route (self-SSRF). A single-threaded dev
    # server would deadlock on that nested request.
    app.run(host="0.0.0.0", port=5000, threaded=True)
