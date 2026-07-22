import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_REPO = ROOT.parent / "KOSEN69 - software-security"
SRC_LABS = SRC_REPO / "labs"

LESSON_DIRS = {
    "threat-modeling": "week01-threat-modeling", "sdlc-tooling": "week02-sdlc-tooling",
    "cryptography": "week03-cryptography", "injection": "week04-injection",
    "xss-client-side": "week05-xss-client-side", "authn-authz": "week06-authn-authz",
    "api-security": "week10-api-security", "memory-safety-exploitation": "week11-memory-safety-exploitation",
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
    # No lesson in this course has a slides.md, so no out/slides/ output is expected here; not asserted.


def test_mfu_content_matches_library_source_verbatim(tmp_path):
    """Re-scheduling changes only schedule-derived tokens, never the substance: normalize the
    slides-path token (`{{ slides }}` resolves via slotfile(), e.g. `slides/week01.md` vs
    `slides/session1.md` — a legitimate, structurally-forced difference per schedule_unit; see
    crossref.slotfile()/context()) and strip the schedule label line (`{{ slot_label }}`, e.g.
    "Week 1" vs "Session 1"); the rest must be identical between the 19-slot render and the MFU
    render of the SAME lesson."""
    from tools import render
    out19 = tmp_path / "out19"
    render.render_course(str(ROOT / "courses" / "software-security.yml"),
                         lessons_root=str(ROOT / "lessons"), out_dir=str(out19))
    out_mfu = _render_mfu(tmp_path)
    a = (out19 / "labs" / "week01-threat-modeling" / "README.md").read_text(encoding="utf-8")
    b = (out_mfu / "labs" / "session1-threat-modeling" / "README.md").read_text(encoding="utf-8")
    slides_re = re.compile(r"slides/\w+\.md")
    a = slides_re.sub("slides/<SLOT>.md", a)
    b = slides_re.sub("slides/<SLOT>.md", b)
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


def test_mfu_covers_midterm_and_final_exam():
    """Coverage means more than lessons: the midterm and final exam are graded assessment events
    that must survive the compression too, not just be implied by 'the lessons are all there.'
    Checked generally via validate.missing_phases() against the canonical manifest's phase-tagged
    exam slots — if a future edit ever dropped Session 4 or Session 7 from the MFU schedule, this
    is what would catch it."""
    from tools import model, validate
    canonical = model.load_manifest(str(ROOT / "courses" / "software-security.yml"))
    mfu = model.load_manifest(str(MFU_MANIFEST))
    assert validate.missing_phases(canonical, mfu) == set()


def test_mfu_capstone_deliberately_absent():
    """week16-capstone is explicitly self-study between sessions in the source syllabus — it must
    never be scheduled as a lesson in the MFU manifest."""
    from tools import model
    m = model.load_manifest(str(MFU_MANIFEST))
    assert "capstone" not in m.lesson_slugs()
