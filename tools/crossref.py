# tools/crossref.py — resolve slug-based cross-reference tokens against a course's schedule.
import jinja2


class CrossRefError(Exception):
    pass


def slotfile(unit, n):
    if unit == "weeks":
        return f"week{n:02d}"
    if unit == "days":
        return f"day{n}"
    if unit == "sessions":
        return f"session{n}"
    if unit == "lessons":
        return f"lesson{n:02d}"
    raise CrossRefError(f"unknown schedule_unit '{unit}'")


def labdir(unit, n, slug):
    return f"{slotfile(unit, n)}-{slug}"


def context(manifest, current_slug):
    """Build the Jinja render context (values + callables) for one lesson in one course."""
    unit = manifest.schedule_unit
    label_tmpl = manifest.slot_label
    slug_to_slot = {s.value: s.slot for s in manifest.schedule if s.kind == "lesson"}
    ordered = [s.value for s in manifest.schedule if s.kind == "lesson"]

    if current_slug not in slug_to_slot:
        raise CrossRefError(f"lesson '{current_slug}' is not scheduled in this course")
    here = ordered.index(current_slug)

    def label(slug):
        if slug not in slug_to_slot:
            raise CrossRefError(f"ref('{slug}') — not scheduled in this course")
        return label_tmpl.format(n=slug_to_slot[slug])

    def ref(slug, link=False):
        if link:
            if slug not in slug_to_slot:
                raise CrossRefError(f"ref('{slug}', link=True) — not scheduled in this course")
            return f"../{labdir(unit, slug_to_slot[slug], slug)}/"
        return label(slug)

    my_slot = slug_to_slot[current_slug]
    return {
        "ref": ref,
        "slides": f"slides/{slotfile(unit, my_slot)}.md",          # this lesson's slide path
        "labpath": f"labs/{labdir(unit, my_slot, current_slug)}",  # this lesson's lab dir (for `cd labs/…`)
        "slot": my_slot,
        "slot_label": label_tmpl.format(n=my_slot),
        "prev": label(ordered[here - 1]) if here > 0 else "",
        "next": label(ordered[here + 1]) if here < len(ordered) - 1 else "",
        "brand": manifest.course.get("brand", ""),
    }


_ENV = jinja2.Environment(undefined=jinja2.StrictUndefined, autoescape=False,
                          keep_trailing_newline=True)


def render(text, ctx):
    try:
        return _ENV.from_string(text).render(**ctx)
    except jinja2.UndefinedError as e:
        raise CrossRefError(str(e)) from e
