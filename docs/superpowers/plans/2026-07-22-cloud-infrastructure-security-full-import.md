# Cloud Infrastructure & Security Full Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import all 10 real lessons of the `cloud-infrastructure-security` course into the shared
library (no pilot lesson exists yet for this course — this IS the pilot), write its manifest, and
verify it renders with full content parity against the current local source repo.

**Architecture:** No engine changes needed — everything this course's content needs (a `lessons`
schedule unit, multi-flag-free CONCEPTUAL lessons, plain flat lessons with no nested subdirectories)
is already supported. This course is **structurally different** from its two siblings and that changes
how this plan reads:

- **The source repo is unpublished.** `course-plan.md` (source repo) states explicitly: *"Not yet
  actually created on GitHub — this repo exists only locally so far."* This means the byte-parity
  invariant that mattered for `software-security`/`security-cryptography` (external links, students,
  drop-in-replacement) does not apply the same way here. What still matters — and what this plan's
  parity test still checks — is **file-content parity** against the current local source repo (the
  authoritative hand-maintained content), not directory-NAME parity against a live published path.
- **The source directory names don't follow a clean, renderable numbering scheme.** They mirror AWS
  Academy's own module numbers for traceability with the co-instructor (Shinya Oyama): `lesson01-03-`
  (a combined range), `lesson07b-` (a letter suffix with no separating hyphen from the digits). The
  renderer's `slotfile()` can only ever produce `lesson{n:02d}` for a single integer `n` — it cannot
  reproduce `lesson01-03` or `lesson07b` from any slot number. **Decision (confirmed with the user):**
  renumber cleanly, slots 1–10 sequential, matching this course's own pedagogical order (the order
  `course-plan.md`'s own lesson-topic table already uses). AWS's original module numbers are NOT lost —
  they stay legible in each lesson's own "Topic (source):" prose line (an unchanged, un-tokenized
  citation) and can be added to `lesson.yml` tags if useful later; they just stop being the *primary*
  numbering scheme once this course has its own portable schedule position.
- **This decouples "Lesson N" prose from directory naming — read carefully before tokenizing.** In the
  two prior courses, "Week N" in prose was always synonymous with "this course's own schedule
  position," so tokenizing it was mechanical. Here, most "Lesson N" self-title mentions ARE this
  course's own schedule position (correctly `{{ slot_label }}`) — but at least one place
  (`lesson07b-cloudtrail-monitoring/worksheet.md`) explains AWS's *own historical* numbering ("the two
  topics of Lesson 7 deliberately split across blocks") as background/explanatory context, not a claim
  about our schedule. That one stays literal — see Task 1 Step 1.3 for the full distinction and why.
- **Lighter cross-referencing than both prior courses.** A full grep sweep (done before writing this
  plan) found exactly TWO same-course cross-references beyond each lesson's own self-title — both
  "same precedent as [`]lesson11[`]'s KMS envelope-encryption week" style mentions, both pointing at
  the same lesson (`kms-envelope-encryption`). No dense multi-reference lessons like
  `security-cryptography`'s `aead`/`pqc`. No `slides/` mentions anywhere (this course has no slides
  yet, same as the `security-cryptography` pilot's starting state). No nested subdirectories (unlike
  `pqc`'s `hndl/`) — only a stray `__pycache__` in `lesson14-config-lambda-remediation` to clean up.
- **`target_repo` is provisional.** The field is required by `tools/model.py`'s `load_manifest` (no
  default) but not otherwise read by any current tooling. `nutthakorn7/cloud-infrastructure-security`
  is used as a deterministic extrapolation of the same `nutthakorn7/<repo-name>` convention every other
  manifest already uses — not a fabricated guess (no unknown data is being invented) — but the repo
  does not exist on GitHub yet; this field will need revisiting once/if it's actually created there.

**Tech Stack:** Same as prior work — Python 3.12, PyYAML, Jinja2, pytest, the monorepo's existing `.venv`.

**Working dir for every path below:** the monorepo root
`/Users/pop7/Library/CloudStorage/OneDrive-MonsterConnectCo.,Ltd/Lecture/KOSEN69 - curriculum`.
Run tests from there: `.venv/bin/python -m pytest tests/ -q` (95 pass at the start of this plan — verify
in Task 1 Step 0). The **source** repo is the filesystem sibling
`../KOSEN69 - cloud-infrastructure-security/`.

---

## Source facts (gathered directly from the source repo; used verbatim below — no placeholders)

### The slot → slug mapping (authoritative — this is a NEW schedule, not inherited from AWS numbers)

| Slot | Slug | Source dir | Kind | `flag_keys` |
|---|---|---|---|---|
| 1 | `aws-fundamentals-intro` | `lesson01-03-aws-fundamentals-intro` | CONCEPTUAL | `[]` |
| 2 | `ec2-lambda-beanstalk` | `lesson04-ec2-lambda-beanstalk` | HYBRID | `[ec2]` |
| 3 | `s3-static-site-lambda-sns` | `lesson05-s3-static-site-lambda-sns` | LAB | `[s3]` |
| 4 | `load-balancing-autoscaling` | `lesson06-load-balancing-autoscaling` | HYBRID | `[scaling]` |
| 5 | `iam-policy-evaluation` | `lesson07-iam-policy-evaluation` | LAB | `[iam]` |
| 6 | `cloudtrail-monitoring` | `lesson07b-cloudtrail-monitoring` | HYBRID | `[monitor]` |
| 7 | `vpc-networking` | `lesson10-vpc-networking` | HYBRID | `[nacl]` |
| 8 | `kms-envelope-encryption` | `lesson11-kms-envelope-encryption` | CONCEPTUAL | `[]` |
| 9 | `s3-versioning-lifecycle-replication` | `lesson13-s3-versioning-lifecycle-replication` | CONCEPTUAL | `[]` |
| 10 | `config-lambda-remediation` | `lesson14-config-lambda-remediation` | HYBRID | `[remediate]` |
| 11 | — | n/a | non-lesson: `review` (AWS-graded reflection/wrap-up — shared baseline, not authored in this repo) |

(Slugs are the source directory name with its numeric `lessonNN[b][-MM]-` prefix mechanically
stripped — same derivation rule used for every lesson in the prior two courses. 7 flags total, matching
`course-plan.md`'s own count: "7 challenge keys.")

### Per-lesson import facts (Kind/CWE copied verbatim from each README's own header line)

| Slug | Kind | CWE (verbatim from README) | Notable content |
|---|---|---|---|
| `aws-fundamentals-intro` | CONCEPTUAL | CWE-269, CWE-287 | No code at all (README + worksheet only). H1 is `# Lessons 1–3 — ...` (a range) — becomes `{{ slot_label }} — ...` (renders a single "Lesson 1", losing the "1–3" range from the title only; the range itself stays legible in the unchanged "Topic (source): AWS Academy Modules 1–3..." line). Contains the same-course cross-ref `` same precedent as `lesson11`'s KMS envelope-encryption week `` → `{{ ref('kms-envelope-encryption') }}`. |
| `ec2-lambda-beanstalk` | HYBRID | CWE-918 | Standard flat lab (Dockerfile, docker-compose.yml, exploit.py, fixed_app.py, vulnerable_app.py, requirements.txt). `cd labs/lesson04-ec2-lambda-beanstalk` → `{{ labpath }}`. |
| `s3-static-site-lambda-sns` | LAB | CWE-284, CWE-668 | Same flat lab shape. `cd labs/lesson05-...` → `{{ labpath }}`. |
| `load-balancing-autoscaling` | HYBRID | CWE-400 | Has an extra `scaler.py` alongside the usual lab files — copy verbatim, no tokenization inside `.py` files. `cd labs/lesson06-...` → `{{ labpath }}`. |
| `iam-policy-evaluation` | LAB | CWE-284, CWE-668 | Has an extra `policy_engine.py`. `cd labs/lesson07-...` → `{{ labpath }}`. |
| `cloudtrail-monitoring` | HYBRID | CWE-778 (adjacent) | `flag_keys: [monitor]` — confirmed against `course-plan.md`'s explicit statement that `seed_flags.py`'s `CHALLENGES` list "already includes `monitor`." **Special case:** `worksheet.md` line 4, *"the two topics of Lesson 7 deliberately split across blocks,"* is explanatory background about AWS's own historical module 7 (which had two topics, now split into this course's own slots 5 and 6) — this is NOT a claim about our schedule position and must stay literal, not `{{ slot_label }}` or `{{ ref(...) }}`. Every other "Lesson 7"/"Lesson N" mention in this lesson's own title IS this lesson's own self-reference and DOES get `{{ slot_label }}`. `cd labs/lesson07b-...` → `{{ labpath }}`. |
| `vpc-networking` | HYBRID | CWE-863, CWE-284 | Has an extra `nacl_engine.py`. `cd labs/lesson10-...` → `{{ labpath }}`. |
| `kms-envelope-encryption` | CONCEPTUAL | CWE-320 | No code (README + worksheet only). Referenced BY `aws-fundamentals-intro` and `s3-versioning-lifecycle-replication` (see below) — no outgoing same-course reference of its own found. |
| `s3-versioning-lifecycle-replication` | CONCEPTUAL | CWE-1188 (the README calls it "CWE-1188-adjacent... applied loosely" — use the bare ID `CWE-1188` in `lesson.yml`, matching the numeric-ID-only convention every other lesson's `cwe:` list already uses) | No code. Contains the same-course cross-ref *"same precedent as Lesson 11"* → `{{ ref('kms-envelope-encryption') }}`. |
| `config-lambda-remediation` | HYBRID | CWE-697, CWE-284 | Has an extra `remediation_engine.py` and a stray `__pycache__/` to remove. `cd labs/lesson14-...` → `{{ labpath }}`. |

### The manifest

```yaml
course:
  name: "Cloud Infrastructure & Security"
  brand: "KOSEN·KMITL"
  flag_salt_env: CIS_FLAG_SALT
  challenge_keys_env: AIRSEC_CHALLENGE_KEYS
target_repo: "nutthakorn7/cloud-infrastructure-security"
schedule_unit: lessons
slot_label: "Lesson {n}"
schedule:
  - {slot: 1,  lesson: aws-fundamentals-intro}
  - {slot: 2,  lesson: ec2-lambda-beanstalk}
  - {slot: 3,  lesson: s3-static-site-lambda-sns}
  - {slot: 4,  lesson: load-balancing-autoscaling}
  - {slot: 5,  lesson: iam-policy-evaluation}
  - {slot: 6,  lesson: cloudtrail-monitoring}
  - {slot: 7,  lesson: vpc-networking}
  - {slot: 8,  lesson: kms-envelope-encryption}
  - {slot: 9,  lesson: s3-versioning-lifecycle-replication}
  - {slot: 10, lesson: config-lambda-remediation}
  - {slot: 11, review: "Reflection & Wrap-up (AWS-graded assessments — shared baseline, not authored in this repo)"}
```
`flag_salt_env`/`challenge_keys_env` names follow the `<COURSE_ABBREV>_FLAG_SALT` /
`AIRSEC_CHALLENGE_KEYS` convention of the two existing manifests (`SC_FLAG_SALT` for
security-cryptography); `CIS_FLAG_SALT` is the natural abbreviation for this course, not yet confirmed
against any existing `.env` — flag this to the user if a different name is already in use anywhere in
the source repo's `instructor/` tooling (this plan does not touch `instructor/` or `seed_flags.py`,
which is git-ignored and out of scope — see "Not in scope" below).
`target_repo` is top-level, matching the confirmed-working convention in all three existing manifests.

### Not in scope for this plan

- `instructor/seed_flags.py`, `instructor/check_flag_keys.py`, and any other `instructor/`-tooling
  migration — git-ignored, never committed, and explicitly deferred as its own future "flag-tooling
  migration" task (centralizing all three courses' copies), not part of this import.
- The AWS Academy licensing/co-ownership/OSF-amendment items in `course-plan.md`'s "Open / not yet
  done" section — none of them block or relate to this technical import; not raised here.
- Creating the `nutthakorn7/cloud-infrastructure-security` GitHub repo — out of scope; `target_repo` is
  written provisionally per the note above.

---

### Task 1: Import all 10 lessons

**Files:** Create `lessons/<slug>/` for each of the 10 slugs in the mapping table above.

- [ ] **Step 0: Confirm the starting baseline.** Run `.venv/bin/python -m pytest tests/ -q` and confirm
  95 pass (the state after the `security-cryptography` import merged) — if different, stop and report
  rather than proceeding on a wrong assumption.

- [ ] **Step 1: For EACH of the 10 lessons, in slot order:**
  1. Copy: `cp -R "../KOSEN69 - cloud-infrastructure-security/labs/<source-dir>"/. "lessons/<slug>/"`.
     Then remove any `__pycache__`/`.pyc` (only `config-lambda-remediation` has one, but check all):
     `find "lessons/<slug>" -iname "__pycache__" -exec rm -rf {} + ; find "lessons/<slug>" -iname "*.pyc" -delete`
  2. Write `lessons/<slug>/lesson.yml` using the Kind/CWE from the facts table above:
     ```yaml
     slug: <slug>
     title: "<the H1 of the copied README.md, with the leading 'Lesson(s) N[–M]' / 'Lesson N (2nd topic)' prefix stripped>"
     kind: <LAB | HYBRID | CONCEPTUAL, from the table>
     duration_min: 180
     tags: [<2-4 short topic tags from the README's own Concepts line>]
     cwe: [<the verbatim CWE IDs from the facts table above — bare IDs only, e.g. "CWE-320", not the "-adjacent" qualifier text>]
     prereqs: []
     flag_keys: <the exact list from the facts table above, lowercased; [] if none>
     ```
  3. **Tokenize — the systematic loop (do this exactly, do not shortcut it):**
     a. Grep every "Lesson N" / "Lessons N–M" mention: `grep -noE "Lessons? [0-9]+([-–][0-9]+)?" lessons/<slug>/*.md`
     b. For each hit, decide:
        - **This lesson's own self-title/self-reference** (the H1, a "Worksheet — Lesson N..." line, a
          plain "(Lesson N falls in Block ...)" aside about ITSELF) → `{{ slot_label }}`. If the hit is
          a range ("Lessons 1–3") because this lesson maps multiple AWS modules onto one of our slots,
          replace the WHOLE "Lessons 1–3" span with `{{ slot_label }}` (it renders a single number —
          that's expected and correct; the AWS module range stays legible elsewhere in the unchanged
          "Topic (source):" line, do not also touch that line).
        - **A mention of a DIFFERENT same-course lesson by name/topic** ("same precedent as
          `lesson11`'s KMS envelope-encryption week", "same precedent as Lesson 11") →
          `{{ ref('<slug>') }}` using the slot→slug mapping table (both known instances resolve to
          `kms-envelope-encryption`).
        - **An explanatory/historical reference to AWS's OWN original numbering** — text describing why
          AWS's own module was split, combined, or organized a particular way (the ONE confirmed
          instance: `cloudtrail-monitoring/worksheet.md`'s "the two topics of Lesson 7 deliberately
          split across blocks") — leave as literal text, do NOT tokenize. This is background context
          about AWS's fixed curriculum, not a claim about our own schedule.
        - **A mention of a DIFFERENT course** (e.g. `software-security`, `security-cryptography`) → if
          any such mention exists (none were found in the pre-plan grep sweep, but re-check per-lesson
          since the sweep was global-pattern-based, not exhaustive-reading), leave as literal text.
     c. Apply the replacements, changing ONLY the schedule-reference text — do not alter surrounding
        wording.
     d. Re-run the grep from (a). Confirm every remaining hit is a deliberate case from (b) above (note
        which, in your final report) — if anything else remains, you missed a case; go back to (b).
  4. Lint: `.venv/bin/python -c "from tools import validate; print('\n'.join(validate.lint_lesson('lessons/<slug>')) or 'clean')"`
     — this WILL flag the one deliberate literal-text exception in `cloudtrail-monitoring` (matching the
     precedent set by `security-cryptography`'s `intro`/`hybrid-encryption` lessons, which also lint
     "dirty" for deliberate, reviewed cross-reference exceptions — no test asserts whole-library lint
     cleanliness, so this is not a blocker). Fix anything else flagged.
     Also grep for bare path references the linter doesn't catch:
     `grep -noE "(labs/)?lesson[0-9a-z-]+" lessons/<slug>/*.md` and tokenize any real self-reference
     found (`{{ labpath }}` for a `labs/`-prefixed self-reference — every known instance in this course
     is exactly this shape, one `cd labs/<source-dir>` line per LAB/HYBRID lesson's "Run it" section).
  5. Byte-check the lab code wasn't touched:
     `diff -rq "../KOSEN69 - cloud-infrastructure-security/labs/<source-dir>" "lessons/<slug>"` should
     report differences ONLY in the `.md` files you tokenized, plus the removed `__pycache__` (only for
     `config-lambda-remediation`) — every other file must be byte-identical to source.

- [ ] **Step 2: After all 10 are imported, lint the whole library at once** (expect exactly one
  known-dirty lesson, `cloudtrail-monitoring`, for the deliberate literal exception above — everything
  else, including all 24 already-imported lessons from the other two courses, must print `clean`):
```bash
.venv/bin/python -c "
from tools import validate
import os
for slug in sorted(os.listdir('lessons')):
    v = validate.lint_lesson(f'lessons/{slug}')
    print(slug, '->', v or 'clean')
"
```

- [ ] **Step 3: Run the full suite** — `.venv/bin/python -m pytest tests/ -q` (no new tests in this
  task; confirms nothing broke — should still be 95 passing).

- [ ] **Step 4: Commit**
```bash
git add lessons/aws-fundamentals-intro lessons/ec2-lambda-beanstalk lessons/s3-static-site-lambda-sns \
        lessons/load-balancing-autoscaling lessons/iam-policy-evaluation lessons/cloudtrail-monitoring \
        lessons/vpc-networking lessons/kms-envelope-encryption lessons/s3-versioning-lifecycle-replication \
        lessons/config-lambda-remediation
git status --short          # verify ONLY these 10 lessons/ dirs are staged
git commit -m "import: all 10 cloud-infrastructure-security lessons"
```

---

### Task 2: Write the manifest + render + parity-verify

**Files:**
- Create: `courses/cloud-infrastructure-security.yml` (verbatim from "Source facts" above)
- Create: `tests/test_parity_cis.py`

- [ ] **Step 1: Write `courses/cloud-infrastructure-security.yml`** with the manifest from "Source
  facts" above (11 slots: the 10 lessons + the reflection/wrap-up review slot).

- [ ] **Step 2: Write the parity test** — `tests/test_parity_cis.py` (mirror `tests/test_parity_sc.py`'s
  structure; this course has no nested lesson subdirectories, so `rglob` vs flat `glob` doesn't matter,
  but keep `rglob` for consistency and future-proofing):
```python
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_REPO = ROOT.parent / "KOSEN69 - cloud-infrastructure-security"
SRC_LABS = SRC_REPO / "labs"

LESSON_DIRS = {
    "aws-fundamentals-intro": "lesson01-03-aws-fundamentals-intro",
    "ec2-lambda-beanstalk": "lesson04-ec2-lambda-beanstalk",
    "s3-static-site-lambda-sns": "lesson05-s3-static-site-lambda-sns",
    "load-balancing-autoscaling": "lesson06-load-balancing-autoscaling",
    "iam-policy-evaluation": "lesson07-iam-policy-evaluation",
    "cloudtrail-monitoring": "lesson07b-cloudtrail-monitoring",
    "vpc-networking": "lesson10-vpc-networking",
    "kms-envelope-encryption": "lesson11-kms-envelope-encryption",
    "s3-versioning-lifecycle-replication": "lesson13-s3-versioning-lifecycle-replication",
    "config-lambda-remediation": "lesson14-config-lambda-remediation",
}

pytestmark = pytest.mark.skipif(not SRC_LABS.is_dir(), reason="source cloud-infrastructure-security repo not present")


def _render(tmp):
    from tools import render
    render.render_course(str(ROOT / "courses" / "cloud-infrastructure-security.yml"),
                         lessons_root=str(ROOT / "lessons"), out_dir=str(tmp / "out"))
    return tmp / "out"


def test_no_unresolved_tokens(tmp_path):
    out = _render(tmp_path)
    for md in out.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        assert "{{" not in text and "{%" not in text, f"unresolved token in {md}"


@pytest.mark.parametrize("slug,srcdir", sorted(LESSON_DIRS.items()))
def test_lab_code_byte_identical(tmp_path, slug, srcdir):
    out = _render(tmp_path)
    src_lab = SRC_LABS / srcdir
    out_lab = next(out.glob(f"labs/lesson*-{slug}"))
    for src in src_lab.rglob("*"):
        if src.is_dir() or src.suffix == ".md" or "__pycache__" in src.parts:
            continue
        rel = src.relative_to(src_lab)
        dst = out_lab / rel
        assert dst.is_file(), f"{slug}: missing rendered file {rel}"
        assert dst.read_bytes() == src.read_bytes(), f"{slug}: lab code drifted: {rel}"


@pytest.mark.parametrize("slug,srcdir", sorted(LESSON_DIRS.items()))
def test_markdown_matches_source(tmp_path, slug, srcdir):
    out = _render(tmp_path)
    src_lab = SRC_LABS / srcdir
    out_lab = next(out.glob(f"labs/lesson*-{slug}"))
    for src in src_lab.rglob("*.md"):
        rel = src.relative_to(src_lab)
        dst = out_lab / rel
        assert dst.is_file(), f"{slug}: missing rendered {rel}"
        assert dst.read_text(encoding="utf-8") == src.read_text(encoding="utf-8"), \
            f"{slug}: rendered {rel} != current source content"
```
Note `out.glob(f"labs/lesson*-{slug}")`: this matches the RENDERED directory (e.g.
`labs/lesson01-aws-fundamentals-intro`) by slug, not by the (deliberately different) source directory
name (`lesson01-03-aws-fundamentals-intro`) — directory-NAME parity is not being asserted, only
file-CONTENT parity against the source files found via `LESSON_DIRS`' explicit map. This is intentional
(see this plan's Architecture section) and does not need "fixing" if slot/source numbers don't visually
match.

- [ ] **Step 3: Render + run.**
```bash
.venv/bin/python -m tools.render courses/cloud-infrastructure-security.yml --out _render/cis
find _render/cis/labs -maxdepth 1 -type d | sort
```
  Expect 10 `labs/lessonNN-<slug>/` directories, cleanly numbered `lesson01` through `lesson10`. Then:
```bash
.venv/bin/python -m pytest tests/test_parity_cis.py -q
```
  For any failure, the diff shows exactly which tokenization needs fixing — the fix ALWAYS goes in
  `lessons/<slug>/*.md` (never in the test, never in the manifest, never in the renderer). Watch
  specifically for the two classes of bug the last two imports actually hit: (a) a paragraph
  reflow/line-wrap change introduced while inserting a token (the fix is to preserve the exact original
  line-break positions, only swapping the literal text for the token — see
  `security-cryptography`'s plan and its `hybrid-encryption` fix for the exact failure shape this
  produces), and (b) a token substituted where the literal source text should have stayed (matching the
  precedent of leaving "last week" literal in `security-cryptography` and the one deliberate literal
  exception documented in this plan's Task 1 Step 1.3) — do not weaken this test to accommodate either;
  fix the lesson `.md` file's tokenization instead.

- [ ] **Step 4: Full suite** — `.venv/bin/python -m pytest tests/ -q` — all green.

- [ ] **Step 5: Commit**
```bash
git add courses/cloud-infrastructure-security.yml tests/test_parity_cis.py
git status --short   # verify only these 2 files are staged (plus any lesson fixes from Step 3, called out explicitly if so)
git commit -m "manifest: cloud-infrastructure-security course; content-parity verified per lesson"
```

---

## Verification (before finishing the branch)

1. `.venv/bin/python -m pytest tests/ -q` — all green (95 baseline + ~1 + 20 parametrized parity tests
   ≈ 116, but don't assume the exact number — report what you observe).
2. `.venv/bin/python -m tools.render courses/cloud-infrastructure-security.yml --out _render/cis`
   succeeds with no errors.
3. Manual: open `_render/cis/labs/lesson01-aws-fundamentals-intro/README.md` and confirm the KMS
   cross-reference reads naturally ("same precedent as Lesson 8's KMS envelope-encryption week" or
   similar, resolving to whatever slot `kms-envelope-encryption` ends up at).
4. Manual: open `_render/cis/labs/lesson06-cloudtrail-monitoring/README.md`'s worksheet and confirm the
   deliberate literal exception ("the two topics of Lesson 7...") still reads as a sensible historical
   aside, not a broken/mismatched claim about the new slot numbering.
5. `git log --oneline` on the branch shows 2 commits (Task 1–2), each independently green.

## Self-review

- **Spec coverage:** all 10 real lessons (matching `course-plan.md`'s "all 10 lesson topics built")
  · the AWS-graded reflection/wrap-up correctly modeled as a non-lesson calendar slot, not silently
  dropped · the renumbering decision and its prose implications explicitly resolved with the user before
  writing task steps, not assumed.
- **Type/name consistency:** the slot→slug table is the single source of truth referenced by both Task
  1 (tokenization + `lesson.yml`) and Task 2 (manifest `schedule:` + test `LESSON_DIRS`) — cross-checked
  for agreement before this plan was finalized.
- **No placeholders:** every lesson's kind/CWE/flags came from a direct read of the source repo
  (reproduced in "Source facts"); flag count (7) cross-checked against `course-plan.md`'s own claim.
  `target_repo` and `flag_salt_env` are flagged explicitly as provisional/unconfirmed rather than
  silently presented as settled facts.
- **Lesson learned from the prior two imports, applied here:** real bugs in both were caught by
  systematic re-grepping and the byte/content-parity test, not a perfect first pass — this plan keeps
  that discipline (Task 1 Step 1.3's loop, Task 2 Step 3's explicit callout of the two failure shapes
  already seen once each). The one NEW risk class specific to this course (self-title tokenization
  colliding with AWS's-own-numbering explanatory prose) is called out by name with its one confirmed
  instance, rather than trusting the general loop alone to notice a pattern it hasn't seen before.
