# tools/render.py — render one course's student-facing tree from its manifest.
import argparse
import os
import shutil
from pathlib import PurePosixPath

from tools import crossref, model, validate


class RenderError(Exception):
    pass


def _write(path, data, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding=None if "b" in mode else "utf-8") as f:
        f.write(data)


def _render_md(src, ctx, rel):
    try:
        return crossref.render(open(src, encoding="utf-8").read(), ctx)
    except crossref.CrossRefError as e:
        raise crossref.CrossRefError(f"{rel}: {e}") from e


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
            if os.path.islink(src):
                # A symlink here would get its TARGET's content silently copied
                # into the published output — shutil.copy2 and open() both
                # follow symlinks by default. No lesson has a legitimate reason
                # to contain one, so refuse outright rather than try to confine
                # the resolved path.
                raise RenderError(
                    f"refusing to render a symlink: {os.path.relpath(src, lesson.dir)} "
                    f"(lessons must be plain files)")
            rel = os.path.relpath(src, lesson.dir)
            if rel == "slides.md":
                dst = os.path.join(out_dir, "slides", f"{crossref.slotfile(unit, n)}.md")
                _write(dst, _render_md(src, ctx, rel))
                continue
            dst = os.path.join(lab_out, rel)
            if name.endswith(".md"):
                _write(dst, _render_md(src, ctx, rel))
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)                 # byte-for-byte, preserves mode


def _safe_relative(path):
    if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path:
        raise RenderError(f"invalid content overlay path: {path!r}")
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise RenderError(f"invalid content overlay path: {path!r}")
    return PurePosixPath(path)


def _apply_content_overlay(manifest, staging):
    for raw in manifest.content_remove:
        rel = _safe_relative(raw)
        target = os.path.join(staging, *rel.parts)
        if os.path.isdir(target):
            raise RenderError(f"content_remove names a directory: {raw}")
        if os.path.exists(target):
            os.remove(target)

    if not manifest.content_overlay:
        return
    rel = _safe_relative(manifest.content_overlay)
    repo_root = os.path.dirname(os.path.dirname(os.path.realpath(manifest.path)))
    overlay = os.path.join(repo_root, *rel.parts)
    if os.path.islink(overlay) or not os.path.isdir(overlay):
        raise RenderError(f"content overlay missing or symlinked: {overlay}")
    if os.path.commonpath((repo_root, os.path.realpath(overlay))) != repo_root:
        raise RenderError(f"content overlay escapes repository: {overlay}")
    for root, dirs, files in os.walk(overlay):
        if any(os.path.islink(os.path.join(root, name)) for name in dirs + files):
            raise RenderError(f"content overlay contains a symlink: {root}")
        for name in files:
            src = os.path.join(root, name)
            rel = os.path.relpath(src, overlay)
            dst = os.path.join(staging, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


def render_course(manifest_path, lessons_root, out_dir):
    manifest = model.load_manifest(manifest_path)
    lessons = model.load_lessons(lessons_root)
    errs = validate.validate_manifest(manifest, lessons)
    if errs:
        raise RenderError("manifest invalid:\n  " + "\n  ".join(errs))
    # Never clobber a real repo: render belongs in a dedicated staging dir. Syncing the staged tree
    # into a course repo (deleting the repo's own orphans) is a separate, later step.
    if os.path.isdir(os.path.join(out_dir, ".git")):
        raise RenderError(f"refusing to overwrite a git working tree at {out_dir}; "
                          f"render to a dedicated staging dir instead")
    # Render into a fresh staging dir; swap into place only on full success so a re-render is
    # clean-slate (no stale orphans) and a mid-render error leaves the previous output intact.
    staging = out_dir.rstrip("/") + ".tmp-render"
    if os.path.isdir(staging):
        shutil.rmtree(staging)
    os.makedirs(staging, exist_ok=True)
    try:
        for slug in manifest.lesson_slugs():
            _render_lesson(manifest, lessons[slug], staging)
        _apply_content_overlay(manifest, staging)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.replace(staging, out_dir)      # atomic within the same filesystem
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
