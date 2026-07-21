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
