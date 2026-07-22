# tools/validate.py — manifest validation + the lesson portability invariant lint.
import os
import re

# A lesson must not hard-code a schedule number for itself or another lesson.
_WEEK_WORD = re.compile(r"\b(?:Weeks?|Days?|Sessions?|Lessons?)\s+\d+(?:\s*[-–]\s*\d+)?\b", re.IGNORECASE)
_SLIDE_PATH = re.compile(r"slides/(?:week|day|session|lesson)\d+\.md", re.IGNORECASE)


def validate_manifest(manifest, lessons_by_slug):
    """Return a list of human-readable error strings (empty == valid)."""
    errors = []
    seen_nonlesson_slots = set()      # non-lesson slots (exam/review/project/...) are one-per-slot
    seen_at = {}                      # lesson slug -> the (first) slot it's scheduled at, in order
    for s in manifest.schedule:
        if s.kind != "lesson":
            if s.slot in seen_nonlesson_slots:
                errors.append(f"duplicate slot {s.slot}")
            seen_nonlesson_slots.add(s.slot)
            continue
        # Multiple DIFFERENT lessons may legitimately share one slot (e.g. an MFU session packing
        # several weeks into one day) — labdir() already keys on slug, so no path collision results.
        if s.value in seen_at:
            errors.append(f"lesson '{s.value}' scheduled more than once (slots must map to distinct lessons)")
            continue
        if s.value not in lessons_by_slug:
            errors.append(f"slot {s.slot}: unknown lesson slug '{s.value}'")
            continue
        for pre in lessons_by_slug[s.value].prereqs:
            if pre not in seen_at:
                errors.append(
                    f"slot {s.slot}: lesson '{s.value}' needs prereq '{pre}' scheduled earlier "
                    f"(it is missing or comes later)")
        seen_at[s.value] = s.slot
    return errors


def missing_lessons(canonical_manifest, compressed_manifest):
    """Lesson slugs required by canonical_manifest but absent from compressed_manifest. Only
    lesson-kind slots count as "required content" — non-lesson calendar entries (exam/review/project)
    may be freely merged or dropped by a compressed schedule without that being a coverage gap."""
    return set(canonical_manifest.lesson_slugs()) - set(compressed_manifest.lesson_slugs())


def missing_phases(canonical_manifest, compressed_manifest):
    """Exam-kind phases (e.g. 'midterm', 'final') required by canonical_manifest but absent from
    compressed_manifest. Only exam slots carrying a `phase` tag are "required assessment periods" —
    an untagged exam/review/project slot is ordinary calendar content and isn't checked here. A
    compressed schedule MAY merge multiple canonical exam slots sharing one phase into a single slot;
    it may NOT drop a phase entirely."""
    def phases(manifest):
        return {s.phase for s in manifest.schedule if s.kind == "exam" and s.phase}
    return phases(canonical_manifest) - phases(compressed_manifest)


def lint_lesson(lesson_dir):
    """Return invariant violations (literal schedule refs) across the lesson's .md files."""
    violations = []
    for root, _dirs, files in os.walk(lesson_dir):
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, lesson_dir)
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    for m in _WEEK_WORD.finditer(line):
                        violations.append(f"{rel}:{i}: literal schedule ref '{m.group(0)}' "
                                          f"(use a cross-ref token instead)")
                    for m in _SLIDE_PATH.finditer(line):
                        violations.append(f"{rel}:{i}: hard-coded slide path '{m.group(0)}' "
                                          f"(use {{{{ slides }}}} instead)")
    return violations
