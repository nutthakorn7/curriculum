import os, textwrap
from tools import render, model


def _mk_lesson(root, slug, files):
    d = os.path.join(root, "lessons", slug)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "lesson.yml"), "w", encoding="utf-8") as f:
        f.write(f"slug: {slug}\ntitle: {slug}\nkind: LAB\n")
    for rel, content in files.items():
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)


def _mk_manifest(root, schedule):
    p = os.path.join(root, "courses", "sc.yml")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    lines = "\n".join(f"  - {{slot: {s}, lesson: {sl}}}" for s, sl in schedule)
    with open(p, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(f"""\
            course: {{name: SC, brand: "KOSEN·KMITL", flag_salt_env: SC_FLAG_SALT}}
            schedule_unit: weeks
            slot_label: "Week {{n}}"
            target_repo: "x/sc"
            schedule:
            """) + lines + "\n")
    return p


def test_render_lab_and_crossref(tmp_path):
    root = str(tmp_path)
    _mk_lesson(root, "hash", {
        "README.md": "# Hash\nNext up: {{ next }}. Slides: {{ slides }}\n",
        "docker-compose.yml": "services: {app: {image: python:3.12}}\n",
        "exploit.py": "print('week5')\n",   # NOT .md → must stay byte-identical
    })
    _mk_lesson(root, "macs", {"README.md": "# MACs\n"})
    _mk_manifest(root, [(2, "hash"), (3, "macs")])
    out = os.path.join(root, "out")
    render.render_course(os.path.join(root, "courses", "sc.yml"),
                         lessons_root=os.path.join(root, "lessons"), out_dir=out)

    readme = open(os.path.join(out, "labs", "week02-hash", "README.md"), encoding="utf-8").read()
    assert "Next up: Week 3." in readme and "Slides: slides/week02.md" in readme
    # non-.md copied verbatim (the literal 'week5' string must survive untouched)
    assert open(os.path.join(out, "labs", "week02-hash", "exploit.py"), encoding="utf-8").read() == "print('week5')\n"
    assert os.path.isfile(os.path.join(out, "labs", "week02-hash", "docker-compose.yml"))


def test_render_slides_go_to_slides_dir(tmp_path):
    root = str(tmp_path)
    _mk_lesson(root, "hash", {"slides.md": "# {{ slot_label }} slides\n"})
    _mk_manifest(root, [(2, "hash")])
    out = os.path.join(root, "out")
    render.render_course(os.path.join(root, "courses", "sc.yml"),
                         lessons_root=os.path.join(root, "lessons"), out_dir=out)
    assert not os.path.exists(os.path.join(out, "labs", "week02-hash", "slides.md"))
    slides = open(os.path.join(out, "slides", "week02.md"), encoding="utf-8").read()
    assert "# Week 2 slides" in slides


def test_render_is_idempotent(tmp_path):
    root = str(tmp_path)
    _mk_lesson(root, "hash", {"README.md": "# Hash {{ slot_label }}\n"})
    _mk_manifest(root, [(2, "hash")])
    out = os.path.join(root, "out")
    mpath = os.path.join(root, "courses", "sc.yml")
    lr = os.path.join(root, "lessons")
    render.render_course(mpath, lessons_root=lr, out_dir=out)
    first = open(os.path.join(out, "labs", "week02-hash", "README.md"), "rb").read()
    render.render_course(mpath, lessons_root=lr, out_dir=out)
    assert open(os.path.join(out, "labs", "week02-hash", "README.md"), "rb").read() == first


def test_render_rejects_invalid_manifest(tmp_path):
    root = str(tmp_path)
    _mk_lesson(root, "hash", {"README.md": "# Hash\n"})
    _mk_manifest(root, [(2, "ghost")])          # slug not present
    out = os.path.join(root, "out")
    try:
        render.render_course(os.path.join(root, "courses", "sc.yml"),
                             lessons_root=os.path.join(root, "lessons"), out_dir=out)
        assert False, "expected a validation error"
    except render.RenderError as e:
        assert "ghost" in str(e)
