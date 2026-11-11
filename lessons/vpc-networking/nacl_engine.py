"""Shared minimal Network ACL (NACL) rule-evaluation engine.

Models exactly the one concept this lesson is about: AWS evaluates NACL rules
in ascending rule-number order and STOPS at the first matching rule -- it does
not keep scanning for a "more specific" or "more correct" rule further down.
That means a broad ALLOW placed at a low rule number can make a later DENY
at a higher rule number completely unreachable, even though the deny rule is
still sitting there, visibly present, in the rule list.

This is an original simplification for teaching, not AWS code. It evaluates
one inbound IPv4 source and one exact destination port; it does not model
protocols, return traffic, routing, or security groups.
"""

from ipaddress import IPv4Address, IPv4Network, AddressValueError

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
    # Only the allow CIDR changes between the two apps; both rule numbers
    # stay the same. Narrowing #90 lets the unchanged #100 catch external
    # traffic. A catch-all deny before this narrow allow would instead
    # shadow legitimate app-tier traffic. The general lesson is to order
    # specific rules before a broad catch-all.
    {"rule_number": 90, "action": "allow", "cidr": "10.0.1.0/24", "port": 5432},
    # Catch-all deny for everyone else on the DB port, including the public
    # internet -- now actually reachable, because nothing broader sits ahead
    # of it for traffic that isn't from the internal app tier.
    {"rule_number": 100, "action": "deny", "cidr": "0.0.0.0/0", "port": 5432},
]


def valid_packet(source_ip, port):
    """Accept only an IPv4 source and an integer destination port."""
    if not isinstance(source_ip, str) or not isinstance(port, int) or isinstance(port, bool):
        return False
    if not 0 <= port <= 65535:
        return False
    try:
        IPv4Address(source_ip)
    except AddressValueError:
        return False
    return True


def _cidr_matches(cidr, ip):
    """Check the actual IPv4 CIDR, not a textual prefix."""
    return IPv4Address(ip) in IPv4Network(cidr, strict=False)


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
