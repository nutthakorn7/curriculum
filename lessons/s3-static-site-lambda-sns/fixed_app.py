import os

from flask import Flask, jsonify, request

app = Flask(__name__)

FLAG_S3SITE = os.environ.get("FLAG_S3SITE", "FLAG{public_putobject_defaces_your_website}")

WEBSITE_FILES = {
    "index.html": "<html><body><h1>Welcome to our official site</h1></body></html>",
}

# Least privilege for static website hosting: the public statement grants
# ONLY GetObject to "*". Anyone's browser can still load the pages — that's
# the whole point of website hosting — but nobody anonymous can write. Site
# content updates happen out-of-band, via an authenticated deploy identity
# (CI role, console upload) that this public-facing bucket policy never
# needs to mention at all.
BUCKET_POLICY = [
    {"principal": "*", "actions": ["GetObject"]},
]


def is_allowed(action):
    for stmt in BUCKET_POLICY:
        if stmt["principal"] == "*" and action in stmt["actions"]:
            return True
    return False


@app.route("/bucket/website/<path:filename>", methods=["GET"])
def get_object(filename):
    if not is_allowed("GetObject"):
        return jsonify({"error": "AccessDenied", "key": filename}), 403
    if filename not in WEBSITE_FILES:
        return jsonify({"error": "NoSuchKey", "key": filename}), 404
    return jsonify({"key": filename, "content": WEBSITE_FILES[filename]})


@app.route("/bucket/website/<path:filename>", methods=["PUT"])
def put_object(filename):
    if not is_allowed("PutObject"):
        return jsonify({"error": "AccessDenied", "key": filename}), 403
    content = (request.get_json(silent=True) or {}).get("content", "")
    WEBSITE_FILES[filename] = content
    return jsonify({"status": "uploaded", "key": filename, "content": content})


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "mode": "fixed"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
