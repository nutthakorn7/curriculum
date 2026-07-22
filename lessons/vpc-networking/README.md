# {{ slot_label }} — VPC Networking (Public/Private Subnets, NAT Gateway, Security Groups vs. NACLs)

**Topic (source):** AWS Academy Cloud Foundations' VPC networking module (public/private
subnets, NAT gateway, security groups, network ACLs), described here in our own words —
**not** copied from any AWS Academy file. **Kind:** HYBRID (conceptual essay + a small,
from-scratch lab on one specific NACL misconfiguration).
**Concepts:** stateful vs. stateless traffic filtering, NAT gateway purpose for private
subnets, Network ACL rule evaluation order · **Analogous CWE:** CWE-863 (Incorrect
Authorization) / CWE-284 (Improper Access Control) — the access decision is technically
"authorized" by a rule that exists, but the wrong rule wins because of ordering, not because
either rule's content is individually wrong.

## ✅ This lesson — what to do
1. **Before class** — complete the real AWS Academy VPC networking lab in your Learner Lab
   sandbox (creating public/private subnets, a NAT gateway, security groups, and a custom
   network ACL) — that's still where you learn the actual AWS console UI and see NAT gateway
   routing live.
2. **This add-on lab (45–60 min)** — a local, from-scratch simulation of one specific,
   easy-to-miss Network ACL bug: rule *number* order, not just rule *content*, decides the
   outcome. Kickoff: `docker compose up -d`.
3. **Submit** — worksheet + flag → Classroom.

## Objectives
- State the difference between **security groups** (stateful, instance-level, allow-only) and
  **network ACLs** (stateless, subnet-level, allow **and** deny, evaluated in strict rule-number
  order).
- Explain precisely why AWS Network ACLs evaluate rules **in ascending rule-number order and
  stop at the first match** — and why that means a broad rule at a low number can make a
  narrower, more "correct-looking" rule at a higher number **completely unreachable**, even
  though it is still sitting there in the rule list.
- Explain, in general terms, why a NAT gateway lets instances in a private subnet initiate
  outbound connections without exposing them to unsolicited inbound connections from the
  internet.

## 🔢 Signature exercise — "The Deny Rule That Never Runs"
A simplified Network ACL rule evaluator: each app holds an ordered list of
`{"rule_number": int, "action": "allow"|"deny", "cidr": str, "port": int}` rules for a
database's inbound traffic on port `5432`. `POST /check-access {"source_ip", "port"}` walks
the rules **in ascending `rule_number` order** and returns the action of the **first** rule
whose `cidr`/`port` matches — exactly how AWS's own NACL evaluation works.

| Service | Port | Rule #90 | Rule #100 | External IP on port 5432 |
|---|---|---|---|---|
| `vulnerable_app.py` | `:8113` | `allow 0.0.0.0/0` | `deny 0.0.0.0/0` | **allowed** (rule #90 wins) |
| `fixed_app.py` | `:8114` | `allow 10.0.1.0/24` | `deny 0.0.0.0/0` | **denied** (rule #100 wins) |

**Why it's exciting:** on the vulnerable app, a "secure default" deny-all rule for the database
port *visibly exists* at rule #100 — anyone reviewing the rule list would see it and might
assume the database is locked down. It never actually runs. Rule #90's broad `allow 0.0.0.0/0`
(almost certainly meant to mean "our app tier can reach the DB," but written far too broadly
and placed too early) matches first, and NACL evaluation **stops at the first match**. The
deny-all rule at #100 is dead code.

The fix is not "swap allow and deny" — it's **two changes together**: scope the allow down to
the actual internal CIDR that needs it (`10.0.1.0/24`, not `0.0.0.0/0`), *and* make sure that
narrower rule sits at a **lower** rule number than the broad catch-all deny, so the specific
case is decided before the general case ever gets a chance to match.

1. **Baseline:** `GET /rules` on either app to see the ordered rule list.
2. **The real question:** `POST /check-access` with an external source IP
   (`203.0.113.55`, a public documentation-range address) on port `5432`.
3. On `:8113` (vulnerable) this returns `{"action": "allow", ...}` **and a flag** — rule #90
   matched first, so the deny-all at #100 was never reached.
4. **Confirm the fix:** the identical request against `:8114` (fixed) returns
   `{"action": "deny"}` — no flag — because the catch-all deny at #100 is now reachable for any
   traffic that isn't from the internal CIDR. (A request from inside `10.0.1.0/24` is still
   correctly allowed — the fix does not lock out legitimate traffic.)

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build   # vulnerable_app.py on :8113, fixed_app.py on :8114
pip install requests           # once, on the host
python exploit.py
```
Expect two `PASS` lines and exit `0`: an external IP allowed + flag on `:8113`, the identical
external IP denied (no flag) on `:8114`.

**Verified:** `docker compose up -d --build` was run on this machine; `exploit.py` ran from the
host against the published ports. Real captured output:
```
=== VULNERABLE (allow-all at #90 shadows deny-all at #100) (http://localhost:8113) ===
[*] rule set (ascending order) -> [{'action': 'allow', 'cidr': '0.0.0.0/0', 'port': 5432, 'rule_number': 90}, {'action': 'deny', 'cidr': '0.0.0.0/0', 'port': 5432, 'rule_number': 100}]
[*] external IP 203.0.113.55 -> port 5432 -> 200 {'action': 'allow', 'flag': 'FLAG{low_numbered_allow_shadows_the_deny}', 'matched_rule_number': 90, 'port': 5432, 'source_ip': '203.0.113.55'}
PASS: external IP was ALLOWED to the DB port on the vulnerable app (rule #90 matched first), flag = FLAG{low_numbered_allow_shadows_the_deny}

=== FIXED (scoped allow at #90 evaluated first, catch-all deny at #100) (http://localhost:8114) ===
[*] rule set (ascending order) -> [{'action': 'allow', 'cidr': '10.0.1.0/24', 'port': 5432, 'rule_number': 90}, {'action': 'deny', 'cidr': '0.0.0.0/0', 'port': 5432, 'rule_number': 100}]
[*] external IP 203.0.113.55 -> port 5432 -> 200 {'action': 'deny', 'matched_rule_number': 100, 'port': 5432, 'source_ip': '203.0.113.55'}
PASS: external IP correctly DENIED to the DB port on the fixed app (rule #100 matched first), no flag
```
Exit code `0`. Negative/positive controls confirmed separately: a request from inside the
internal CIDR (`10.0.1.25`) on port `5432` is correctly **allowed** on the fixed app (the fix
does not break legitimate access); a request on an unrelated port (`22`) with no matching rule
falls through to the implicit default **deny** on both apps, matching AWS's own NACL behavior
of an implicit deny-all when nothing matches.

Per-student flag: run `python3 instructor/seed_flags.py env <STUDENT_ID>` — this course's own
`instructor/seed_flags.py` already exists and its `CHALLENGES` list already includes `"nacl"`.
Without it, `FLAG_NACL` defaults to `FLAG{low_numbered_allow_shadows_the_deny}` and can be
overridden: `FLAG_NACL=FLAG{...} docker compose up`.

**Evidence artifact.** The attributable evidence is the captured `flag` value returned by the
*vulnerable* app's `/check-access` response for an external IP on port 5432. The fixed app
never returns it for that same request. Submitting another student's flag is a violation.

## Deliverable
The captured flag + the exact request (`source_ip`, `port`) that produced it + a one-paragraph
explanation of why a visibly-present "deny all" rule at a higher rule number can still be
completely unreachable — it's not that the deny rule is wrong, it's that a broader rule ahead
of it already decided the outcome.

## References
- AWS VPC documentation — *Control subnet traffic with network access control lists*: "We
  evaluate the rules in order, starting with the lowest numbered rule ... If the traffic
  matches a rule, the rule is applied and we do not evaluate any additional rules." (publicly
  available, general concept — no AWS Academy file used or copied).
- AWS VPC documentation — *Compare security groups and network ACLs*: security groups
  "evaluate all rules before deciding whether to allow traffic" (stateful, allow-only);
  network ACLs "evaluate rules in ascending order until a match ... is found" (stateless,
  allow and deny).
- AWS VPC documentation — *NAT gateways*: instances in a private subnet can connect outbound
  through a NAT gateway, but "external services can't initiate a connection with those
  instances."
