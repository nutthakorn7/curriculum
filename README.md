# KOSEN69 — Curriculum (lesson library + course manifests)

Single source of truth for the KOSEN69 security course family. Lessons are authored **once** here and
composed into courses by thin manifests; a renderer generates each course's student-facing tree into its
own repo (`software-security`, `security-cryptography`, `cloud-infrastructure-security`, …). Short courses,
new courses, and site-specific re-scheduling (e.g. MFU) are each just another manifest.

- **Design:** [`docs/superpowers/specs/2026-07-22-cross-course-lesson-library-design.md`](docs/superpowers/specs/2026-07-22-cross-course-lesson-library-design.md)
- **Status:** engine + all three courses built. 34 lessons (software-security 12 · security-cryptography 12 · cloud-infrastructure-security 10), 4 course manifests, atomic renderer, 120 passing tests (unit + byte/content parity vs. every published source repo). Remaining before the source repos are generated *from* here (rather than kept in parity): the cutover itself, calendar/AGENDA generation, and porting existing slide decks into the library.

> `instructor/` is git-ignored (salts, flag tables, rosters, answer keys) — never committed.
