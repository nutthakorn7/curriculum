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


def test_duplicate_lesson_slots_are_allowed(tmp_path):
    lessons = _lessons(tmp_path, {"hash": [], "macs": []})
    m = _manifest([{"slot": 2, "kind": "lesson", "value": "hash"},
                   {"slot": 2, "kind": "lesson", "value": "macs"}])
    assert validate.validate_manifest(m, lessons) == []


def test_duplicate_lesson_slug(tmp_path):
    lessons = _lessons(tmp_path, {"hash": []})
    m = _manifest([{"slot": 2, "kind": "lesson", "value": "hash"},
                   {"slot": 5, "kind": "lesson", "value": "hash"}])
    errs = validate.validate_manifest(m, lessons)
    assert any("more than once" in e and "hash" in e for e in errs)


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


def test_lint_lesson_flags_case_insensitive_and_plural_range(tmp_path):
    d = tmp_path / "lessons" / "hash"
    os.makedirs(d, exist_ok=True)
    (d / "lesson.yml").write_text("slug: hash\ntitle: h\nkind: LAB\n", encoding="utf-8")
    (d / "README.md").write_text(
        "see week 5 for background. Weeks 5-6 cover MACs. Slides/week03.md has the deck.\n",
        encoding="utf-8")
    violations = validate.lint_lesson(str(d))
    assert any("week 5" in v for v in violations)
    assert any("Weeks 5-6" in v for v in violations)
    assert any("Slides/week03.md" in v for v in violations)


def test_lint_lesson_clean(tmp_path):
    d = tmp_path / "lessons" / "hash"
    os.makedirs(d, exist_ok=True)
    (d / "lesson.yml").write_text("slug: hash\ntitle: h\nkind: LAB\n", encoding="utf-8")
    (d / "README.md").write_text("See {{ ref('key-exchange') }}. Slides: {{ slides }}\n", encoding="utf-8")
    assert validate.lint_lesson(str(d)) == []


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
    compressed = _manifest([{"slot": 1, "kind": "lesson", "value": "sdlc-tooling"},
                            {"slot": 1, "kind": "lesson", "value": "threat-modeling"}])
    assert validate.missing_lessons(canonical, compressed) == set()


def test_missing_lessons_ignores_untagged_non_lesson_slots():
    canonical = _manifest([{"slot": 1, "kind": "lesson", "value": "threat-modeling"},
                           {"slot": 2, "kind": "review", "value": "Review week"}])
    compressed = _manifest([{"slot": 1, "kind": "lesson", "value": "threat-modeling"},
                            {"slot": 2, "kind": "exam", "value": "Combined review+exam session"}])
    assert validate.missing_lessons(canonical, compressed) == set()


def test_missing_phases_finds_gap(tmp_path):
    canonical = _manifest([
        {"slot": 8, "kind": "exam", "value": "Midterm written", "phase": "midterm"},
        {"slot": 9, "kind": "exam", "value": "Midterm practical", "phase": "midterm"},
        {"slot": 18, "kind": "exam", "value": "Final written", "phase": "final"},
    ])
    compressed = _manifest([{"slot": 4, "kind": "exam", "value": "Midterm combined", "phase": "midterm"}])
    assert validate.missing_phases(canonical, compressed) == {"final"}


def test_missing_phases_empty_when_merged_but_present(tmp_path):
    canonical = _manifest([
        {"slot": 8, "kind": "exam", "value": "Midterm written", "phase": "midterm"},
        {"slot": 9, "kind": "exam", "value": "Midterm practical", "phase": "midterm"},
    ])
    compressed = _manifest([{"slot": 4, "kind": "exam", "value": "Midterm: written + practical combined",
                             "phase": "midterm"}])
    assert validate.missing_phases(canonical, compressed) == set()


def test_missing_phases_ignores_untagged_exams():
    canonical = _manifest([{"slot": 8, "kind": "exam", "value": "Pop quiz", "phase": None}])
    compressed = _manifest([])
    assert validate.missing_phases(canonical, compressed) == set()
