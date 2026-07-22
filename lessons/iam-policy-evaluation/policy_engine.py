"""Shared minimal IAM-style policy evaluation engine.

Models exactly the one concept this lesson is about: a resource-based policy
(attached to a bucket) can grant access to a principal even when that
principal's identity-based policy alone would not — and if a resource policy's
`Principal` is scoped too broadly, it grants that access to far more callers
than intended. This is an original simplification for teaching, not AWS code.
"""

BUCKETS_VULNERABLE = {
    "bucket1": {
        "resource_policy": [
            {"principal": "BucketsAccessRole", "actions": ["get"]},
        ],
    },
    "bucket2": {
        "resource_policy": [
            {"principal": "BucketsAccessRole", "actions": ["get", "put"]},
        ],
    },
    # The bug: Principal "*" was meant to mean "any role in this account" but
    # actually means "any caller, including nobody assuming a role at all."
    "bucket3": {
        "resource_policy": [
            {"principal": "*", "actions": ["get", "put"]},
        ],
    },
}

BUCKETS_FIXED = {
    "bucket1": {
        "resource_policy": [
            {"principal": "BucketsAccessRole", "actions": ["get"]},
        ],
    },
    "bucket2": {
        "resource_policy": [
            {"principal": "BucketsAccessRole", "actions": ["get", "put"]},
        ],
    },
    # Least privilege: scoped to the one legitimate role, get-only. No
    # principal — including BucketsAccessRole — can put to bucket3.
    "bucket3": {
        "resource_policy": [
            {"principal": "BucketsAccessRole", "actions": ["get"]},
        ],
    },
}

# devuser's identity-based policy: explicitly does NOT include get/put on any
# bucket (matches the real lesson's "Developer group policy has no
# s3:GetObject/PutObject" setup) — access can only come from a resource policy.
IDENTITY_POLICY = {
    "devuser": {"actions": []},
    "BucketsAccessRole": {"actions": []},
}


def is_allowed(buckets, principal, bucket_name, action):
    bucket = buckets.get(bucket_name)
    if bucket is None:
        return False
    for stmt in bucket["resource_policy"]:
        if stmt["principal"] in ("*", principal) and action in stmt["actions"]:
            return True
    identity = IDENTITY_POLICY.get(principal, {"actions": []})
    return action in identity["actions"]
