"""Shared minimal auto-remediation engine for a simulated security group.

Models exactly the one concept this lesson is about: an AWS Config rule flags
a security group as NON_COMPLIANT (e.g. an inbound rule open to the world on
a disallowed port), and a Lambda-style remediation function is supposed to
revoke every inbound rule whose port is NOT on the allowed list, keeping only
the allowed ones. This is an original simplification for teaching, not AWS
code — no AWS Config or Lambda SDK calls happen here, the "compliance check"
and "remediation" are just plain Python over an in-memory list of rules.
"""

ALLOWED_PORTS = {80, 443}


def seed_rules():
    """A fresh, deterministic starting rule set for each demo run.

    Two legitimate web rules (80/443) plus one dangerous rule: SSH (22) open
    to the entire internet — exactly the kind of finding an AWS Config rule
    like restricted-ssh would flag as NON_COMPLIANT.
    """
    return [
        {"port": 80, "cidr": "0.0.0.0/0"},
        {"port": 443, "cidr": "0.0.0.0/0"},
        {"port": 22, "cidr": "0.0.0.0/0"},
    ]


def remediate_correct(rules, allowed_ports=ALLOWED_PORTS):
    """Correct logic: KEEP only rules whose port is in the allowed set.

    Equivalently: revoke (drop) any rule whose port is NOT allowed. This is
    the behavior an AWS Config auto-remediation Lambda should implement —
    close everything that isn't explicitly permitted, keep only what's on
    the allowlist.
    """
    return [rule for rule in rules if rule["port"] in allowed_ports]


def remediate_inverted(rules, allowed_ports=ALLOWED_PORTS):
    """Buggy logic: the keep/revoke condition is inverted.

    Instead of keeping only allowed-port rules, this keeps only the
    *disallowed* ones — i.e. it revokes exactly the rules it should have
    kept (80/443) and leaves everything else (like SSH-from-anywhere)
    untouched. Net effect: legitimate web traffic gets cut off, while the
    dangerous rule survives — the exact opposite of the intended
    remediation. Note this is a one-token flip (`not in` vs `in`) relative
    to `remediate_correct`, and it raises no exception — it looks like the
    automation "ran successfully."
    """
    return [rule for rule in rules if rule["port"] not in allowed_ports]
