# Cross-Course Lesson Library — Design

**Date:** 2026-07-22 · **Status:** Approved (brainstorm complete; pending spec review before writing-plans)

## 1. Problem & motivation

Three courses — `software-security` (19-week), `security-cryptography` (19-week), and
`cloud-infrastructure-security` (lesson-based) — each live in their own public GitHub repo, and every
lesson is physically tied to a week/lesson number (directory names `labs/week11-…`, slide files
`slides/week11.md`, marp headers `"… · Week 11"`, and in-content refs like *"skim last week's recap"*
and *"Slides: slides/week11.md"*). Because content is duplicated per repo and hard-coded to a schedule
slot, **the same lesson cannot be reused across courses** without copy-paste that then drifts.

This reuse need is already real and already handled *by hand*:

- `software-security/syllabus-mfu.md` states it is *"the same content and pedagogy as the parent
  software-security course, compressed from a 16-week weekly format into 7 all-day Saturday sessions…
  This file is MFU-specific scheduling; `syllabus.md` is the canonical 19-week version this content is
  drawn from."* — i.e. the same lessons, re-scheduled. A manual manifest.

Two upcoming drivers make the manual approach untenable:

1. **Short courses** — ad-hoc intensives (e.g. a 1-day PQC workshop) that pick a subset of existing
   lessons on a compressed schedule.
2. **New courses** — e.g. a Quantum Computing course that pulls existing crypto/PQC lessons and adds
   new ones.

## 2. Goals & non-goals

**Goals**
- One source of truth for each lesson; a lesson is authored once and reused across any number of courses.
- A "course" is a thin manifest that selects lessons, orders them, and assigns schedule labels + branding.
- Short courses, new courses, and the MFU re-scheduling all become "just another manifest."
- Students keep their current workflow unchanged: `git clone <course-repo>`, `cd labs/<slot> && docker compose up`.
- Preserve the existing per-course attributable-flag model and its cross-course domain separation.

**Non-goals (locked decisions from the brainstorm)**
- **No per-course content variants.** Reuse is *re-scheduling only* — a lesson's content is identical in
  every course that uses it. There is deliberately **no** conditional-section / fork mechanism in a
  lesson. (If this ever changes, it is a separate future design; the whole architecture below leans on
  this simplification.)
- Not changing the delivery medium: still Docker-first, still cloned course repos (not a web portal).

## 3. Architecture overview

```
┌─────────────────────── monorepo: KOSEN69 - curriculum (SOURCE OF TRUTH) ───────────────────────┐
│                                                                                                  │
│   lessons/<slug>/           courses/<course>.yml            tools/render.py                       │
│   (self-contained,          (manifest: which lessons,       (reads a manifest, emits the          │
│    schedule-agnostic)        order, slot labels, brand,      course's student-facing tree)         │
│                              target repo, flag salt env)                                          │
└──────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                │  render (per manifest)
                    ┌───────────────────────────┼───────────────────────────┐
                    ▼                           ▼                           ▼
         software-security repo      security-cryptography repo    quantum-computing repo …
         (GENERATED student view)    (GENERATED student view)      (GENERATED — new manifest)
         students clone this         students clone this           students clone this
```

- **Instructor edits `lessons/` in the monorepo, never the course repos.** Course repos become generated
  artifacts (a hand-edit there would be clobbered on the next render).
- Adding a course = adding one `courses/*.yml` file. No content is copied by hand.

## 4. Component: the lesson unit

```
lessons/<slug>/
  lesson.yml        # metadata (schema below)
  README.md         # objectives + run instructions; refs other lessons by slug, never by number
  worksheet.md
  slides.md         # optional; marp source, header carries NO slot number (renderer injects it)
  docker-compose.yml, vulnerable_app.py / fixed_app.py, exploit.py, …   # lab code, flat, copied verbatim
```

A lesson is flat: everything except `lesson.yml` and `slides.md` lives directly under `lessons/<slug>/`
and is treated as lab content. On render, `slides.md` (if present) is split out to the course's
`slides/<slotfile>.md`; every other file is copied — `.md` files with tokens resolved, everything else
verbatim — into `labs/<labdir>/`.

`lesson.yml`:

```yaml
slug: key-exchange                       # unique, stable, filesystem-safe; the lesson's identity
title: "Key Exchange & Unauthenticated DH MITM"
kind: LAB                                # LAB | HYBRID | CONCEPTUAL
duration_min: 180
tags: [crypto, mitm, diffie-hellman]
cwe: [CWE-345]
prereqs: [hash-basics]                   # other lesson slugs (used to validate a manifest's ordering)
flag_key: kex                            # the FLAG_<KEY> this lab mints; omit for flagless lessons
```

**Invariant (enforced by a lint check):** a lesson's files must not contain a literal week/day/session
number for itself or any other lesson, and must not hard-link to `slides/weekNN.md`. All such references
go through the cross-reference mechanism (§6). This invariant is what makes a lesson portable.

## 5. Component: the course manifest

```yaml
# courses/software-security.yml
course:
  name: "Software Security"
  code: "1305315"                        # optional; per offering
  brand: "KOSEN·KMITL"                   # masthead wordmark
  flag_salt_env: SWSEC_FLAG_SALT         # domain-separated per course (never shared across courses)
  challenge_keys_env: AIRSEC_CHALLENGE_KEYS
  target_repo: "nutthakorn7/software-security"

schedule_unit: weeks                     # weeks | days | sessions | lessons  → controls slot label + slide filename
slot_label: "Week {n}"                   # how a slot renders in headers/prose ("Day {n}", "Session {n}", …)

schedule:
  - {slot: 1,  lesson: threat-modeling}
  - {slot: 2,  lesson: sdlc-tooling}
  - {slot: 5,  lesson: key-exchange}
  - {slot: 7,  review: "Midterm review"}         # non-lesson slot (no lesson dir)
  - {slot: 8,  exam: "Midterm (written)"}        # non-lesson slot
  - {slot: 15, lesson: pqc-hndl}
```

- `schedule_unit` + `slot_label` drive both the on-page label ("Week 5") and the generated slide filename
  (`slides/week05.md`). MFU uses `schedule_unit: sessions`, `slot_label: "Session {n}"`; a slot may map to
  a half-day (the manifest can carry `session: "Sat 2, AM"` metadata for the syllabus table).
- Non-lesson slots (`exam`, `review`, `project`, `holiday`) are allowed so a manifest fully describes the
  calendar, not only the lessons.
- **The manifest is validated before render:** every `lesson:` slug must exist; every lesson's `prereqs`
  must appear at an earlier slot in *this* manifest (or be explicitly waived) — this catches
  "you scheduled key-exchange before hash-basics."

### Examples the same machinery produces
- `courses/software-security-mfu.yml` — same lesson slugs as `software-security.yml`, packed into 7
  session slots. (Replaces the hand-maintained `syllabus-mfu.md`.)
- `courses/quantum-computing.yml` — references `pqc-hndl`, `key-exchange`, `lamport-ots`, plus new
  quantum-specific lessons.
- `courses/shortcourse-pqc-1day.yml` — `schedule_unit: sessions`, 4 lessons, a capstone slot.

## 6. Component: cross-reference resolution (the one invasive part)

Content today says "see Week 5", "skim last week's recap", "Slides: slides/week11.md". Under
re-scheduling these are wrong in any other course. Lessons therefore reference **by slug** through a
minimal template layer, and the renderer resolves each to the current course's slot label.

Supported template tokens (Jinja2, evaluated **only in `*.md` files** — never in code, `docker-compose.yml`,
or `exploit.py`, which are copied verbatim):

| Token | Resolves to | Example output |
|---|---|---|
| `{{ slides }}` | this lesson's generated slide path in this course | `slides/week11.md` · `slides/day3.md` |
| `{{ ref('hash-basics') }}` | the slot label of another lesson in this course | `Week 2` · `Session 1` |
| `{{ ref('hash-basics', link=True) }}` | a relative link to that lesson's lab | `../week02-hash/` |
| `{{ prev }}` / `{{ next }}` | the adjacent lesson in this manifest's order | `Week 4` |
| `{{ slot }}` / `{{ slot_label }}` | this lesson's own slot | `5` / `Week 5` |
| `{{ brand }}` | the course masthead | `KOSEN·KMITL` |

- A lesson that references a slug **not scheduled in the current course** is a render error (fail closed),
  surfaced with the manifest + lesson so it is fixed rather than silently dangling.
- Lessons with no cross-refs contain no tokens and pass through untouched — most prose is plain markdown.
- **Import cost:** porting existing content into `lessons/` includes a one-time pass replacing literal
  "Week N" / `slides/weekNN.md` refs with tokens. This is the only content-invasive step and is done once
  per lesson at import.

## 7. Component: the flag model

The existing model (per-student HMAC flags, `FLAG_<KEY>` env, per-course salt for domain separation) is
preserved by splitting *what* from *whose*:

- **`flag_key` lives on the lesson** (it is a property of that lab).
- **Salt + student roster live on the course** (`instructor/`, git-ignored — unchanged convention).
- `seed_flags.py` becomes a single shared tool in the monorepo: given a manifest, it collects the
  `flag_key` of every scheduled lesson, then mints per-student flags using **that course's**
  `flag_salt_env`. Different salt per course ⇒ the same lesson's flag is a different value in
  `software-security` vs `quantum-computing` (domain separation intact).
- `check_flag_keys.py` drift guard now compares manifest-derived keys against the course's
  `AIRSEC_CHALLENGE_KEYS` — no more hand-maintained `CHALLENGES` list per repo.

## 8. Component: the renderer

`tools/render.py <course-manifest>`:

1. Parse + **validate** the manifest (slugs exist, prereqs ordered, no duplicate slots).
2. Build the `slug → slot` map for this course.
3. For each scheduled lesson:
   - copy `lessons/<slug>/lab/` → `<target>/labs/<slot-prefixed-name>/` verbatim.
   - render `slides.md` → `<target>/slides/<slotfile>.md`, injecting the marp header + `{{ … }}` tokens.
   - render `worksheet.md`, `README.md` with tokens resolved.
4. For non-lesson slots, emit the calendar entry only.
5. Generate `course-plan.md` / syllabus table + `AGENDA.md` from the manifest (single source for the calendar).
6. Write into the target course repo's working tree; the instructor reviews `git diff`, commits, pushes.

**Idempotence:** rendering the same (lessons + manifest) twice produces a byte-identical tree — this is
what makes the parity check (§10) and safe re-renders possible.

## 9. Monorepo layout

```
KOSEN69 - curriculum/
  lessons/<slug>/…                     # the library
  courses/<course>.yml                 # manifests (incl. -mfu, quantum, short courses)
  shared/                              # ETHICS.md, SUBMISSION.md, toolbox/, brand assets reused across courses
  tools/
    render.py                         # manifest → course repo tree
    validate.py                       # manifest + lesson-invariant linters
    seed_flags.py                     # per-course attributable flags (moved from each repo's instructor/)
    check_flag_keys.py                # drift guard (manifest-derived)
  instructor/                          # git-ignored: salts, rosters, answer keys, research materials
  docs/superpowers/specs|plans/
  tests/                               # renderer + validator + cross-ref unit tests, link-integrity checks
```

## 10. Migration (strangler-fig — the live courses must never break)

1. Stand up the monorepo skeleton (`tools/render.py`, `validate.py`, one lesson, one manifest) and prove
   the pipeline on a single lesson end-to-end.
2. **Pilot: `security-cryptography` first** — chosen because it is the smallest, its labs are already
   topic-named (`week02-hash` → `hash`), and it has **no `slides/` directory yet** (less to port ⇒ lowest
   risk). Import its lessons, write `courses/security-cryptography.yml`, render.
3. **Parity gate:** `render` into a scratch copy and `git diff` against the *current* published repo until
   the generated tree matches the intended content (differences are reviewed, not blindly accepted). Only
   after parity does the generated tree replace the hand-maintained one.
4. Import `software-security` next (largest; its payoff is that `-mfu.yml` immediately replaces the manual
   `syllabus-mfu.md` — the first concrete reuse win), then `cloud-infrastructure-security` (already
   lesson-named ⇒ easy).
5. Only once a course's generated twin is at parity and pushed does its old hand-maintained content stop
   being edited directly. Old repos stay live throughout.
6. After all three are generated: quantum-computing and any short course are new manifests with near-zero
   marginal cost — the goal state.

## 11. Testing & verification

- **Validator unit tests:** unknown slug, prereq-after-dependent, duplicate slot, dangling `ref()` all
  fail with a clear message.
- **Cross-ref unit tests:** the same lesson rendered under a `weeks` manifest vs a `sessions` manifest
  produces the correct, different slot labels; a `ref()` to an unscheduled slug errors.
- **Idempotence test:** render twice → identical bytes.
- **Parity diff (per migrated course):** generated tree vs intended current content.
- **Link-integrity check:** no rendered `.md` contains a leftover `{{ … }}` token or a broken relative link.
- **Lab smoke (spot-check):** a rendered lab still `docker compose up`s and its `exploit.py` passes — the
  copy-verbatim guarantee means this should be unchanged from the source lesson.

## 12. Risks & open items

- **Renderer bug clobbers a course repo.** Mitigation: render into a scratch dir, human `git diff` +
  commit in the target repo (never force-push from the tool); course repos keep full git history.
- **Cross-ref import is tedious.** Accepted: it is one-time per lesson and mechanically checkable (grep for
  residual "Week \d" after import).
- **`instructor/` consolidation.** Salts/rosters move from three `instructor/` dirs into the monorepo's
  git-ignored `instructor/`, keyed per course — must preserve the existing per-course salts so already-issued
  flags stay valid. (Handle in the plan; do not regenerate salts.)
- **Naming.** Monorepo named `KOSEN69 - curriculum` provisionally; trivially renamed before it has remotes.

## 12a. Future output targets (deliberately out of scope now)

The renderer is a `manifest → output` function and the lessons are a structured library
(`lesson.yml` + markdown, with slug/tags/cwe/prereqs/flag_key). Additional consumers of the same
source are therefore a clean *additive* extension, never a rearchitecture:

- **A 2027 LMS / HTB-THM-style platform** (deferred per the platform roadmap) would be a second output
  target reading the same `lessons/` — building it now would be speculative (YAGNI) and premature (its
  shape is unknown). The single-source design keeps that door open at zero present cost.
- **Quiz bank → live-quiz platform.** Quizzes today live at repo level (`quizzes/`, `instructor/quizzes/`).
  A natural later step is to make each lesson own its quiz (`lessons/<slug>/quiz.md`) and have the renderer
  aggregate a per-course bank that also feeds the live-quiz platform — so quizzes become single-sourced too.
  **Not in the pilot;** a follow-on plan.

No work is committed for these now. This section only records the intent so the pilot does not accidentally
foreclose them (e.g. keep `lesson.yml` rich; keep the renderer target-agnostic).

## 13. Locked decisions (from the brainstorm)

1. Reuse is **re-scheduling only** — no per-course content variants; lessons are single-source.
2. Source of truth = **one monorepo** (`lessons/` + `courses/*.yml` + `tools/`).
3. Delivery = renderer **generates into the existing course repos**; student clone/Docker workflow unchanged.
4. Cross-references use a **slug-based Jinja token layer in `.md` files only**; code is copied verbatim.
5. Migration is **strangler-fig**, piloting **`security-cryptography`**, gated on a **parity diff**.
