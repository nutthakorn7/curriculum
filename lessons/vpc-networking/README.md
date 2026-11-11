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
1. **Before class** — complete the real AWS Academy VPC networking labs in your Learner Lab
   sandbox (Cloud Foundations Module 5, *Build Your VPC and Launch a Web Server*, and Cloud
   Security Foundations Module 4, *Securing VPC Resources by Using Security Groups*: public/private
   subnets, a NAT gateway, security groups and network ACLs) — that's still where you learn the
   actual AWS console UI and see NAT gateway routing live.
2. **This add-on lab (45–60 min)** — a local, from-scratch simulation of one specific,
   easy-to-miss Network ACL bug: rule *number* order, not just rule *content*, decides the
   outcome. Follow **Step-by-step** below (kickoff: `docker compose up -d --build`).
3. **Submit** — worksheet evidence and explanation → see [SUBMISSION.md](../../SUBMISSION.md).

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

## Step-by-step (copy these commands)
**First, get this lab onto your computer.** You need your own copy of the course files. You download them once, then update them each
time. Open a terminal (Terminal on macOS or Linux, **Git Bash** on Windows) and do
A, B and C in order. You installed Git in the Week 01 setup; if `git` is "not found", do that
setup first.

A. **Download the course files (first time only).** Skip this if you already did it in Week 01.
   ```bash
   cd ~
   git clone https://github.com/nutthakorn7/cloud-infrastructure-security.git
   ```
   You should see `Cloning into 'cloud-infrastructure-security'...` and no error. If it says
   `already exists`, you have the files already: go on to B.

B. **Get the newest version (every time).** The course files change during the term, so do this
   even if you downloaded them last week. Your answers stay in Classroom; update the repo before each lab.
   ```bash
   cd ~/cloud-infrastructure-security
   git pull
   ```
   You should see `Already up to date.` or a list of changed files. If you see
   `No such file or directory`, your copy is in another folder: do A to make a new one here. If you
   see `Your local changes to the following files would be overwritten`, stop and ask the
   instructor for help syncing your copy. Do not discard your local changes blindly.

C. **Go into this lab's folder and check it.**
   ```bash
   cd {{ labpath }}
   ls
   ```
   You should see `README.md`, `worksheet.md` and `docker-compose.yml` among the files. Every
   command below runs from this folder. If you open a new terminal later, do B and C again first.

Run these in a terminal inside this lab folder: Terminal on macOS or Linux, or **Git Bash** on
Windows (it comes with Git). Each step says what you should see. The apps only answer questions;
nothing you send changes them, so you can repeat any step.

0. **No private setup:** this public lab runs without a personal `.env` or an instructor message.
   The `flag` field is a shared demonstration marker, not proof of identity. Submit the complete
   request and vulnerable/fixed responses plus your explanation.

1. **Start both apps.** The first run downloads and builds the image, so it can take a few
   minutes.
   ```bash
   docker compose up -d --build
   ```
   When it finishes, wait about 10 seconds for the apps to start.
2. **Check that both apps are running.** If you see only `HTTP 000`, the apps are still starting:
   wait a few seconds and run the command again.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8113/ping
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8114/ping
   ```
   You should see `{"mode":"vulnerable","status":"ok"}` and then `{"mode":"fixed","status":"ok"}`,
   each followed by `HTTP 200`.
3. **Read the rule list of each app.** Rules are checked from the lowest `rule_number` up, and
   the first rule that matches decides.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8113/rules
   curl -s -w 'HTTP %{http_code}\n' http://localhost:8114/rules
   ```
   Both lists have rule `90` (allow) and rule `100` (deny 0.0.0.0/0) for port 5432. On the
   vulnerable app (`:8113`) rule 90 allows `"cidr":"0.0.0.0/0"` (everyone); on the fixed app
   (`:8114`) it allows only `"cidr":"10.0.1.0/24"` (the internal app tier). Copy both lists into
   the worksheet.
4. **The attack:** ask the vulnerable app whether an outside address, `203.0.113.55`, may reach
   the database port 5432.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8113/check-access -H 'Content-Type: application/json' -d '{"source_ip": "203.0.113.55", "port": 5432}'
   ```
   You should see `"action":"allow"`, `"matched_rule_number":90`, `"flag":"FLAG{...}"` and
   `HTTP 200`. Rule 90 matched first, so the deny rule 100 never ran. Record the full response
   into the worksheet, together with the whole `curl` command you sent.
5. **The same request on the fixed app:**
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8114/check-access -H 'Content-Type: application/json' -d '{"source_ip": "203.0.113.55", "port": 5432}'
   ```
   You should see `"action":"deny"` and `"matched_rule_number":100`, with no flag. (`HTTP 200`
   only means the app answered your question.)
6. **The fix still lets the app tier in:** ask the fixed app about an internal address,
   `10.0.1.25`.
   ```bash
   curl -s -w 'HTTP %{http_code}\n' -X POST http://localhost:8114/check-access -H 'Content-Type: application/json' -d '{"source_ip": "10.0.1.25", "port": 5432}'
   ```
   You should see `"action":"allow"` and `"matched_rule_number":90`. Legitimate traffic still
   gets through.
7. **Stop the apps when you finish.**
   ```bash
   docker compose down
   ```

If a step doesn't match, check that Docker Desktop is running and that you are in this lab folder,
then ask in class.

## Run it
```bash
cd {{ labpath }}
docker compose up -d --build   # vulnerable_app.py on :8113, fixed_app.py on :8114
python3 -m pip install requests           # once, on the host
python3 exploit.py
```
`exploit.py` runs the main checks in one go (an optional self-check, not a replacement for the
steps above; the Step-by-step needs no Python). Expect two `PASS` lines and exit `0`: an external
IP allowed + flag on `:8113`, the identical external IP denied (no flag) on `:8114`.

**Verified (2026-11-04):** The "get this lab" commands (A, B and C) were run as written on 2026-11-08, in bash and in zsh, on a fresh clone. `docker compose up -d --build` was run on this machine (macOS) and
every command in Step-by-step was run as written, in bash and in zsh (the macOS default shell).
Windows Git Bash was not tested. The optional environment override was tested; the public default is a shared marker. `exploit.py` then ran
from the host against the published ports. Real captured output, flag value masked:
```
=== VULNERABLE (allow-all at #90 shadows deny-all at #100) (http://localhost:8113) ===
[*] rule set (ascending order) -> [{'action': 'allow', 'cidr': '0.0.0.0/0', 'port': 5432, 'rule_number': 90}, {'action': 'deny', 'cidr': '0.0.0.0/0', 'port': 5432, 'rule_number': 100}]
[*] external IP 203.0.113.55 -> port 5432 -> 200 {'action': 'allow', 'flag': 'FLAG{...}', 'matched_rule_number': 90, 'port': 5432, 'source_ip': '203.0.113.55'}
PASS: external IP was ALLOWED to the DB port on the vulnerable app (rule #90 matched first), flag = FLAG{...}

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

**Shared demonstration marker.** No personal `.env` or individual flag is required. Any
`flag` printed by this simulation is a public example marker; it does not identify the student
and is not graded by itself. Submit the exact request or command, the complete relevant
vulnerable and fixed responses, and your own explanation of the security effect. The instructor
may ask you to reproduce and explain the result live. Do not use real credentials in evidence.

## Deliverable
The complete vulnerable/fixed response evidence + the exact request (`source_ip`, `port`) that produced it + a one-paragraph
explanation of why a visibly-present "deny all" rule at a higher rule number can still be
completely unreachable — it's not that the deny rule is wrong, it's that a broader rule ahead
of it already decided the outcome. You may answer in Thai or English. Write your answers on the
**Local07 Answer Sheet** copy in Classroom and click Turn in (no PDF needed). Full tasks:
`worksheet.md`.

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
