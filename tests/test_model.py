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
