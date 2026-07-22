# Security & Cryptography Full Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import the remaining 11 real lessons of the `security-cryptography` course into the shared
library (the `hash` pilot lesson is already imported), write its full 19-slot manifest, and verify it
renders to byte-parity with what is currently published.

**Architecture:** No engine changes are needed this time — everything this course's content needs
(multi-flag lessons, nested subdirectories, a `CONCEPTUAL` kind with little/no code) is already
supported by the engine built for the pilot and the `software-security` import. This course also has
**no MFU-equivalent compressed schedule** (confirmed: no such doc exists in the source repo) — only the
one 19-slot manifest is built here. A compressed variant, if one is ever needed, is a trivial follow-on
once this manifest exists (same recipe as `software-security-mfu.yml`).

**What's different from the `software-security` import, and why this plan is structured the way it is:**
- **Cross-references are denser and less uniform.** `software-security`'s lessons almost all had exactly
  one pattern ("Week 1 *Lab 0*; last week's recap"). This course's lessons reference MULTIPLE earlier
  weeks, sometimes non-adjacent ones, sometimes more than once in the same file (e.g. `week06-aead`
  discusses `Week 3` and `Week 4` in at least two separate places; `week15-pqc` references `Week 3` AND
  `Week 5`). A table of "the" cross-ref per lesson would be incomplete and misleading here. Instead, this
  plan gives the authoritative **week-number → slug mapping** and a **systematic tokenize-verify loop**
  (grep for every remaining `Week \d+` after tokenizing, not just the ones a spot-check happened to
  find) — this is the same process that caught real gaps during the `software-security` import (see that
  course's plan's Task 2 follow-up commits) and is deliberately made the primary instruction here rather
  than an afterthought.
- **One lesson (`pqc`) has a nested subdirectory** (`hndl/`, a companion sub-lab already built earlier
  this session) and **two flags** (`FLAG_PQC` + `FLAG_HNDL`). The renderer already copies nested
  directories correctly (proven working); `__pycache__` cleanup must be applied recursively (`find`,
  not a flat `rm -rf lessons/<slug>/__pycache__`, since `hndl/__pycache__` is one level deeper).
- **Two lessons (`intro`, `hybrid-encryption`) are `kind: CONCEPTUAL`** — `intro` has no code at all
  (just README + worksheet); `hybrid-encryption` has a small `audit_the_ai/` exercise but no
  docker-compose lab. Neither needs a `docker-compose.yml`; this is expected, not a gap.
- **Cross-COURSE mentions must NOT be tokenized.** Several lessons mention `` `software-security` ``'s
  own Week 1 for context (e.g. `week01-intro`: *"same precedent as software-security's Week 1
  threat-modeling"*). `ref()` only resolves within the CURRENT manifest — there is no cross-course
  token. Leave these as literal prose; only tokenize numeric week references to THIS course's own weeks.

**Tech Stack:** Same as prior work — Python 3.12, PyYAML, Jinja2, pytest, the monorepo's existing `.venv`.

**Working dir for every path below:** the monorepo root
`/Users/pop7/Library/CloudStorage/OneDrive-MonsterConnectCo.,Ltd/Lecture/KOSEN69 - curriculum`.
Run tests from there: `.venv/bin/python -m pytest tests/ -q` (70 pass at the start of this plan — verify
in Task 1 Step 0). The **source** repo is the filesystem sibling
`../KOSEN69 - security-cryptography/`.

---

## Source facts (gathered directly from the source repo; used verbatim below — no placeholders)

### The week-number → slug mapping (authoritative — use this to resolve EVERY numeric week reference)

| Week | Slug | Status |
|---|---|---|
| 1 | `intro` | to import (this plan) |
| 2 | `hash` | **already imported** (the pilot lesson) |
| 3 | `macs` | to import |
| 4 | `aes-modes` | to import |
| 5 | `key-exchanges` | to import |
| 6 | `aead` | to import |
| 7 | — | non-lesson: review (pre-midterm) |
| 8 | — | non-lesson: exam, `phase: midterm` |
| 9 | — | non-lesson: exam, `phase: midterm` |
| 10 | `hybrid-encryption` | to import |
| 11 | `signatures-zkp` | to import |
| 12 | `secure-transport` | to import |
| 13 | `e2e-encryption` | to import |
| 14 | `authentication` | to import |
| 15 | `pqc` | to import (has a nested `hndl/` sub-lab + 2 flags) |
| 16 | — | non-lesson: project (capstone studio; **no `labs/week16` directory exists at all** — pure calendar entry) |
| 17 | — | non-lesson: review (pre-final) |
| 18 | — | non-lesson: exam, `phase: final` |
| 19 | — | non-lesson: exam, `phase: final` |

(Confirmed: `syllabus.md` states *"Weekly lab worksheets — 12 graded (Weeks 1–6, 10–15)"*, *"Midterm —
Week 8 (written) + Week 9 (CTF practical)"*, *"Final — Week 18 written + Week 19 capstone CTF"* — matches
this table exactly. Weeks 8, 9, 16, 18, 19 have no `labs/` subdirectory in the source repo at all, unlike
`software-security` where the equivalent weeks had thin placeholder directories — nothing to import for
these, they are pure manifest entries.)

### Per-lesson import facts

| Slug | Source dir | Kind | `flag_keys` | Notable content |
|---|---|---|---|---|
| `intro` | `week01-intro` | CONCEPTUAL | `[]` | README + worksheet only, no code. Mentions `software-security`'s Week 1 and this course's own Week 10 — the Week 10 mention is same-course (tokenize as `{{ ref('hybrid-encryption') }}`); the `software-security` mention is cross-course (leave literal). |
| `macs` | `week03-macs` | LAB | `[macs]` | |
| `aes-modes` | `week04-aes-modes` | LAB | `[aes]` | |
| `key-exchanges` | `week05-key-exchanges` | HYBRID | `[]` | Has 2 `docker-compose*.yml` files (vulnerable/fixed pair) — copy both verbatim, unrelated to tokenization. |
| `aead` | `week06-aead` | LAB | `[aead]` | References Week 3 AND Week 4 in at least two separate places (README and worksheet) — this is the densest cross-ref lesson; also references Week 10 once in the worksheet. |
| `hybrid-encryption` | `week10-hybrid-encryption` | CONCEPTUAL | `[]` | Has a nested `audit_the_ai/` subdirectory with one `.py` file — no docker-compose, expected. |
| `signatures-zkp` | `week11-signatures-zkp` | HYBRID | `[sig]` | |
| `secure-transport` | `week12-secure-transport` | HYBRID | `[]` | References Week 5 (non-adjacent) for its MITM recap, not just "last week". |
| `e2e-encryption` | `week13-e2e-encryption` | HYBRID | `[]` | References Week 12 specifically ("the Week 12 recap on asymmetric/hybrid encryption") — note Week 12 in THIS course is `secure-transport`, not `hybrid-encryption` (Week 10) — do not confuse the two; re-verify against the mapping table above, don't guess from the topic name alone. |
| `authentication` | `week14-authentication` | HYBRID | `[]` | References Week 2 (`hash`) at least twice, non-adjacent. |
| `pqc` | `week15-pqc` | LAB | `[pqc, hndl]` | References Week 3 (`macs`) and Week 5 (`key-exchanges`). **Has a nested `hndl/` subdirectory** (a companion HNDL/hybrid-KEM lab) — copy it as part of the lesson; remove `hndl/__pycache__` too (use `find lessons/pqc -iname __pycache__ -exec rm -rf {} +` or equivalent recursive cleanup, not a single flat path). |

### The manifest

```yaml
course:
  name: "Security & Cryptography"
  brand: "KOSEN·KMITL"
  flag_salt_env: SC_FLAG_SALT
  challenge_keys_env: AIRSEC_CHALLENGE_KEYS
target_repo: "nutthakorn7/security-cryptography"
schedule_unit: weeks
slot_label: "Week {n}"
schedule:
  - {slot: 1,  lesson: intro}
  - {slot: 2,  lesson: hash}
  - {slot: 3,  lesson: macs}
  - {slot: 4,  lesson: aes-modes}
  - {slot: 5,  lesson: key-exchanges}
  - {slot: 6,  lesson: aead}
  - {slot: 7,  review: "Review (pre-Midterm)"}
  - {slot: 8,  exam: "Midterm: Written", phase: midterm}
  - {slot: 9,  exam: "Midterm: CTF Practical", phase: midterm}
  - {slot: 10, lesson: hybrid-encryption}
  - {slot: 11, lesson: signatures-zkp}
  - {slot: 12, lesson: secure-transport}
  - {slot: 13, lesson: e2e-encryption}
  - {slot: 14, lesson: authentication}
  - {slot: 15, lesson: pqc}
  - {slot: 16, project: "Capstone Studio (CryptoVault build)"}
  - {slot: 17, review: "Review (pre-Final)"}
  - {slot: 18, exam: "Final: Written", phase: final}
  - {slot: 19, exam: "Final: Capstone CTF", phase: final}
```
`target_repo` is top-level (a sibling of `schedule_unit`/`schedule`), matching how `tools/model.py`'s
`load_manifest` actually reads it — confirmed against the two already-working manifests
(`courses/software-security.yml`, `courses/software-security-mfu.yml`); do not nest it under `course:`.

---

### Task 1: Import all 11 remaining lessons

**Files:** Create `lessons/<slug>/` for each of the 11 slugs in the table above.

- [ ] **Step 0: Confirm the starting baseline.** Run `.venv/bin/python -m pytest tests/ -q` and confirm
  70 pass (the state after the `software-security` import merged) — if different, stop and report rather
  than proceeding on a wrong assumption.

- [ ] **Step 1: For EACH of the 11 lessons, in the order listed in the mapping table:**
  1. Copy: `cp -R "../KOSEN69 - security-cryptography/labs/<source-dir>"/. "lessons/<slug>/"`. Then
     recursively remove ALL `__pycache__` directories and `.pyc` files anywhere under the lesson,
     including nested ones:
     `find "lessons/<slug>" -iname "__pycache__" -exec rm -rf {} + ; find "lessons/<slug>" -iname "*.pyc" -delete`
     (this matters especially for `pqc`, whose `hndl/` subdirectory has its own `__pycache__`).
  2. Write `lessons/<slug>/lesson.yml` using the Kind and `flag_keys` from the table above:
     ```yaml
     slug: <slug>
     title: "<the H1 of the copied README.md, with any leading 'Week N — ' prefix stripped>"
     kind: <LAB | HYBRID | CONCEPTUAL, from the table>
     duration_min: 180
     tags: [<2-4 short topic tags inferred from the README's own Kind/Topic line or Concepts>]
     cwe: [<CWE IDs cited in the README, verbatim — do not invent one; if the README cites none, leave []>]
     prereqs: []
     flag_keys: <the exact list from the table above, lowercased; [] if none>
     ```
  3. **Tokenize — the systematic loop (do this exactly, do not shortcut it):**
     a. First, grep the lesson for every numeric week mention: `grep -noE "Week [0-9]+" lessons/<slug>/*.md`
        (and `lessons/<slug>/**/*.md` for nested files, e.g. `pqc`'s `hndl/README.md` /
        `hndl/worksheet.md` if they mention a week number — check).
     b. For each hit, look up the referenced week number in the mapping table above and decide:
        - **This lesson's own number** → `{{ slot_label }}` (or `{{ ref('<this-slug>', link=True) }}` /
          `{{ labpath }}` / `{{ labname }}` if it's a path/link, not prose — same token vocabulary as the
          `software-security` import, see `tools/crossref.py` for the full list).
        - **The immediately preceding lesson, referred to as "last week"** → `{{ prev }}` (only use this
          when the text literally says "last/previous week", not a specific number — if it names a
          SPECIFIC week number, even if adjacent, prefer `{{ ref('<slug>') }}` naming that lesson
          directly, since that's more precise and self-documenting).
        - **Any other same-course week, by number** → `{{ ref('<slug>') }}` using the mapping table.
        - **A mention of a DIFFERENT course** (e.g. "software-security's Week 1") → leave as literal
          text, do NOT tokenize. This is the one case where a "Week N"-shaped match is correct to leave
          alone.
     c. Apply the replacements, changing ONLY the schedule-reference text — do not alter surrounding
        wording.
     d. Re-run the grep from step (a). Confirm every remaining hit is a deliberate cross-course mention
        (and note which ones, in your final report) — if anything else remains, you missed a case; go
        back to (b).
  4. Lint: `.venv/bin/python -c "from tools import validate; print('\n'.join(validate.lint_lesson('lessons/<slug>')) or 'clean')"`
     — fix anything flagged (this catches literal `Week N` and `slides/weekNN.md` patterns; it will NOT
     catch a bare `labs/weekNN-slug` path reference used in a shell command or "Working dir:" line —
     ALSO manually grep for that pattern, as was needed during the `software-security` import:
     `grep -noE "(labs/)?(week|day|session|lesson)[0-9]+-[a-z0-9-]+" lessons/<slug>/*.md` and tokenize
     any real self/cross-lesson path reference found (`{{ labpath }}` for a self-reference WITH a
     `labs/` prefix in the original text, `{{ labname }}` for a bare directory-name mention with NO
     `labs/` prefix, `{{ ref('<slug>', link=True) }}` for a cross-lesson link) — but leave alone any
     hit that's an arbitrary Docker image tag rather than a real navigation path (the
     `software-security` import found examples like `week13-hardened:lab`, a locally-chosen build tag
     that doesn't need to track the real schedule slot; if this course has anything similar, recognize
     the same pattern: used inside `docker build -t <name>` / `docker run <name>` / `docker tag`, not as
     a `cd`/`Working dir:`/file-path reference).
  5. Byte-check the lab code wasn't touched:
     `diff -rq "../KOSEN69 - security-cryptography/labs/<source-dir>" "lessons/<slug>"` should report
     differences ONLY in the `.md` files you tokenized, plus the removed `__pycache__` — every other
     file (code, configs, data files) must be byte-identical to the source. If diff shows anything else
     changed, restore it from source.

- [ ] **Step 2: After all 11 are imported, lint the whole library at once:**
```bash
.venv/bin/python -c "
from tools import validate
import os
for slug in sorted(os.listdir('lessons')):
    v = validate.lint_lesson(f'lessons/{slug}')
    print(slug, '->', v or 'clean')
"
```
  Every lesson (including the pre-existing `hash` pilot and all 12 `software-security` lessons) must
  print `clean`.

- [ ] **Step 3: Run the full suite** — `.venv/bin/python -m pytest tests/ -q` (no new tests in this
  task; confirms nothing broke — should still be 70 passing).

- [ ] **Step 4: Commit**
```bash
git add lessons/intro lessons/macs lessons/aes-modes lessons/key-exchanges lessons/aead \
        lessons/hybrid-encryption lessons/signatures-zkp lessons/secure-transport \
        lessons/e2e-encryption lessons/authentication lessons/pqc
git status --short          # verify ONLY these 11 lessons/ dirs are staged
git commit -m "import: remaining 11 security-cryptography lessons (intro through pqc)"
```

---

### Task 2: Write the manifest + render + parity-verify

**Files:**
- Create: `courses/security-cryptography.yml` (verbatim from "Source facts" above — **NOTE:** a
  different, PARTIAL manifest of this name may already exist from the original pilot task, scoped to
  just the `hash` lesson + one review slot — read it first; if it exists, REPLACE its contents with the
  full 19-slot version below rather than creating a duplicate or a second file)
- Create: `tests/test_parity_sc.py`

- [ ] **Step 1: Check for and replace/write `courses/security-cryptography.yml`** with the full manifest
  from "Source facts" above (19 slots, all 11 newly-imported lessons + the pre-existing `hash`).

- [ ] **Step 2: Write the parity test** — `tests/test_parity_sc.py` (a NEW file; mirror the structure of
  the existing `tests/test_parity_swsec.py` from the `software-security` import, adapted for this
  course's lessons and source paths):
```python
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_REPO = ROOT.parent / "KOSEN69 - security-cryptography"
SRC_LABS = SRC_REPO / "labs"

LESSON_DIRS = {
    "intro": "week01-intro", "hash": "week02-hash", "macs": "week03-macs",
    "aes-modes": "week04-aes-modes", "key-exchanges": "week05-key-exchanges", "aead": "week06-aead",
    "hybrid-encryption": "week10-hybrid-encryption", "signatures-zkp": "week11-signatures-zkp",
    "secure-transport": "week12-secure-transport", "e2e-encryption": "week13-e2e-encryption",
    "authentication": "week14-authentication", "pqc": "week15-pqc",
}

pytestmark = pytest.mark.skipif(not SRC_LABS.is_dir(), reason="source security-cryptography repo not present")


def _render(tmp):
    from tools import render
    render.render_course(str(ROOT / "courses" / "security-cryptography.yml"),
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
    out_lab = next(out.glob(f"labs/week*-{slug}"))
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
    out_lab = next(out.glob(f"labs/week*-{slug}"))
    for src in src_lab.rglob("*.md"):
        rel = src.relative_to(src_lab)
        dst = out_lab / rel
        assert dst.is_file(), f"{slug}: missing rendered {rel}"
        assert dst.read_text(encoding="utf-8") == src.read_text(encoding="utf-8"), \
            f"{slug}: rendered {rel} != current published content"
```
(Note this version's `test_markdown_matches_source` uses `rglob("*.md")` + `relative_to`, not a flat
`glob("*.md")` + filename join like the `software-security` version — this course's `pqc` lesson has
`.md` files nested inside `hndl/`, so the comparison must walk the whole tree, not just the lesson root.)

- [ ] **Step 3: Render + run.** First a manual sanity render:
```bash
.venv/bin/python -m tools.render courses/security-cryptography.yml --out _render/sc
find _render/sc/labs -maxdepth 1 -type d | sort
find _render/sc/labs/week15-pqc -type d   # confirm hndl/ came through
```
  Expect 12 `labs/weekNN-<slug>/` directories (weeks 1-6, 10-15), and `week15-pqc/hndl/` present as a
  subdirectory. Then:
```bash
.venv/bin/python -m pytest tests/test_parity_sc.py -q
```
  For any failure, the diff shows exactly which tokenization needs fixing — the fix ALWAYS goes in
  `lessons/<slug>/*.md` (never in the test, never in the manifest, never in the renderer). This is the
  same iterate-until-green process as the `software-security` import: investigate the ROOT CAUSE (a
  missed cross-ref, a slug that doesn't match the published directory name, a residual literal path) —
  do not weaken this test. If a lesson's rendered directory name doesn't match what's published (the
  same class of bug the `software-security` import hit for 3 lessons), rename the lesson's slug to match
  the published suffix exactly, update `lesson.yml`, the manifest, and this test's `LESSON_DIRS`
  together, and re-tokenize any self-references using the corrected slug — do not leave a slug/directory
  mismatch as literal text just to pass parity.

- [ ] **Step 4: Full suite** — `.venv/bin/python -m pytest tests/ -q` — all green.

- [ ] **Step 5: Commit**
```bash
git add courses/security-cryptography.yml tests/test_parity_sc.py
git status --short   # verify only these 2 files are staged (plus any lesson fixes from Step 3, called out explicitly if so)
git commit -m "manifest: full 19-slot security-cryptography course; byte-parity verified per lesson"
```

---

## Verification (before finishing the branch)

1. `.venv/bin/python -m pytest tests/ -q` — all green (70 baseline + ~1 + 24 parametrized parity tests
   ≈ 95, but don't assume the exact number — report what you observe).
2. `.venv/bin/python -m tools.render courses/security-cryptography.yml --out _render/sc` succeeds with
   no errors; `_render/sc/labs/week15-pqc/hndl/` exists and contains real files.
3. Manual: open `_render/sc/labs/week06-aead/README.md` and confirm the Week 3/Week 4 cross-references
   read naturally and resolve to real week labels (spot-check the densest cross-ref lesson).
4. `git log --oneline` on the branch shows 2 commits (Task 1-2), each independently green.

## Self-review

- **Spec coverage:** all 11 remaining lessons + the pre-existing `hash` pilot (12 total, matching
  `syllabus.md`'s "12 graded" weekly labs) · all 7 non-lesson calendar slots incl. midterm/final
  `phase` tags for future compressed-schedule readiness (no compressed manifest exists yet for this
  course, so no coverage test is written against it — that's a natural follow-on, not missing scope
  here) · the nested `hndl/` subdirectory and multi-flag `pqc` lesson explicitly handled · cross-course
  references explicitly identified as never-tokenized.
- **Type/name consistency:** the week-number→slug table is the single source of truth referenced by
  both Task 1 (tokenization) and Task 2 (manifest `schedule:` + test `LESSON_DIRS`) — cross-checked for
  agreement before this plan was finalized.
- **No placeholders:** every lesson's kind/flags/source-dir came from a direct read of the source repo
  (reproduced in "Source facts"). The manifest omits a `code:` field entirely (the pre-existing pilot
  manifest didn't have one either, and no real KOSEN course code for this course was found during this
  plan's research) rather than guessing a value — `code` is optional, unused metadata, not load-bearing
  for any test.
- **Lesson learned from `software-security`, applied here:** that import's real bugs (residual literal
  paths the initial pass missed; 3 slugs not matching published directory names) were caught by
  systematic re-grepping and the byte-parity test, not by getting the first pass perfect. This plan bakes
  that same discipline in as the PRIMARY method (Task 1 Step 1.3's tokenize-verify loop, Task 2 Step 3's
  "investigate root cause, rename if needed" instruction) rather than trying to exhaustively pre-solve
  every cross-reference by hand in this document, which — given this course's denser, less uniform
  cross-ref pattern — would be more likely to be wrong than the systematic loop is to miss something.
