# Rendering Machinery + Single-Lesson Pilot — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended)
> or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Build the lesson-library rendering engine (data model, cross-reference resolution, manifest
validator, renderer) and prove it end-to-end by importing one real `security-cryptography` lesson and
rendering it back to byte-parity with the current published content.

**Architecture:** A lesson is a schedule-agnostic folder (`lessons/<slug>/` with `lesson.yml` + content).
A course is a manifest (`courses/<course>.yml`) mapping lesson slugs to schedule slots. `tools/render.py`
reads a manifest, resolves cross-reference tokens against the course's `slug→slot` map, and emits the
course's student-facing tree. Full design: `docs/superpowers/specs/2026-07-22-cross-course-lesson-library-design.md`.

**Tech Stack:** Python 3.12, `PyYAML` (parse lesson.yml/manifests), `Jinja2` (cross-ref token rendering),
`pytest`. No runtime services.

**Working dir for every path below:** the monorepo root
`/Users/pop7/Library/CloudStorage/OneDrive-MonsterConnectCo.,Ltd/Lecture/KOSEN69 - curriculum`.
Run tests from there: `.venv/bin/python -m pytest tests/ -q`.

**Refinement of the spec:** the spec's §4 shows an illustrative `lab/` subdir. This plan uses a **flat
lesson** (all content files at `lessons/<slug>/` root; `slides.md` special-cased to the repo's
`slides/` dir on render) because the current course repos are flat and this makes parity trivial. Update
the spec's §4 to match at the end of Task 6.

---

## File structure

- `requirements.txt` (NEW) — `PyYAML`, `Jinja2`, `pytest`.
- `tools/__init__.py` (NEW) — marks `tools` a package.
- `tools/model.py` (NEW) — `Lesson`, `Slot`, `Manifest` dataclasses + loaders.
- `tools/crossref.py` (NEW) — the Jinja token environment (`slides`, `ref`, `prev`, `next`, `slot`, `slot_label`, `brand`).
- `tools/validate.py` (NEW) — manifest validation + lesson-invariant linter.
- `tools/render.py` (NEW) — manifest → course tree; CLI entrypoint.
- `lessons/hash/` (NEW) — the pilot lesson, imported from `security-cryptography/labs/week02-hash/`.
- `courses/security-cryptography.yml` (NEW) — partial manifest (the pilot lesson + a couple of slots).
- `tests/conftest.py`, `tests/test_model.py`, `tests/test_crossref.py`, `tests/test_validate.py`,
  `tests/test_render.py`, `tests/test_parity.py` (NEW).

Slot/file conventions the renderer uses (locked here so every task agrees):
- `slotfile(unit, n)`: `weeks→f"week{n:02d}"`, `days→f"day{n}"`, `sessions→f"session{n}"`, `lessons→f"lesson{n:02d}"`.
- `labdir(slotfile, slug)`: `f"{slotfile}-{slug}"` (e.g. `week02-hash`).
- `slot_label`: from the manifest's `slot_label` template, e.g. `"Week {n}".format(n=slot)` → `"Week 2"`.

---

### Task 1: Repo deps + data model (`tools/model.py`)

**Files:**
- Create: `requirements.txt`, `tools/__init__.py`, `tools/model.py`, `tests/conftest.py`, `tests/test_model.py`

- [ ] **Step 1: Write `requirements.txt`**

```
PyYAML>=6.0
Jinja2>=3.1
pytest>=8.0
```

- [ ] **Step 2: Create venv + install**

Run:
```bash
python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt
```

- [ ] **Step 3: Create `tools/__init__.py`** (empty file).

- [ ] **Step 4: Write `tests/conftest.py`** — put the repo root on `sys.path` so `import tools...` works.

```python
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

- [ ] **Step 5: Write the failing test** — `tests/test_model.py`

```python
import os, textwrap
from tools import model


def _write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(s))


def test_load_lesson(tmp_path):
    d = tmp_path / "lessons" / "hash"
    _write(str(d / "lesson.yml"), """
        slug: hash
        title: "Hashing & Cookie Forgery"
        kind: LAB
        duration_min: 180
        tags: [crypto, hashing]
        prereqs: []
        flag_key: hash
    """)
    lsn = model.load_lesson(str(d))
    assert lsn.slug == "hash" and lsn.kind == "LAB" and lsn.flag_key == "hash"
    assert lsn.dir == str(d)


def test_load_manifest(tmp_path):
    p = tmp_path / "courses" / "sc.yml"
    _write(str(p), """
        course: {name: "Security & Cryptography", brand: "KOSEN·KMITL", flag_salt_env: SC_FLAG_SALT}
        schedule_unit: weeks
        slot_label: "Week {n}"
        target_repo: "nutthakorn7/security-cryptography"
        schedule:
          - {slot: 2, lesson: hash}
          - {slot: 7, review: "Midterm review"}
          - {slot: 8, exam: "Midterm (written)"}
    """)
    m = model.load_manifest(str(p))
    assert m.schedule_unit == "weeks" and m.course["brand"] == "KOSEN·KMITL"
    assert [(s.slot, s.kind, s.value) for s in m.schedule] == [
        (2, "lesson", "hash"), (7, "review", "Midterm review"), (8, "exam", "Midterm (written)")]
    assert m.lesson_slugs() == ["hash"]
```

- [ ] **Step 6: Run it, confirm it fails** — `.venv/bin/python -m pytest tests/test_model.py -q` → `ModuleNotFoundError: tools.model`.

- [ ] **Step 7: Write `tools/model.py`**

```python
# tools/model.py — data model for lessons and course manifests.
import os
from dataclasses import dataclass, field

import yaml

# The recognised non-lesson slot kinds (a slot is either a lesson or one of these calendar entries).
NON_LESSON_KINDS = ("exam", "review", "project", "holiday", "break")


@dataclass
class Lesson:
    slug: str
    title: str
    kind: str                      # LAB | HYBRID | CONCEPTUAL
    duration_min: int = 0
    tags: list = field(default_factory=list)
    cwe: list = field(default_factory=list)
    prereqs: list = field(default_factory=list)
    flag_key: str | None = None
    dir: str = ""                  # filesystem path to lessons/<slug>/


def load_lesson(lesson_dir):
    with open(os.path.join(lesson_dir, "lesson.yml"), encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Lesson(dir=lesson_dir, **data)


def load_lessons(lessons_root):
    """Return {slug: Lesson} for every lessons/<slug>/lesson.yml under lessons_root."""
    out = {}
    if not os.path.isdir(lessons_root):
        return out
    for name in sorted(os.listdir(lessons_root)):
        d = os.path.join(lessons_root, name)
        if os.path.isfile(os.path.join(d, "lesson.yml")):
            lsn = load_lesson(d)
            out[lsn.slug] = lsn
    return out


@dataclass
class Slot:
    slot: int
    kind: str                      # "lesson" or a NON_LESSON_KINDS value
    value: str                     # lesson slug, or the calendar-entry title


@dataclass
class Manifest:
    course: dict
    schedule_unit: str
    slot_label: str
    target_repo: str
    schedule: list                 # list[Slot]
    path: str = ""

    def lesson_slugs(self):
        return [s.value for s in self.schedule if s.kind == "lesson"]


def _parse_slot(entry):
    e = dict(entry)
    slot = e.pop("slot")
    # exactly one remaining key names the kind; lesson is the common case
    if not e:
        raise ValueError(f"slot {slot} has no kind (expected 'lesson' or one of {NON_LESSON_KINDS})")
    if len(e) != 1:
        raise ValueError(f"slot {slot} has multiple kinds {list(e)}; a slot carries exactly one")
    kind, value = next(iter(e.items()))
    if kind != "lesson" and kind not in NON_LESSON_KINDS:
        raise ValueError(f"slot {slot}: unknown kind '{kind}'")
    return Slot(slot=slot, kind=kind, value=value)


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f) or {}
    return Manifest(
        course=d["course"],
        schedule_unit=d["schedule_unit"],
        slot_label=d["slot_label"],
        target_repo=d["target_repo"],
        schedule=[_parse_slot(x) for x in d["schedule"]],
        path=path,
    )
```

- [ ] **Step 8: Run tests, confirm pass** — `.venv/bin/python -m pytest tests/test_model.py -q`.

- [ ] **Step 9: Commit**

```bash
git add requirements.txt tools/__init__.py tools/model.py tests/conftest.py tests/test_model.py
git commit -m "model: load lessons + course manifests (schedule-agnostic)"
```

---

### Task 2: Cross-reference token resolution (`tools/crossref.py`)

The heart of re-scheduling: a lesson references others by slug; the renderer turns each token into this
course's slot label. Uses `StrictUndefined` so an unresolved token fails the render loudly.

**Files:**
- Create: `tools/crossref.py`, `tests/test_crossref.py`

- [ ] **Step 1: Write the failing test** — `tests/test_crossref.py`

```python
import pytest
from tools import crossref, model


def _manifest():
    return model.Manifest(
        course={"brand": "KOSEN·KMITL"},
        schedule_unit="weeks", slot_label="Week {n}",
        target_repo="x/y",
        schedule=[model.Slot(2, "lesson", "hash"),
                  model.Slot(3, "lesson", "macs"),
                  model.Slot(5, "lesson", "key-exchange")],
    )


def test_ref_resolves_to_slot_label():
    ctx = crossref.context(_manifest(), current_slug="macs")
    assert crossref.render("builds on {{ ref('hash') }}", ctx) == "builds on Week 2"


def test_self_tokens():
    ctx = crossref.context(_manifest(), current_slug="macs")
    assert crossref.render("{{ slot_label }} · slides {{ slides }} · {{ brand }}", ctx) \
        == "Week 3 · slides slides/week03.md · KOSEN·KMITL"
    assert crossref.render("cd {{ labpath }}", ctx) == "cd labs/week03-macs"


def test_prev_next():
    ctx = crossref.context(_manifest(), current_slug="macs")
    assert crossref.render("{{ prev }} / {{ next }}", ctx) == "Week 2 / Week 5"


def test_ref_link():
    ctx = crossref.context(_manifest(), current_slug="key-exchange")
    assert crossref.render("{{ ref('hash', link=True) }}", ctx) == "../week02-hash/"


def test_unscheduled_ref_raises():
    ctx = crossref.context(_manifest(), current_slug="macs")
    with pytest.raises(crossref.CrossRefError):
        crossref.render("{{ ref('not-in-course') }}", ctx)


def test_plain_markdown_untouched():
    ctx = crossref.context(_manifest(), current_slug="hash")
    assert crossref.render("# Hashing\nNo tokens here.\n", ctx) == "# Hashing\nNo tokens here.\n"
```

- [ ] **Step 2: Run it, confirm it fails** — `AttributeError`/`ModuleNotFoundError`.

- [ ] **Step 3: Write `tools/crossref.py`**

```python
# tools/crossref.py — resolve slug-based cross-reference tokens against a course's schedule.
import jinja2


class CrossRefError(Exception):
    pass


def slotfile(unit, n):
    if unit == "weeks":
        return f"week{n:02d}"
    if unit == "days":
        return f"day{n}"
    if unit == "sessions":
        return f"session{n}"
    if unit == "lessons":
        return f"lesson{n:02d}"
    raise CrossRefError(f"unknown schedule_unit '{unit}'")


def labdir(unit, n, slug):
    return f"{slotfile(unit, n)}-{slug}"


def context(manifest, current_slug):
    """Build the Jinja render context (values + callables) for one lesson in one course."""
    unit = manifest.schedule_unit
    label_tmpl = manifest.slot_label
    slug_to_slot = {s.value: s.slot for s in manifest.schedule if s.kind == "lesson"}
    ordered = [s.value for s in manifest.schedule if s.kind == "lesson"]

    if current_slug not in slug_to_slot:
        raise CrossRefError(f"lesson '{current_slug}' is not scheduled in this course")
    here = ordered.index(current_slug)

    def label(slug):
        if slug not in slug_to_slot:
            raise CrossRefError(f"ref('{slug}') — not scheduled in this course")
        return label_tmpl.format(n=slug_to_slot[slug])

    def ref(slug, link=False):
        if link:
            if slug not in slug_to_slot:
                raise CrossRefError(f"ref('{slug}', link=True) — not scheduled in this course")
            return f"../{labdir(unit, slug_to_slot[slug], slug)}/"
        return label(slug)

    my_slot = slug_to_slot[current_slug]
    return {
        "ref": ref,
        "slides": f"slides/{slotfile(unit, my_slot)}.md",          # this lesson's slide path
        "labpath": f"labs/{labdir(unit, my_slot, current_slug)}",  # this lesson's lab dir (for `cd labs/…`)
        "slot": my_slot,
        "slot_label": label_tmpl.format(n=my_slot),
        "prev": label(ordered[here - 1]) if here > 0 else "",
        "next": label(ordered[here + 1]) if here < len(ordered) - 1 else "",
        "brand": manifest.course.get("brand", ""),
    }


_ENV = jinja2.Environment(undefined=jinja2.StrictUndefined, autoescape=False,
                          keep_trailing_newline=True)


def render(text, ctx):
    try:
        return _ENV.from_string(text).render(**ctx)
    except jinja2.UndefinedError as e:
        raise CrossRefError(str(e)) from e
```

- [ ] **Step 4: Run tests, confirm pass** — `.venv/bin/python -m pytest tests/test_crossref.py -q`.

- [ ] **Step 5: Commit**

```bash
git add tools/crossref.py tests/test_crossref.py
git commit -m "crossref: resolve slug tokens (ref/slides/prev/next) to course slot labels"
```

---

### Task 3: Manifest validation + lesson-invariant lint (`tools/validate.py`)

**Files:**
- Create: `tools/validate.py`, `tests/test_validate.py`

- [ ] **Step 1: Write the failing test** — `tests/test_validate.py`

```python
import os, textwrap
from tools import validate, model


def _lessons(tmp_path, specs):
    root = tmp_path / "lessons"
    lessons = {}
    for slug, prereqs in specs.items():
        d = root / slug
        os.makedirs(d, exist_ok=True)
        (d / "lesson.yml").write_text(textwrap.dedent(f"""
            slug: {slug}
            title: "{slug}"
            kind: LAB
            prereqs: {prereqs}
        """), encoding="utf-8")
        lessons[slug] = model.load_lesson(str(d))
    return lessons


def _manifest(schedule):
    return model.Manifest(course={}, schedule_unit="weeks", slot_label="Week {n}",
                          target_repo="x/y",
                          schedule=[model.Slot(**s) for s in schedule])


def test_ok_manifest(tmp_path):
    lessons = _lessons(tmp_path, {"hash": [], "macs": ["hash"]})
    m = _manifest([{"slot": 2, "kind": "lesson", "value": "hash"},
                   {"slot": 3, "kind": "lesson", "value": "macs"}])
    assert validate.validate_manifest(m, lessons) == []


def test_unknown_slug(tmp_path):
    lessons = _lessons(tmp_path, {"hash": []})
    m = _manifest([{"slot": 2, "kind": "lesson", "value": "ghost"}])
    errs = validate.validate_manifest(m, lessons)
    assert any("ghost" in e for e in errs)


def test_duplicate_slot(tmp_path):
    lessons = _lessons(tmp_path, {"hash": [], "macs": []})
    m = _manifest([{"slot": 2, "kind": "lesson", "value": "hash"},
                   {"slot": 2, "kind": "lesson", "value": "macs"}])
    assert any("duplicate slot 2" in e for e in validate.validate_manifest(m, lessons))


def test_prereq_after_dependent(tmp_path):
    lessons = _lessons(tmp_path, {"hash": [], "macs": ["hash"]})
    m = _manifest([{"slot": 2, "kind": "lesson", "value": "macs"},
                   {"slot": 3, "kind": "lesson", "value": "hash"}])
    assert any("prereq 'hash'" in e and "macs" in e for e in validate.validate_manifest(m, lessons))


def test_lint_lesson_flags_week_literal(tmp_path):
    d = tmp_path / "lessons" / "hash"
    os.makedirs(d, exist_ok=True)
    (d / "lesson.yml").write_text("slug: hash\ntitle: h\nkind: LAB\n", encoding="utf-8")
    (d / "README.md").write_text("See Week 5 for the recap. Slides: slides/week02.md\n", encoding="utf-8")
    violations = validate.lint_lesson(str(d))
    assert any("Week 5" in v for v in violations) and any("slides/week02.md" in v for v in violations)


def test_lint_lesson_clean(tmp_path):
    d = tmp_path / "lessons" / "hash"
    os.makedirs(d, exist_ok=True)
    (d / "lesson.yml").write_text("slug: hash\ntitle: h\nkind: LAB\n", encoding="utf-8")
    (d / "README.md").write_text("See {{ ref('key-exchange') }}. Slides: {{ slides }}\n", encoding="utf-8")
    assert validate.lint_lesson(str(d)) == []
```

- [ ] **Step 2: Run it, confirm it fails.**

- [ ] **Step 3: Write `tools/validate.py`**

```python
# tools/validate.py — manifest validation + the lesson portability invariant lint.
import os
import re

# A lesson must not hard-code a schedule number for itself or another lesson.
_WEEK_WORD = re.compile(r"\b(?:Week|Day|Session|Lesson)\s+\d+\b")
_SLIDE_PATH = re.compile(r"slides/(?:week|day|session|lesson)\d+\.md")


def validate_manifest(manifest, lessons_by_slug):
    """Return a list of human-readable error strings (empty == valid)."""
    errors = []
    seen_slots = set()
    seen_at = {}                                  # lesson slug -> its slot (in order)
    for s in manifest.schedule:
        if s.slot in seen_slots:
            errors.append(f"duplicate slot {s.slot}")
        seen_slots.add(s.slot)
        if s.kind != "lesson":
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


def lint_lesson(lesson_dir):
    """Return invariant violations (literal schedule refs) across the lesson's .md files."""
    violations = []
    for root, _dirs, files in os.walk(lesson_dir):
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, lesson_dir)
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    for m in _WEEK_WORD.finditer(line):
                        violations.append(f"{rel}:{i}: literal schedule ref '{m.group(0)}' "
                                          f"(use a cross-ref token instead)")
                    for m in _SLIDE_PATH.finditer(line):
                        violations.append(f"{rel}:{i}: hard-coded slide path '{m.group(0)}' "
                                          f"(use {{{{ slides }}}} instead)")
    return violations
```

- [ ] **Step 4: Run tests, confirm pass.**

- [ ] **Step 5: Commit**

```bash
git add tools/validate.py tests/test_validate.py
git commit -m "validate: manifest checks (unknown slug, dup slot, prereq order) + lesson lint"
```

---

### Task 4: The renderer (`tools/render.py`)

Emits one course's tree from its manifest. `slides.md` → `<out>/slides/<slotfile>.md`; every other file →
`<out>/labs/<labdir>/<relpath>`; `.md` files are token-rendered, everything else copied byte-for-byte.

**Files:**
- Create: `tools/render.py`, `tests/test_render.py`

- [ ] **Step 1: Write the failing test** — `tests/test_render.py`

```python
import os, textwrap
from tools import render, model


def _mk_lesson(root, slug, files):
    d = os.path.join(root, "lessons", slug)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "lesson.yml"), "w", encoding="utf-8") as f:
        f.write(f"slug: {slug}\ntitle: {slug}\nkind: LAB\n")
    for rel, content in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)


def _mk_manifest(root, schedule):
    p = os.path.join(root, "courses", "sc.yml")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lines = "\n".join(f"  - {{slot: {s}, lesson: {sl}}}" for s, sl in schedule)
    with open(p, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(f"""\
            course: {{name: SC, brand: "KOSEN·KMITL", flag_salt_env: SC_FLAG_SALT}}
            schedule_unit: weeks
            slot_label: "Week {{n}}"
            target_repo: "x/sc"
            schedule:
            """) + lines + "\n")
    return p


def test_render_lab_and_crossref(tmp_path):
    root = str(tmp_path)
    _mk_lesson(root, "hash", {
        "README.md": "# Hash\nNext up: {{ next }}. Slides: {{ slides }}\n",
        "docker-compose.yml": "services: {app: {image: python:3.12}}\n",
        "exploit.py": "print('week5')\n",   # NOT .md → must stay byte-identical
    })
    _mk_lesson(root, "macs", {"README.md": "# MACs\n"})
    _mk_manifest(root, [(2, "hash"), (3, "macs")])
    out = os.path.join(root, "out")
    render.render_course(os.path.join(root, "courses", "sc.yml"),
                         lessons_root=os.path.join(root, "lessons"), out_dir=out)

    readme = open(os.path.join(out, "labs", "week02-hash", "README.md"), encoding="utf-8").read()
    assert "Next up: Week 3." in readme and "Slides: slides/week02.md" in readme
    # non-.md copied verbatim (the literal 'week5' string must survive untouched)
    assert open(os.path.join(out, "labs", "week02-hash", "exploit.py"), encoding="utf-8").read() == "print('week5')\n"
    assert os.path.isfile(os.path.join(out, "labs", "week02-hash", "docker-compose.yml"))


def test_render_slides_go_to_slides_dir(tmp_path):
    root = str(tmp_path)
    _mk_lesson(root, "hash", {"slides.md": "# {{ slot_label }} slides\n"})
    _mk_manifest(root, [(2, "hash")])
    out = os.path.join(root, "out")
    render.render_course(os.path.join(root, "courses", "sc.yml"),
                         lessons_root=os.path.join(root, "lessons"), out_dir=out)
    assert not os.path.exists(os.path.join(out, "labs", "week02-hash", "slides.md"))
    slides = open(os.path.join(out, "slides", "week02.md"), encoding="utf-8").read()
    assert "# Week 2 slides" in slides


def test_render_is_idempotent(tmp_path):
    root = str(tmp_path)
    _mk_lesson(root, "hash", {"README.md": "# Hash {{ slot_label }}\n"})
    _mk_manifest(root, [(2, "hash")])
    out = os.path.join(root, "out")
    mpath = os.path.join(root, "courses", "sc.yml")
    lr = os.path.join(root, "lessons")
    render.render_course(mpath, lessons_root=lr, out_dir=out)
    first = open(os.path.join(out, "labs", "week02-hash", "README.md"), "rb").read()
    render.render_course(mpath, lessons_root=lr, out_dir=out)
    assert open(os.path.join(out, "labs", "week02-hash", "README.md"), "rb").read() == first


def test_render_rejects_invalid_manifest(tmp_path):
    root = str(tmp_path)
    _mk_lesson(root, "hash", {"README.md": "# Hash\n"})
    _mk_manifest(root, [(2, "ghost")])          # slug not present
    out = os.path.join(root, "out")
    try:
        render.render_course(os.path.join(root, "courses", "sc.yml"),
                             lessons_root=os.path.join(root, "lessons"), out_dir=out)
        assert False, "expected a validation error"
    except render.RenderError as e:
        assert "ghost" in str(e)
```

- [ ] **Step 2: Run it, confirm it fails.**

- [ ] **Step 3: Write `tools/render.py`**

```python
# tools/render.py — render one course's student-facing tree from its manifest.
import argparse
import os
import shutil

from tools import crossref, model, validate


class RenderError(Exception):
    pass


def _write(path, data, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding=None if "b" in mode else "utf-8") as f:
        f.write(data)


def _render_lesson(manifest, lesson, out_dir):
    unit, n = manifest.schedule_unit, next(
        s.slot for s in manifest.schedule if s.kind == "lesson" and s.value == lesson.slug)
    ctx = crossref.context(manifest, lesson.slug)
    lab_out = os.path.join(out_dir, "labs", crossref.labdir(unit, n, lesson.slug))
    for root, _dirs, files in os.walk(lesson.dir):
        for name in sorted(files):
            if name == "lesson.yml":
                continue
            src = os.path.join(root, name)
            rel = os.path.relpath(src, lesson.dir)
            if rel == "slides.md":
                dst = os.path.join(out_dir, "slides", f"{crossref.slotfile(unit, n)}.md")
                _write(dst, crossref.render(open(src, encoding="utf-8").read(), ctx))
                continue
            dst = os.path.join(lab_out, rel)
            if name.endswith(".md"):
                _write(dst, crossref.render(open(src, encoding="utf-8").read(), ctx))
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)                 # byte-for-byte, preserves mode


def render_course(manifest_path, lessons_root, out_dir):
    manifest = model.load_manifest(manifest_path)
    lessons = model.load_lessons(lessons_root)
    errs = validate.validate_manifest(manifest, lessons)
    if errs:
        raise RenderError("manifest invalid:\n  " + "\n  ".join(errs))
    for slug in manifest.lesson_slugs():
        _render_lesson(manifest, lessons[slug], out_dir)
    return out_dir


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render a course tree from its manifest.")
    ap.add_argument("manifest")
    ap.add_argument("--lessons", default="lessons")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    render_course(args.manifest, args.lessons, args.out)
    print(f"rendered {args.manifest} -> {args.out}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests, confirm pass** — `.venv/bin/python -m pytest tests/test_render.py -q`.

- [ ] **Step 5: Commit**

```bash
git add tools/render.py tests/test_render.py
git commit -m "render: manifest -> course tree (slides split, .md tokenized, code verbatim, idempotent)"
```

---

### Task 5: Import the `hash` pilot lesson + partial manifest

Bring one real lesson into the library and tokenize its schedule refs.

**Files:**
- Create: `lessons/hash/lesson.yml` + copied content, `courses/security-cryptography.yml`

- [ ] **Step 1: Copy the source lesson content.** From the sibling repo
  `../KOSEN69 - security-cryptography/labs/week02-hash/`, copy every file into `lessons/hash/` (flat).
  Run:
```bash
SRC="../KOSEN69 - security-cryptography/labs/week02-hash"
mkdir -p lessons/hash && cp -R "$SRC"/. lessons/hash/
ls lessons/hash
```

- [ ] **Step 2: Write `lessons/hash/lesson.yml`** — read the copied `README.md` to fill title/kind/flag_key
  accurately (grep for `FLAG_` in the copied lab to get the real flag key):
```yaml
slug: hash
title: "<real title from the source README's H1>"
kind: LAB
duration_min: 180
tags: [crypto, hashing, integrity]
cwe: [CWE-345]
prereqs: []
flag_key: "<the FLAG_<KEY> the lab actually mints — grep the lab .py/compose>"
```

- [ ] **Step 3: Tokenize schedule refs.** Run the linter to find every literal schedule ref, then replace
  each with the correct token (`{{ ref('<slug>') }}`, `{{ prev }}`, `{{ slides }}`, etc.):
```bash
.venv/bin/python -c "from tools import validate; print('\n'.join(validate.lint_lesson('lessons/hash')) or 'clean')"
```
  **week02-hash is self-contained** — a source grep shows its only schedule refs are to *itself*:
  `# Week 2 — …` and `**Week 2**` → `{{ slot_label }}`; `Slides: slides/week02.md` → `Slides: {{ slides }}`;
  `cd labs/week02-hash` → `cd {{ labpath }}`. There are **no references to other lessons**, so the pilot
  needs only the `hash` lesson and byte-parity is fully achievable. Edit the flagged `.md` files until the
  linter prints `clean`. (General rule for later lessons: "last week's recap" → `{{ prev }}`; a named
  other-week → `{{ ref('<slug>') }}` with that slug scheduled in the manifest.)

- [ ] **Step 4: Write `courses/security-cryptography.yml`** (partial — just the pilot lesson + the two
  non-lesson slots that surround it in the real course, to exercise calendar entries):
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
  - {slot: 2, lesson: hash}
  - {slot: 7, review: "Review / midterm prep"}
```

- [ ] **Step 5: Sanity render + lint** — confirm the machinery runs on the real lesson:
```bash
.venv/bin/python -m tools.render courses/security-cryptography.yml --out _render/sc
ls _render/sc/labs
```
  (`_render/` is git-ignored.) Expect `week02-hash/` with the README/worksheet token-resolved and the lab
  code verbatim.

- [ ] **Step 6: Commit**

```bash
git add lessons/hash courses/security-cryptography.yml
git commit -m "pilot: import security-cryptography week02-hash as lessons/hash + partial manifest"
```

---

### Task 6: Parity + link-integrity verification

Prove the rendered output reproduces the current published lesson, and no token leaked through.

**Files:**
- Create: `tests/test_parity.py`
- Modify: the spec's §4 (flat-lesson refinement note)

- [ ] **Step 1: Write the parity + integrity test** — `tests/test_parity.py`

```python
import os, subprocess, sys, pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_REPO = ROOT.parent / "KOSEN69 - security-cryptography"
SRC_LAB = SRC_REPO / "labs" / "week02-hash"


pytestmark = pytest.mark.skipif(not SRC_LAB.is_dir(),
                                reason="source security-cryptography repo not present")


def _render(tmp):
    from tools import render
    render.render_course(str(ROOT / "courses" / "security-cryptography.yml"),
                         lessons_root=str(ROOT / "lessons"), out_dir=str(tmp))
    return tmp / "labs" / "week02-hash"


def test_no_unresolved_tokens(tmp_path):
    out = _render(tmp_path)
    for md in out.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        assert "{{" not in text and "{%" not in text, f"unresolved token in {md}"


def test_lab_code_is_byte_identical_to_source(tmp_path):
    out = _render(tmp_path)
    # every NON-markdown file in the source lab must render byte-for-byte identical
    for src in SRC_LAB.rglob("*"):
        if src.is_dir() or src.suffix == ".md":
            continue
        rel = src.relative_to(SRC_LAB)
        dst = out / rel
        assert dst.is_file(), f"missing rendered file {rel}"
        assert dst.read_bytes() == src.read_bytes(), f"lab code drifted: {rel}"


def test_rendered_markdown_matches_source_after_detokenize(tmp_path):
    """The rendered .md (tokens resolved for Week 2) must equal the current published .md."""
    out = _render(tmp_path)
    for src in SRC_LAB.glob("*.md"):
        dst = out / src.name
        assert dst.is_file(), f"missing rendered {src.name}"
        assert dst.read_text(encoding="utf-8") == src.read_text(encoding="utf-8"), \
            f"rendered {src.name} != current published content"
```

- [ ] **Step 2: Run it.** If `test_rendered_markdown_matches_source_after_detokenize` fails, the diff shows
  where tokenization changed the text — reconcile by fixing the token (Task 5 step 3) until the rendered
  `.md` equals the current published `.md` exactly. This is the parity gate. Non-`.md` should already match.

- [ ] **Step 3: Run the FULL suite** — `.venv/bin/python -m pytest tests/ -q`. All green.

- [ ] **Step 4: Update the spec** — in
  `docs/superpowers/specs/2026-07-22-cross-course-lesson-library-design.md` §4, replace the illustrative
  `lab/` subdir with the flat-lesson layout this plan implemented (content files at `lessons/<slug>/` root,
  `slides.md` special-cased on render), so spec and code agree.

- [ ] **Step 5: Commit**

```bash
git add tests/test_parity.py docs/superpowers/specs/2026-07-22-cross-course-lesson-library-design.md
git commit -m "parity: rendered hash lesson matches current published content byte-for-byte; align spec"
```

---

## Verification (before finishing the branch)

1. `.venv/bin/python -m pytest tests/ -q` — all green (model, crossref, validate, render, parity).
2. `.venv/bin/python -m tools.render courses/security-cryptography.yml --out _render/sc` runs clean and
   `_render/sc/labs/week02-hash/` contains the token-resolved docs + verbatim lab code.
3. `.venv/bin/python -c "from tools import validate; print(validate.lint_lesson('lessons/hash'))"` → `[]`
   (the imported lesson satisfies the portability invariant).
4. Manual: `cd _render/sc/labs/week02-hash && docker compose up` still starts the lab (copy-verbatim means
   behaviour is unchanged from the source) — spot check, then tear down.

## Self-review

- **Spec coverage:** lesson unit + `lesson.yml` (Task 1), manifest schema + parsing (Task 1), cross-ref
  resolution (Task 2, spec §6), validation + portability invariant (Task 3, spec §4/§5), renderer pipeline
  (Task 4, spec §8), a real imported lesson + manifest (Task 5), and the parity gate + idempotence + link
  integrity (Task 6, spec §11). Flag tooling (spec §7) and full-course import (spec §10 phase 4+) are
  explicitly deferred to follow-on plans — this plan produces a working, tested renderer proven on one real
  lesson.
- **Type/name consistency:** `slotfile`/`labdir`/`context`/`render` in `crossref.py` are the exact names
  `render.py` imports; `validate_manifest(manifest, lessons_by_slug)` and `lint_lesson(dir)` match their
  callers; `Manifest.lesson_slugs()` and `Slot(slot, kind, value)` are used identically in model, validate,
  render, and their tests; `RenderError`/`CrossRefError` are the exception types the tests assert on.
- **No placeholders:** every code step contains complete, runnable code. The only intentionally-templated
  values are in Task 5 (`<real title>`, `<flag key>`) which the executor fills from the actual source
  files it copies — called out explicitly with the grep to obtain them.
