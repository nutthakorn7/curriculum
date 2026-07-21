# tools/model.py — data model for lessons and course manifests.
import os
from dataclasses import dataclass, field

import yaml

# The recognised non-lesson slot kinds (a slot is either a lesson or one of these calendar entries).
NON_LESSON_KINDS = ("exam", "review", "project", "holiday", "break")


@dataclass
class Lesson:
    slug: str
    title: str
    kind: str                      # LAB | HYBRID | CONCEPTUAL
    duration_min: int = 0
    tags: list = field(default_factory=list)
    cwe: list = field(default_factory=list)
    prereqs: list = field(default_factory=list)
    flag_key: str | None = None
    dir: str = ""                  # filesystem path to lessons/<slug>/


def load_lesson(lesson_dir):
    with open(os.path.join(lesson_dir, "lesson.yml"), encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Lesson(dir=lesson_dir, **data)


def load_lessons(lessons_root):
    """Return {slug: Lesson} for every lessons/<slug>/lesson.yml under lessons_root."""
    out = {}
    if not os.path.isdir(lessons_root):
        return out
    for name in sorted(os.listdir(lessons_root)):
        d = os.path.join(lessons_root, name)
        if os.path.isfile(os.path.join(d, "lesson.yml")):
            lsn = load_lesson(d)
            if name != lsn.slug:
                raise ValueError(
                    f"lesson directory '{name}' declares slug '{lsn.slug}'; "
                    f"directory name must equal the slug (rename the directory to '{lsn.slug}')")
            if lsn.slug in out:
                raise ValueError(f"duplicate lesson slug '{lsn.slug}'")
            out[lsn.slug] = lsn
    return out


@dataclass
class Slot:
    slot: int
    kind: str                      # "lesson" or a NON_LESSON_KINDS value
    value: str                     # lesson slug, or the calendar-entry title


@dataclass
class Manifest:
    course: dict
    schedule_unit: str
    slot_label: str
    target_repo: str
    schedule: list                 # list[Slot]
    path: str = ""

    def lesson_slugs(self):
        return [s.value for s in self.schedule if s.kind == "lesson"]


def _parse_slot(entry):
    e = dict(entry)
    slot = e.pop("slot")
    # exactly one remaining key names the kind; lesson is the common case
    if not e:
        raise ValueError(f"slot {slot} has no kind (expected 'lesson' or one of {NON_LESSON_KINDS})")
    if len(e) != 1:
        raise ValueError(f"slot {slot} has multiple kinds {list(e)}; a slot carries exactly one")
    kind, value = next(iter(e.items()))
    if kind != "lesson" and kind not in NON_LESSON_KINDS:
        raise ValueError(f"slot {slot}: unknown kind '{kind}'")
    return Slot(slot=slot, kind=kind, value=value)


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f) or {}
    return Manifest(
        course=d["course"],
        schedule_unit=d["schedule_unit"],
        slot_label=d["slot_label"],
        target_repo=d["target_repo"],
        schedule=[_parse_slot(x) for x in d["schedule"]],
        path=path,
    )
