import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_REPO = ROOT.parent / "KOSEN69 - security-cryptography"
SRC_LAB = SRC_REPO / "labs" / "week02-hash"


pytestmark = pytest.mark.skipif(not SRC_LAB.is_dir(),
                                reason="source security-cryptography repo not present")


def _render(tmp):
    from tools import render
    render.render_course(str(ROOT / "courses" / "security-cryptography.yml"),
                         lessons_root=str(ROOT / "lessons"), out_dir=str(tmp / "out"))
    return tmp / "out" / "labs" / "week02-hash"


def test_no_unresolved_tokens(tmp_path):
    out = _render(tmp_path)
    for md in out.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        assert "{{" not in text and "{%" not in text, f"unresolved token in {md}"


def test_lab_code_is_byte_identical_to_source(tmp_path):
    out = _render(tmp_path)
    for src in SRC_LAB.rglob("*"):
        if src.is_dir() or src.suffix == ".md":
            continue
        rel = src.relative_to(SRC_LAB)
        dst = out / rel
        assert dst.is_file(), f"missing rendered file {rel}"
        assert dst.read_bytes() == src.read_bytes(), f"lab code drifted: {rel}"


def test_rendered_markdown_matches_source(tmp_path):
    """Rendered .md (tokens resolved for Week 2) must equal the current published .md."""
    out = _render(tmp_path)
    for src in SRC_LAB.glob("*.md"):
        dst = out / src.name
        assert dst.is_file(), f"missing rendered {src.name}"
        assert dst.read_text(encoding="utf-8") == src.read_text(encoding="utf-8"), \
            f"rendered {src.name} != current published content"
