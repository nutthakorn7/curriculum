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
