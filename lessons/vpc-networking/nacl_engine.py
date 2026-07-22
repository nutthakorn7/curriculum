"""Shared minimal Network ACL (NACL) rule-evaluation engine.

Models exactly the one concept this lesson is about: AWS evaluates NACL rules
in ascending rule-number order and STOPS at the first matching rule -- it does
not keep scanning for a "more specific" or "more correct" rule further down.
That means a broad ALLOW placed at a low rule number can make a narrower DENY
at a higher rule number completely unreachable, even though the deny rule is
still sitting there, visibly present, in the rule list.

This is an original simplification for teaching, not AWS code. CIDR matching
here is deliberately simplified (exact string match or "0.0.0.0/0" matches
everything) -- the lesson is about evaluation ORDER, not CIDR arithmetic.
"""

# Each rule: {"rule_number": int, "action": "allow"|"deny", "cidr": str, "port": int}
# Lower rule_number is evaluated first. AWS's real range is 1-32766; we reuse
# that numbering convention here purely for realism.

NACL_RULES_VULNERABLE = [
    # Meant as a narrow "allow app-tier CIDR only" rule but written far too
    # broadly (0.0.0.0/0 = the entire internet) and placed at a LOW rule
    # number, so it is evaluated before the catch-all deny below.
    {"rule_number": 90, "action": "allow", "cidr": "0.0.0.0/0", "port": 5432},
    # Intended as the "secure default": deny everything else on the DB port.
    # Because rule 90 already matched first, this rule is never reached for
    # any traffic on port 5432 -- it is dead code, even though it's present.
    {"rule_number": 100, "action": "deny", "cidr": "0.0.0.0/0", "port": 5432},
]

NACL_RULES_FIXED = [
    # The fix is two changes at once, and both matter:
    #   1. The allow is narrowed from 0.0.0.0/0 down to the specific internal
    #      app-tier CIDR -- it no longer claims to be "the whole internet."
    #   2. That narrowed allow is placed at the LOWER rule number (90), ahead
    #      of the catch-all deny (100). This is the AWS ordering rule in
    #      practice: a specific rule must be evaluated before a broader rule
    #      that would otherwise shadow it, because evaluation stops at the
    #      first match. A deny-all 0.0.0.0/0 placed ahead of ANY allow -- even
    #      a well-scoped one -- would shadow that allow the same way rule #90
    #      shadowed rule #100 in the vulnerable app; the bug is about rule
    #      NUMBER order relative to specificity, not simply "deny should be
    #      first."
    {"rule_number": 90, "action": "allow", "cidr": "10.0.1.0/24", "port": 5432},
    # Catch-all deny for everyone else on the DB port, including the public
    # internet -- now actually reachable, because nothing broader sits ahead
    # of it for traffic that isn't from the internal app tier.
    {"rule_number": 100, "action": "deny", "cidr": "0.0.0.0/0", "port": 5432},
]


def _cidr_matches(cidr, ip):
    """Deliberately simplified CIDR matching for teaching purposes.

    "0.0.0.0/0" matches any IP (the standard "anywhere" CIDR). A CIDR written
    as "10.0.1.0/24" matches any IP that starts with "10.0.1." (simple prefix
    check -- not full subnet-mask arithmetic, which is out of scope here).
    An exact IP with no prefix matches only that literal address.
    """
    if cidr == "0.0.0.0/0":
        return True
    if "/" in cidr:
        network = cidr.split("/")[0]
        prefix = ".".join(network.split(".")[:3])
        return ip.startswith(prefix)
    return ip == cidr


def evaluate(rules, source_ip, port):
    """Walk rules in ascending rule_number order; return the FIRST match.

    This mirrors AWS's own documented behavior: "We evaluate the rules in
    order, starting with the lowest numbered rule ... If the traffic matches
    a rule, the rule is applied and we do not evaluate any additional rules."
    If nothing matches, NACLs implicitly deny (the real default "*" rule).
    """
    for rule in sorted(rules, key=lambda r: r["rule_number"]):
        if rule["port"] == port and _cidr_matches(rule["cidr"], source_ip):
            return rule["action"], rule["rule_number"]
    return "deny", None
