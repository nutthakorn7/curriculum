# tools/validate.py — manifest validation + the lesson portability invariant lint.
import os
import re

# A lesson must not hard-code a schedule number for itself or another lesson.
_WEEK_WORD = re.compile(r"\b(?:Week|Day|Session|Lesson)\s+\d+\b")
_SLIDE_PATH = re.compile(r"slides/(?:week|day|session|lesson)\d+\.md")


def validate_manifest(manifest, lessons_by_slug):
    """Return a list of human-readable error strings (empty == valid)."""
    errors = []
    seen_slots = set()
    seen_at = {}                                  # lesson slug -> its slot (in order)
    for s in manifest.schedule:
        if s.slot in seen_slots:
            errors.append(f"duplicate slot {s.slot}")
        seen_slots.add(s.slot)
        if s.kind != "lesson":
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
