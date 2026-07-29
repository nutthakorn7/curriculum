# Working rules for this repo

This monorepo is the **source** for three course repos. A change here is not
local — it renders outward. Nothing else in this file matters as much as that.

```
lessons/<topic>/     the module. The only place content is authored.
courses/*.yml        an ordering over lessons. A course is a manifest, nothing more.
        ↓ render
software-security/labs/weekNN-*/     ← rendered output, byte-parity gated
security-cryptography/...
cloud-infrastructure-security/...
```

## Never "fix" the deliberately vulnerable material

Several lessons are insecure **on purpose** — that is the exercise. Each one says
so in the file itself; read the comment before changing a version.

- `lessons/supply-chain/` — outdated pins and `FROM python:3.9-slim` so SCA tools
  (trivy, pip-audit) have something real to find. Bumping them deletes the lesson.
- `lessons/cloud-container/Dockerfile.insecure` — `FROM python:latest` is the
  defect the hardened variant is compared against.
- `lessons/signatures-zkp/` — `ecdsa` has **no fixed version** for CVE-2024-23342;
  upstream declared side-channel attacks out of scope. Documented accepted risk.
- Every lesson with a `vulnerable_app.py` next to a `fixed_app.py`.

`.github/dependabot.yml` watches the build tooling only and deliberately lists no
`lessons/` directory. Adding one opts that lesson into automated bumps.

## Editing a lesson: three things move together

1. **`lessons/<topic>/`** — the source.
2. **The rendered copy in each course repo that uses it.** The parity gate compares
   them byte for byte. Apply the *same* edit by hand — do **not** `cp`, because the
   monorepo copies carry template tokens (`{{ slot_label }}`, `{{ labpath }}`) that
   the rendered ones have already had filled in.
3. **The answer keys** in the consuming repo's git-ignored `instructor/` —
   `quizzes/weekly/weekNN-answers.md`, `exams/`, `research/`. Nothing in CI will
   remind you, and a worksheet fix that leaves its key stale marks correct answers
   wrong.

Then run the gate:

```
.venv/bin/python -m pytest tests/ -q
```

## Ordering is enforced, and only hard dependencies are declared

`lesson.yml`'s `prereqs` lists what the lesson's own material *assumes* — not what
merely reads better first. `tools/validate.py` refuses a manifest that schedules a
lesson before something it needs, which is what stops a short course from teaching
`api-security` before `authn-authz`.

Over-declaring has a real cost: it rejects legitimate orderings. 11 of the 34
lessons are genuinely standalone and should stay `prereqs: []`.

## Verify by running, not by reading

Payloads, expected tool output, crash messages, line-number citations and package
pins are things students execute literally. Run the command before claiming it
works — several "facts" in this material turned out wrong under reproduction.
