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
        flag_keys: [hash]
    """)
    lsn = model.load_lesson(str(d))
    assert lsn.slug == "hash" and lsn.kind == "LAB" and lsn.flag_keys == ["hash"]
    assert lsn.dir == str(d)


def test_load_lessons_rejects_dir_name_slug_mismatch(tmp_path):
    d = tmp_path / "lessons" / "hash-v2"
    _write(str(d / "lesson.yml"), """
        slug: hash
        title: "Hashing & Cookie Forgery"
        kind: LAB
    """)
    try:
        model.load_lessons(str(tmp_path / "lessons"))
        assert False, "expected a ValueError for dir-name/slug mismatch"
    except ValueError as e:
        assert "hash-v2" in str(e) and "hash" in str(e)


def test_load_lessons_accepts_matching_dir_name(tmp_path):
    d = tmp_path / "lessons" / "hash"
    _write(str(d / "lesson.yml"), """
        slug: hash
        title: "Hashing & Cookie Forgery"
        kind: LAB
    """)
    lessons = model.load_lessons(str(tmp_path / "lessons"))
    assert lessons["hash"].slug == "hash"


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
