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
