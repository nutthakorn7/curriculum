import os

from flask import Flask, jsonify, request

app = Flask(__name__)

FLAG_S3SITE = os.environ.get("FLAG_S3SITE", "FLAG{public_putobject_defaces_your_website}")

# A single S3-like bucket configured for static website hosting, seeded with
# the site's homepage — exactly what you'd see right after "Properties >
# Static website hosting > Enable" in the real console.
WEBSITE_FILES = {
    "index.html": "<html><body><h1>Welcome to our official site</h1></body></html>",
}

# The bucket's resource ("bucket") policy. Static website hosting requires a
# public-read statement so anyone's browser can GET the pages — that part is
# the correct, intended pattern. The bug: whoever wrote this policy scoped
# "Principal": "*" to BOTH GetObject and PutObject, presumably by copying a
# read/write template meant for an authenticated app role and forgetting to
# narrow it back down for the public statement. Now anyone on the internet,
# with no credentials at all, can overwrite any object in the site — including
# index.html.
BUCKET_POLICY = [
    {"principal": "*", "actions": ["GetObject", "PutObject"]},
]


def is_allowed(action):
    """Original, minimal stand-in for S3 bucket-policy evaluation: does any
    statement's principal/action match this request? Every caller here is
    anonymous ("*") — there is no IAM identity in this scenario at all, which
    is exactly what makes an over-broad Principal: "*" statement dangerous:
    it is the *only* thing standing between the object and the public.
    """
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
    resp = {"status": "uploaded", "key": filename, "content": content}
    if filename == "index.html":
        resp["flag"] = FLAG_S3SITE
    return jsonify(resp)


@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "mode": "vulnerable"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
