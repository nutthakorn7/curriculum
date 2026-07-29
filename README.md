# KOSEN69 — Curriculum (lesson library + course manifests)

Single source of truth for the KOSEN69 security course family. Lessons are authored **once** here and
composed into courses by thin manifests; a renderer generates each course's student-facing tree into its
own repo (`software-security`, `security-cryptography`, `cloud-infrastructure-security`, …). Short courses,
new courses, and site-specific re-scheduling (e.g. MFU) are each just another manifest.

- **Design:** [`docs/superpowers/specs/2026-07-22-cross-course-lesson-library-design.md`](docs/superpowers/specs/2026-07-22-cross-course-lesson-library-design.md)
- **Status:** engine + all three courses built. 34 lessons (software-security 12 · security-cryptography 12 · cloud-infrastructure-security 10), 4 course manifests, atomic renderer, 120 passing tests (unit + byte/content parity vs. every published source repo). Remaining before the source repos are generated *from* here (rather than kept in parity): the cutover itself, calendar/AGENDA generation, and porting existing slide decks into the library.

> `instructor/` is git-ignored (salts, flag tables, rosters, answer keys) — never committed.

## Reusing lessons — short courses, other subjects, any ordering

`lessons/` is a **library of topic modules**, not a week-by-week course. A course
is a *manifest*: an ordering over that library, with its own unit and label.

```
lessons/injection/              ← the module. Named by topic, never by week.
courses/software-security.yml   ← 19 weeks   · "Week {n}"
courses/software-security-mfu.yml ← 14 slots · "Session {n}"  ← same 12 lessons, repacked
courses/security-cryptography.yml
courses/cloud-infrastructure-security.yml
```

`labs/weekNN-*/` in a course repo is the **rendered output**, not the source —
which is why the byte-parity gate exists.

### Making a new one

Write a manifest. Nothing is copied.

```yaml
schedule_unit: modules
slot_label: "Module {n}"
schedule:
  - {slot: 1, lesson: threat-modeling}
  - {slot: 2, lesson: cryptography}
  - {slot: 3, lesson: injection}
```

See `courses/EXAMPLE-web-app-security-short.yml` for a complete two-day one.

### Ordering is checked, because intuition gets it wrong

Each lesson declares what its own material assumes:

```yaml
prereqs: [authn-authz]      # api-security: BOLA is IDOR at the API layer
prereqs: [aes-modes, macs]  # aead: padding oracle needs CBC, encrypt-then-MAC needs MACs
```

`tools/validate.py` refuses a manifest that schedules a lesson before something
it needs. That first example is not hypothetical — the draft of the short course
above led with `api-security` because it reads sensibly by topic name, and was
refused:

```
slot 1: lesson 'api-security' needs prereq 'authn-authz' scheduled earlier
slot 3: lesson 'authn-authz' needs prereq 'cryptography' scheduled earlier
```

Only **hard** dependencies are declared — where the material is incoherent
without the other, not merely where an order feels tidier. Over-declaring would
reject legitimate orderings for no reason; 11 of the 34 lessons are standalone
and should stay that way.
