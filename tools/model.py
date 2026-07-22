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
    flag_keys: list = field(default_factory=list)
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
    phase: str | None = None       # optional; groups exam slots into a required assessment period


@dataclass
class Manifest:
    course: dict
    schedule_unit: str
    slot_label: str
    target_repo: str
    schedule: list                 # list[Slot]
    extra_challenge_keys: list = field(default_factory=list)  # non-lesson flag keys (capstones,
                                                                # static/manually-graded CTFd-only
                                                                # challenges with no attributable lab)
    path: str = ""

    def lesson_slugs(self):
        return [s.value for s in self.schedule if s.kind == "lesson"]


def _parse_slot(entry):
    e = dict(entry)
    slot = e.pop("slot")
    phase = e.pop("phase", None)
    # exactly one remaining key names the kind; lesson is the common case
    if not e:
        raise ValueError(f"slot {slot} has no kind (expected 'lesson' or one of {NON_LESSON_KINDS})")
    if len(e) != 1:
        raise ValueError(f"slot {slot} has multiple kinds {list(e)}; a slot carries exactly one")
    kind, value = next(iter(e.items()))
    if kind != "lesson" and kind not in NON_LESSON_KINDS:
        raise ValueError(f"slot {slot}: unknown kind '{kind}'")
    return Slot(slot=slot, kind=kind, value=value, phase=phase)


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f) or {}
    return Manifest(
        course=d["course"],
        schedule_unit=d["schedule_unit"],
        slot_label=d["slot_label"],
        target_repo=d["target_repo"],
        schedule=[_parse_slot(x) for x in d["schedule"]],
        extra_challenge_keys=d.get("extra_challenge_keys", []),
        path=path,
    )


def challenge_keys(manifest, lessons_by_slug):
    """This course's full flag-key vocabulary: every scheduled lesson's flag_keys, plus the
    manifest's own extra_challenge_keys (capstones and other non-lesson, static/manually-graded
    CTFd-only challenges with no attributable per-lesson lab). Single source of truth for
    seed_flags.py and check_flag_keys.py — replaces a hand-maintained CHALLENGES list per repo."""
    keys = set(manifest.extra_challenge_keys)
    for slug in manifest.lesson_slugs():
        keys.update(lessons_by_slug[slug].flag_keys)
    return sorted(keys)
