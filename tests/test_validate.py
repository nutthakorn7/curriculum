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
