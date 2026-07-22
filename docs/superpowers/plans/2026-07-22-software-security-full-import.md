# Software Security Full Import (19-week + MFU) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import all 12 real lessons of the `software-security` course into the shared library, write
its full 19-slot manifest and its 7-session MFU manifest (the concrete "same lessons, re-scheduled"
proof this whole project exists for), and verify both render to byte-parity with what is currently
published.

**Architecture:** Same engine as the pilot (`tools/model.py`, `crossref.py`, `validate.py`,
`render.py`), extended by three small, real gaps the source content surfaced:
1. A lesson can mint **more than one** `FLAG_*` (week04, week06, week10 each mint two) — `lesson.yml`'s
   `flag_key: str` becomes `flag_keys: list[str]`.
2. MFU packs **more than one lesson into the same session** (e.g. Session 1 = Week 1 + Week 2) —
   `validate_manifest`'s "duplicate slot" check must stop rejecting two *different* lessons sharing a
   slot number, while still rejecting the *same* lesson slug used twice (already correct).
3. **A compressed schedule must never silently drop required content.** The 16-week baseline
   (expanded to this course's real 19 calendar slots) is the source of truth for what MUST be taught;
   MFU compresses it into 7 sessions but every lesson-kind slot in the canonical manifest must still
   appear somewhere in the compressed one. This needs a general, reusable **coverage check** — not a
   hand-typed list of slugs a plan author has to remember to keep in sync — so it also protects every
   future compressed variant (a different institution, a future short course) automatically.

No other engine change is needed — `labdir()` already keys on slug (so co-scheduled lessons don't
collide) and `prev`/`next` already derive from schedule-list order, not slot number.

**Tech Stack:** Same as the pilot repo — Python 3.12, PyYAML, Jinja2, pytest, existing `.venv`.

**Working dir for every path below:** the monorepo root
`/Users/pop7/Library/CloudStorage/OneDrive-MonsterConnectCo.,Ltd/Lecture/KOSEN69 - curriculum`.
Run tests from there: `.venv/bin/python -m pytest tests/ -q` (33 pass at the start of this plan: the
26 engine tests + the 3-test parity suite + the hardening tests already there — verify the exact
starting count in Task 1 Step 0). The **source** repo is the filesystem sibling
`../KOSEN69 - software-security/`.

---

## Source facts (gathered directly from the source repo; used verbatim below — no placeholders)

### The 12 real lessons (have lab content) vs. 7 non-lesson calendar weeks

Determined by presence of substantial lab content (`docker-compose.yml`/`Dockerfile`/exploit scripts)
vs. thin review/exam/capstone folders (2–3 files, no lab). Verified by listing every `labs/week*/`
directory's file count and compose presence.

| Source dir | New slug | Lesson? |
|---|---|---|
| `week01-threat-modeling` | `threat-modeling` | yes |
| `week02-sdlc-tooling` | `sdlc-tooling` | yes |
| `week03-cryptography` | `crypto-fundamentals` | yes *(not `crypto` / `hash` / `macs` — those slugs belong to `security-cryptography`'s per-primitive weeks; this is a broad one-week survey, a different lesson)* |
| `week04-injection` | `injection` | yes |
| `week05-xss-client-side` | `xss` | yes |
| `week06-authn-authz` | `authn-authz` | yes |
| `week07-review-midterm-prep` | — | no (review) |
| `week08-midterm-written` | — | no (exam) |
| `week09-midterm-practical` | — | no (exam) |
| `week10-api-security` | `api-security` | yes |
| `week11-memory-safety-exploitation` | `memory-safety` | yes |
| `week12-supply-chain` | `supply-chain` | yes |
| `week13-cloud-container` | `cloud-container` | yes |
| `week14-ai-llm-security` | `ai-llm-security` | yes |
| `week15-devsecops-pipeline` | `devsecops-pipeline` | yes |
| `week16-capstone` | — | no — thin (3 files, no lab), and MFU's own syllabus states its content is *"assigned as self-study/team time... not new taught content"*, never occupying a session. Modeled as a non-lesson `project` slot. |
| `week17-review-final-prep` | — | no (review) |
| `week18-final-written` | — | no (exam) |
| `week19-final-ctf-capstone` | — | no (exam) |

### Per-lesson import facts (grepped directly from source; use exactly these)

| Slug | `flag_keys` (grep of `FLAG_*` in the lesson dir) | Cross-refs found in `README.md`/`worksheet.md` (tokenize each) |
|---|---|---|
| `threat-modeling` | `[]` | Self only: `**Week 1**` → `{{ slot_label }}`; `slides/week01.md` → `{{ slides }}`; `cd labs/week01-threat-modeling` → `cd {{ labpath }}`. **No `{{ prev }}`** — this is the first lesson. |
| `sdlc-tooling` | `[]` | `Week 1 *Lab 0*; skim last week's recap` → `{{ ref('threat-modeling') }} *Lab 0*; skim {{ prev }}'s recap`; self week/slides/labpath tokens; **forward ref**: `A deeper fuzzing+exploit lab follows in [Week 11](../week11-memory-safety-exploitation/)` → `[{{ ref('memory-safety') }}]({{ ref('memory-safety', link=True) }})`. |
| `crypto-fundamentals` | `[]` | `Week 1 *Lab 0*; skim last week's recap` → same pattern as above (`ref('threat-modeling')` + `{{ prev }}`); self tokens. |
| `injection` | `[FLAG_CMDI, FLAG_SQLI]` | Same `Week 1`/`last week`/self pattern. |
| `xss` | `[]` | Same pattern. |
| `authn-authz` | `[FLAG_IDOR, FLAG_JWT]` | Same pattern. |
| `api-security` | `[FLAG_BOLA, FLAG_MASSASSIGN]` | Same pattern. |
| `memory-safety` | `[FLAG_PWN]` | Same `Week 1`/`last week` pattern; self tokens (no incoming link text to fix here — the link target itself, since it's tokenized at the *source* lesson `sdlc-tooling`). |
| `supply-chain` | `[]` | Same pattern. |
| `cloud-container` | `[]` | Same pattern. |
| `ai-llm-security` | `[FLAG_PROMPTINJ]` | Same pattern. |
| `devsecops-pipeline` | `[FLAG_DEVSECOPS]` | Same pattern, **plus** a second file `README-pipeline.md` with a self-ref `"see week15 README"` → `"see {{ slot_label }}'s README"`. |

Every lesson from `sdlc-tooling` onward shares the exact same self + `{{ ref('threat-modeling') }}` +
`{{ prev }}` pattern for its "Before class" line — this is expected: every week in this course recaps
Week 1's environment setup and the immediately preceding week.

### The two manifests

**19-slot `courses/software-security.yml`** — every week keeps its current slot number (so this
manifest's render must byte-match the *currently published* repo, our parity gate):

```yaml
course:
  name: "Software Security"
  code: "1305315"
  brand: "KOSEN·KMITL"
  flag_salt_env: SWSEC_FLAG_SALT
  challenge_keys_env: AIRSEC_CHALLENGE_KEYS
  target_repo: "nutthakorn7/software-security"
schedule_unit: weeks
slot_label: "Week {n}"
schedule:
  - {slot: 1,  lesson: threat-modeling}
  - {slot: 2,  lesson: sdlc-tooling}
  - {slot: 3,  lesson: crypto-fundamentals}
  - {slot: 4,  lesson: injection}
  - {slot: 5,  lesson: xss}
  - {slot: 6,  lesson: authn-authz}
  - {slot: 7,  review: "Reflection & Review (pre-Midterm)"}
  - {slot: 8,  exam: "Midterm: Written / Concept Exam"}
  - {slot: 9,  exam: "Midterm: Hands-on CTF Practical"}
  - {slot: 10, lesson: api-security}
  - {slot: 11, lesson: memory-safety}
  - {slot: 12, lesson: supply-chain}
  - {slot: 13, lesson: cloud-container}
  - {slot: 14, lesson: ai-llm-security}
  - {slot: 15, lesson: devsecops-pipeline}
  - {slot: 16, project: "Capstone Studio & CTF Warm-up"}
  - {slot: 17, review: "Reflection & Review (pre-Final)"}
  - {slot: 18, exam: "Final: Written Exam"}
  - {slot: 19, exam: "Final: Capstone CTF Tournament + Project Demos"}
```

**7-session `courses/software-security-mfu.yml`** — from `syllabus-mfu.md` §5, mapped by **topic name**
(not the stale "Wk N" numbers in that doc's prose, which refer to an older 16-week baseline predating
this repo's 19-week restructure):

```yaml
course:
  name: "Software Security (MFU)"
  code: "1305315"
  brand: "KOSEN·KMITL"
  flag_salt_env: SWSEC_FLAG_SALT           # SAME salt as the main course — same institution/cohort family
  challenge_keys_env: AIRSEC_CHALLENGE_KEYS
  target_repo: "nutthakorn7/software-security"   # rendered into the SAME repo's mfu-specific paths — see Task 4
schedule_unit: sessions
slot_label: "Session {n}"
schedule:
  - {slot: 1, lesson: threat-modeling}
  - {slot: 1, lesson: sdlc-tooling}
  - {slot: 2, lesson: crypto-fundamentals}
  - {slot: 2, lesson: injection}
  - {slot: 3, lesson: xss}
  - {slot: 3, lesson: authn-authz}
  - {slot: 4, exam: "Midterm: written (AM) + CTF practical (PM)"}
  - {slot: 5, lesson: api-security}
  - {slot: 5, lesson: memory-safety}
  - {slot: 5, lesson: supply-chain}
  - {slot: 6, lesson: cloud-container}
  - {slot: 6, lesson: ai-llm-security}
  - {slot: 6, lesson: devsecops-pipeline}
  - {slot: 7, exam: "Final: written (AM) + capstone CTF + project demos (PM)"}
```

Note: `week16-capstone` content is deliberately **absent** from this manifest (per the source syllabus,
it is self-study between Session 6 and 7, never taught in a session) — this is not an oversight.

---

### Task 1: Model + validator changes for real multi-flag and multi-lesson-per-slot content

**Files:**
- Modify: `tools/model.py`, `tools/validate.py`
- Modify: `tests/test_model.py`, `tests/test_validate.py` (extend existing files — do not create new ones)

- [ ] **Step 0: Confirm the starting baseline.** Run `.venv/bin/python -m pytest tests/ -q` and record
  the pass count before making any change (expected 29, per the pilot plan's final state — if different,
  stop and report the discrepancy rather than proceeding on a wrong assumption).

- [ ] **Step 1: Write the failing tests.** Add to `tests/test_model.py`:
```python
def test_lesson_flag_keys_list(tmp_path):
    d = tmp_path / "lessons" / "injection"
    _write(str(d / "lesson.yml"), """
        slug: injection
        title: "Injection & Input Handling"
        kind: LAB
        flag_keys: [cmdi, sqli]
    """)
    lsn = model.load_lesson(str(d))
    assert lsn.flag_keys == ["cmdi", "sqli"]


def test_lesson_flag_keys_defaults_empty(tmp_path):
    d = tmp_path / "lessons" / "threat-modeling"
    _write(str(d / "lesson.yml"), "slug: threat-modeling\ntitle: t\nkind: LAB\n")
    lsn = model.load_lesson(str(d))
    assert lsn.flag_keys == []
```
Add to `tests/test_validate.py`:
```python
def test_multiple_lessons_share_one_slot_is_ok(tmp_path):
    lessons = _lessons(tmp_path, {"threat-modeling": [], "sdlc-tooling": []})
    m = _manifest([{"slot": 1, "kind": "lesson", "value": "threat-modeling"},
                   {"slot": 1, "kind": "lesson", "value": "sdlc-tooling"}])
    assert validate.validate_manifest(m, lessons) == []


def test_non_lesson_slots_still_reject_duplicates(tmp_path):
    lessons = _lessons(tmp_path, {})
    m = _manifest([{"slot": 4, "kind": "exam", "value": "Midterm A"},
                   {"slot": 4, "kind": "exam", "value": "Midterm B"}])
    assert any("duplicate slot 4" in e for e in validate.validate_manifest(m, lessons))


def test_missing_lessons_finds_gap(tmp_path):
    canonical = _manifest([{"slot": 1, "kind": "lesson", "value": "threat-modeling"},
                           {"slot": 2, "kind": "lesson", "value": "sdlc-tooling"}])
    compressed = _manifest([{"slot": 1, "kind": "lesson", "value": "threat-modeling"}])
    assert validate.missing_lessons(canonical, compressed) == {"sdlc-tooling"}


def test_missing_lessons_empty_when_fully_covered(tmp_path):
    canonical = _manifest([{"slot": 1, "kind": "lesson", "value": "threat-modeling"},
                           {"slot": 2, "kind": "lesson", "value": "sdlc-tooling"}])
    # the compressed manifest packs both into one slot — order/slot differ, content is still covered
    compressed = _manifest([{"slot": 1, "kind": "lesson", "value": "sdlc-tooling"},
                            {"slot": 1, "kind": "lesson", "value": "threat-modeling"}])
    assert validate.missing_lessons(canonical, compressed) == set()


def test_missing_lessons_ignores_non_lesson_slots():
    """Review/exam/project slots are calendar entries, not required content — a compressed manifest
    dropping/merging them is not a coverage gap; only missing LESSON slugs are."""
    canonical = _manifest([{"slot": 1, "kind": "lesson", "value": "threat-modeling"},
                           {"slot": 2, "kind": "review", "value": "Review week"}])
    compressed = _manifest([{"slot": 1, "kind": "lesson", "value": "threat-modeling"},
                            {"slot": 2, "kind": "exam", "value": "Combined review+exam session"}])
    assert validate.missing_lessons(canonical, compressed) == set()
```
(`test_duplicate_slot` already in the file used two *lesson* slots colliding — update that existing test
to expect NO error now that duplicate lesson slots are legal; rename it
`test_duplicate_lesson_slots_are_allowed` and assert `== []`, since this plan's whole point is that this
case must now succeed. Do not leave the old contradictory assertion in place.)

- [ ] **Step 2: Run, confirm failures** — `flag_keys` doesn't exist yet (`TypeError`/`AttributeError`);
  the slot-collision tests fail because the current code still flags any repeated slot number;
  `missing_lessons` doesn't exist yet (`AttributeError`).

- [ ] **Step 3: Update `tools/model.py`.** In the `Lesson` dataclass, replace:
```python
    flag_key: str | None = None
```
with:
```python
    flag_keys: list = field(default_factory=list)
```
(`field` and `field(default_factory=list)` are already imported/used elsewhere in this file for `tags`.)

- [ ] **Step 4: Update `tools/validate.py`'s `validate_manifest`.** Only flag a duplicate slot number
  when it is **not** two distinct lessons — i.e. drop the blanket duplicate-slot check for `kind ==
  "lesson"` entries and keep it for everything else. Replace the function body's slot-tracking with:
```python
def validate_manifest(manifest, lessons_by_slug):
    """Return a list of human-readable error strings (empty == valid)."""
    errors = []
    seen_nonlesson_slots = set()      # non-lesson slots (exam/review/project/...) are one-per-slot
    seen_at = {}                      # lesson slug -> the (first) slot it's scheduled at, in order
    for s in manifest.schedule:
        if s.kind != "lesson":
            if s.slot in seen_nonlesson_slots:
                errors.append(f"duplicate slot {s.slot}")
            seen_nonlesson_slots.add(s.slot)
            continue
        # Multiple DIFFERENT lessons may legitimately share one slot (e.g. an MFU session packing
        # several weeks into one day) — labdir() already keys on slug, so no path collision results.
        if s.value in seen_at:
            errors.append(f"lesson '{s.value}' scheduled more than once (slots must map to distinct lessons)")
            continue
        if s.value not in lessons_by_slug:
            errors.append(f"slot {s.slot}: unknown lesson slug '{s.value}'")
            continue
        for pre in lessons_by_slug[s.value].prereqs:
            if pre not in seen_at:
                errors.append(
                    f"slot {s.slot}: lesson '{s.value}' needs prereq '{pre}' scheduled earlier "
                    f"(it is missing or comes later)")
        seen_at[s.value] = s.slot
    return errors
```

- [ ] **Step 5: Add the coverage-check function to `tools/validate.py`.** The 16-week baseline is the
  source of truth for what must be taught; a compressed schedule (MFU, a future short course, a
  different institution) must never silently drop a required lesson. This is a general check — it takes
  two `Manifest`s and returns which lesson slugs the first requires but the second omits, independent
  of which slot number or session either one uses it at:
```python
def missing_lessons(canonical_manifest, compressed_manifest):
    """Lesson slugs required by canonical_manifest but absent from compressed_manifest. Only
    lesson-kind slots count as "required content" — non-lesson calendar entries (exam/review/project)
    may be freely merged or dropped by a compressed schedule without that being a coverage gap."""
    return set(canonical_manifest.lesson_slugs()) - set(compressed_manifest.lesson_slugs())
```

- [ ] **Step 6: Run tests, confirm pass** — then the FULL suite: `.venv/bin/python -m pytest tests/ -q`.
  Every pre-existing test must still pass EXCEPT the one you deliberately updated in Step 1
  (`test_duplicate_lesson_slots_are_allowed`) — if any other pre-existing test now fails, investigate;
  do not weaken it to force a pass.

- [ ] **Step 7: Commit**
```bash
git add tools/model.py tools/validate.py tests/test_model.py tests/test_validate.py
git commit -m "model+validate: multi-flag lessons (flag_keys list), allow distinct lessons sharing one slot, coverage check"
```

---

### Task 2: Import all 12 lessons

Apply the SAME recipe already proven in the pilot (copy → write `lesson.yml` → tokenize → lint clean) to
all 12 lessons in the table above. This is one task because the procedure is identical per lesson —
only the input data (the table above) differs, and that data is now fully specified, not something the
executor derives.

**Files:** Create `lessons/<slug>/` for each of the 12 slugs in the table above.

- [ ] **Step 1: For EACH of the 12 lessons, in the order listed in the source-facts table:**
  1. Copy: `cp -R "../KOSEN69 - software-security/labs/<source-dir>"/. "lessons/<slug>/"` — then
     `rm -rf "lessons/<slug>/__pycache__"` (build artifacts must not be imported; none of the other
     source dirs had anything else to exclude, but re-check each with `find lessons/<slug> -iname
     "__pycache__" -o -iname "*.pyc"` and remove any found).
  2. Write `lessons/<slug>/lesson.yml`:
     ```yaml
     slug: <slug>
     title: "<the H1 of the copied README.md, with any leading 'Week N — ' stripped>"
     kind: LAB
     duration_min: 180
     tags: [<2-4 short topic tags inferred from the README's own '**Concepts:**'/'**OWASP 2025:**' line>]
     cwe: [<the CWEs cited in the README's own CWE line, verbatim — do not invent one>]
     prereqs: []
     flag_keys: <the exact list from the source-facts table above, lowercased, e.g. [cmdi, sqli]; `[]` if none>
     ```
  3. Tokenize: apply the cross-ref replacements from the source-facts table's "Cross-refs" column to
     `README.md` and `worksheet.md` (and `README-pipeline.md` for `devsecops-pipeline`). Change ONLY the
     schedule-reference text; do not alter surrounding wording.
  4. Lint: `.venv/bin/python -c "from tools import validate; print('\n'.join(validate.lint_lesson('lessons/<slug>')) or 'clean')"`
     — fix anything still flagged, matching a token from the vocabulary in `tools/crossref.py`
     (`slot_label`, `slides`, `labpath`, `prev`, `ref(...)`) to what the line actually means. Re-run
     until `clean`.
  5. Byte-check the lab code: `diff -rq "../KOSEN69 - software-security/labs/<source-dir>" "lessons/<slug>"`
     should report differences **only** in `README.md`/`worksheet.md`/(`README-pipeline.md` for
     devsecops-pipeline) and the removed `__pycache__` — every other file must be untouched.

- [ ] **Step 2: After all 12 are imported, lint the whole library at once:**
```bash
.venv/bin/python -c "
from tools import validate
import os
for slug in sorted(os.listdir('lessons')):
    v = validate.lint_lesson(f'lessons/{slug}')
    print(slug, '->', v or 'clean')
"
```
  Every lesson must print `clean`.

- [ ] **Step 3: Run the full suite** — `.venv/bin/python -m pytest tests/ -q` (no new tests in this
  task; confirms nothing broke).

- [ ] **Step 4: Commit**
```bash
git add lessons/threat-modeling lessons/sdlc-tooling lessons/crypto-fundamentals lessons/injection \
        lessons/xss lessons/authn-authz lessons/api-security lessons/memory-safety \
        lessons/supply-chain lessons/cloud-container lessons/ai-llm-security lessons/devsecops-pipeline
git status --short          # verify ONLY the 12 lessons/ dirs are staged
git commit -m "import: all 12 software-security lessons (threat-modeling through devsecops-pipeline)"
```

---

### Task 3: Write both manifests + render + parity-verify the 19-slot course

**Files:**
- Create: `courses/software-security.yml` (verbatim from "Source facts" above)
- Create: `tests/test_parity_swsec.py`

- [ ] **Step 1: Write `courses/software-security.yml`** — copy the YAML block verbatim from the
  "Source facts" section above.

- [ ] **Step 2: Write the failing parity test** — `tests/test_parity_swsec.py`:
```python
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_REPO = ROOT.parent / "KOSEN69 - software-security"
SRC_LABS = SRC_REPO / "labs"

LESSON_DIRS = {
    "threat-modeling": "week01-threat-modeling", "sdlc-tooling": "week02-sdlc-tooling",
    "crypto-fundamentals": "week03-cryptography", "injection": "week04-injection",
    "xss": "week05-xss-client-side", "authn-authz": "week06-authn-authz",
    "api-security": "week10-api-security", "memory-safety": "week11-memory-safety-exploitation",
    "supply-chain": "week12-supply-chain", "cloud-container": "week13-cloud-container",
    "ai-llm-security": "week14-ai-llm-security", "devsecops-pipeline": "week15-devsecops-pipeline",
}

pytestmark = pytest.mark.skipif(not SRC_LABS.is_dir(), reason="source software-security repo not present")


def _render(tmp):
    from tools import render
    render.render_course(str(ROOT / "courses" / "software-security.yml"),
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
    for src in src_lab.glob("*.md"):
        dst = out_lab / src.name
        assert dst.is_file(), f"{slug}: missing rendered {src.name}"
        assert dst.read_text(encoding="utf-8") == src.read_text(encoding="utf-8"), \
            f"{slug}: rendered {src.name} != current published content"
```

- [ ] **Step 3: Render + run.** First a manual sanity render:
```bash
.venv/bin/python -m tools.render courses/software-security.yml --out _render/swsec
find _render/swsec/labs -maxdepth 1 -type d | sort
```
  Expect exactly 12 `labs/weekNN-<slug>/` directories at the slots from the manifest (week01, 02, 03,
  04, 05, 06, week10 through week15). Then:
```bash
.venv/bin/python -m pytest tests/test_parity_swsec.py -q
```
  For any failure, the diff shows exactly which tokenization to fix (in `lessons/<slug>/*.md`, from
  Task 2) — reconcile there, never here. Do not weaken this test.

- [ ] **Step 4: Full suite** — `.venv/bin/python -m pytest tests/ -q` — all green.

- [ ] **Step 5: Commit**
```bash
git add courses/software-security.yml tests/test_parity_swsec.py
git commit -m "manifest: full 19-slot software-security course; byte-parity verified per lesson"
```

---

### Task 4: Write the MFU manifest + verify it renders (structurally, not against a pre-existing generated repo)

MFU has no prior *generated* tree to diff against (the current `syllabus-mfu.md` is hand-written prose,
not a rendered artifact) — so this task's gate is **structural + content correctness**, not byte-parity:
every lesson from Task 3 must appear, session-labelled, with the *same* lesson content byte-identical
to the library source (proving re-scheduling truly changes nothing but labels), and the non-lesson
session entries must be present.

**Files:**
- Create: `courses/software-security-mfu.yml` (verbatim from "Source facts" above)
- Modify: `tests/test_parity_swsec.py` (add MFU-specific assertions)

- [ ] **Step 1: Write `courses/software-security-mfu.yml`** — copy the YAML block verbatim from the
  "Source facts" section above.

- [ ] **Step 2: Write the failing test** — append to `tests/test_parity_swsec.py`:
```python
MFU_MANIFEST = ROOT / "courses" / "software-security-mfu.yml"


def _render_mfu(tmp):
    from tools import render
    render.render_course(str(MFU_MANIFEST), lessons_root=str(ROOT / "lessons"), out_dir=str(tmp / "mfu"))
    return tmp / "mfu"


def test_mfu_sessions_pack_multiple_lessons(tmp_path):
    out = _render_mfu(tmp_path)
    # Session 1 packs threat-modeling + sdlc-tooling — both must render, both labelled "Session 1",
    # in DISTINCT lab dirs (proving labdir()'s slug-keying avoids collision).
    tm = out / "labs" / "session1-threat-modeling" / "README.md"
    sdlc = out / "labs" / "session1-sdlc-tooling" / "README.md"
    assert tm.is_file() and sdlc.is_file()
    assert "Session 1" in tm.read_text(encoding="utf-8")
    assert "Session 1" in sdlc.read_text(encoding="utf-8")
    # No lesson in this course has a slides.md (confirmed: none of the 12 source dirs contain one —
    # course slides live in the source repo's separate top-level slides/, not per-lab), so no
    # out/slides/ output is expected here; not asserted.


def test_mfu_content_matches_library_source_verbatim(tmp_path):
    """Re-scheduling changes only the label, never the substance: strip the two lines that legitimately
    differ (the schedule label line and the recap/labpath line) and the rest must be identical between
    the 19-slot render and the MFU render of the SAME lesson."""
    from tools import render
    out19 = tmp_path / "out19"
    render.render_course(str(ROOT / "courses" / "software-security.yml"),
                         lessons_root=str(ROOT / "lessons"), out_dir=str(out19))
    out_mfu = _render_mfu(tmp_path)
    a = (out19 / "labs" / "week01-threat-modeling" / "README.md").read_text(encoding="utf-8")
    b = (out_mfu / "labs" / "session1-threat-modeling" / "README.md").read_text(encoding="utf-8")
    a_lines = [l for l in a.splitlines() if "Week 1" not in l]
    b_lines = [l for l in b.splitlines() if "Session 1" not in l]
    assert a_lines == b_lines, "content diverged between the 19-slot and MFU renderings of the same lesson"


def test_mfu_covers_every_required_lesson():
    """The 16-week baseline (this course's real 19-slot manifest) is the source of truth for what
    MUST be taught. MFU compresses it into 7 sessions, but nothing required may silently vanish in
    the compression — checked generally via validate.missing_lessons(), not a hand-typed slug list,
    so this guard also protects every future compressed variant (a different institution, a short
    course) without anyone having to remember to update a duplicated list here."""
    from tools import model, validate
    canonical = model.load_manifest(str(ROOT / "courses" / "software-security.yml"))
    mfu = model.load_manifest(str(MFU_MANIFEST))
    assert validate.missing_lessons(canonical, mfu) == set()


def test_mfu_capstone_deliberately_absent():
    """week16-capstone is explicitly self-study between sessions in the source syllabus — it must
    never be scheduled as a lesson in the MFU manifest."""
    from tools import model
    m = model.load_manifest(str(MFU_MANIFEST))
    assert "capstone" not in m.lesson_slugs()
```
- [ ] **Step 3: Run, reconcile, confirm pass** — `.venv/bin/python -m pytest tests/test_parity_swsec.py -q`.
  `test_mfu_content_matches_library_source_verbatim` is the real proof this whole project set out to
  build: the exact same lesson, rendered under two different schedules, is identical apart from its own
  label line. If it fails, the diff shows a token that didn't fully account for the label (e.g. a
  leftover hard-coded "Week" instead of `{{ slot_label }}`) — fix in `lessons/<slug>/README.md`.

- [ ] **Step 4: Full suite** — `.venv/bin/python -m pytest tests/ -q` — all green.

- [ ] **Step 5: Commit**
```bash
git add courses/software-security-mfu.yml tests/test_parity_swsec.py
git commit -m "manifest: MFU 7-session schedule; proves re-scheduling changes only the label"
```

---

## Verification (before finishing the branch)

1. `.venv/bin/python -m pytest tests/ -q` — all green (Task-1 model/validate additions + 12 imported
   lessons + both manifests' parity suites, on top of the pilot's 29).
2. `.venv/bin/python -m tools.render courses/software-security.yml --out _render/swsec` and
   `.venv/bin/python -m tools.render courses/software-security-mfu.yml --out _render/swsec-mfu` both
   succeed with no errors.
3. Manual: open `_render/swsec-mfu/labs/session1-threat-modeling/README.md` and
   `_render/swsec-mfu/labs/session1-sdlc-tooling/README.md` and confirm both correctly say "Session 1"
   with real, readable content — not a token artifact.
4. `git log --oneline` on the branch shows 4 commits (Task 1–4), each independently green.

## Self-review

- **Spec coverage:** flag_keys list (spec's `flag_key` example was singular; this plan generalizes it —
  the design's §4 example is illustrative, not a hard singular-only contract) · multi-lesson-per-slot
  (spec's non-goal #1 already anticipated re-scheduling as the *only* form of reuse; this is exactly
  that, just N lessons at once) · full 19-slot import + non-lesson calendar entries (design §5) · MFU as
  "just another manifest" (design §1's founding motivation — this task is the concrete payoff) ·
  byte-parity gate (design §10/§11) for both manifests · **coverage guarantee** (a requirement raised
  after the design was approved: the 16-week baseline must fully survive a 7-session compression, machine
  -checked via `validate.missing_lessons()` rather than trusted by inspection — this generalizes beyond
  MFU to any future compressed variant for free).
- **Type/name consistency:** `Lesson.flag_keys` (renamed from `flag_key`) is used identically in Task 1's
  model change and Task 2's per-lesson `lesson.yml` write-up. `validate_manifest`'s new
  `seen_nonlesson_slots`/`seen_at` variables are internal to Task 1 and don't leak into any other
  module's public API. All 12 slugs in Task 2's table match exactly what Task 3/4's `LESSON_DIRS` dict
  and manifest `schedule:` blocks reference — cross-checked against the source-facts table at the top.
- **No placeholders:** every lesson's `flag_keys`, cross-ref list, and manifest slot came from a real
  grep/read of the source repo (reproduced in this plan's "Source facts" section), not a "figure it out"
  instruction. The one open judgment call left to the executor — each lesson's `tags`/`cwe` values in
  Task 2 Step 1.2 — is explicitly scoped to "read the README's own stated Concepts/CWE line," not
  invented.
