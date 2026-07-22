#!/usr/bin/env python3
"""Instructor tool — per-student, attributable CTF/lab flags, for ANY course in this library.

One shared tool instead of a per-repo copy: the challenge-key vocabulary comes from the course's
own manifest (every scheduled lesson's flag_keys, plus the manifest's extra_challenge_keys for
capstones/static challenges with no attributable lab — see tools/model.py's challenge_keys()),
and the salt comes from whichever env var that course's manifest names as flag_salt_env. Different
courses use different env var names (e.g. SWSEC_FLAG_SALT vs SC_FLAG_SALT) specifically so a
leaked flag from one course can never be checked against another course's roster — never reuse a
salt across courses.

Why: if every student gets a UNIQUE flag per challenge, a copied flag is instantly traceable to
the student it was *issued* to — so sharing is detectable, not just banned. Flags are
deterministic (HMAC of studentID+challenge keyed by a secret salt), so you can regenerate or
reverse-look-up any flag without storing them.

Run this from the monorepo root. Salts and rosters stay in each course's own instructor/
(git-ignored) — never in this repo. Never publish a salt or a flag table.

Usage:
  export SC_FLAG_SALT='a-long-random-secret-per-cohort'    # THIS course's own salt env var
  python3 -m tools.seed_flags --course courses/security-cryptography.yml gen students.txt -o flags.csv
  python3 -m tools.seed_flags --course courses/security-cryptography.yml env 65123456
  python3 -m tools.seed_flags --course courses/security-cryptography.yml verify 'FLAG{macs_ab12cd34}' students.txt

students.txt = one student ID per line (blank lines / # comments ignored).
"""
import argparse
import csv
import hashlib
import hmac
import os
import sys

from tools import model


def make_flag(student_id: str, challenge: str, salt: str) -> str:
    mac = hmac.new(salt.encode(), f"{student_id}:{challenge}".encode(), hashlib.sha256).hexdigest()[:8]
    return f"FLAG{{{challenge}_{mac}}}"


def load_students(path: str):
    out = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(s)
    return out


def load_course(course_path, lessons_root):
    manifest = model.load_manifest(course_path)
    lessons = model.load_lessons(lessons_root)
    challenges = model.challenge_keys(manifest, lessons)
    return manifest, challenges


def get_salt(args, manifest) -> str:
    salt_env = manifest.course.get("flag_salt_env")
    if not salt_env:
        sys.exit(f"ERROR: {args.course} has no course.flag_salt_env set.")
    salt = args.salt or os.environ.get(salt_env)
    if not salt:
        sys.exit(f"ERROR: set --salt or the {salt_env} env var (a long random per-cohort secret, "
                 f"DIFFERENT from every other course's own salt).")
    return salt


def cmd_gen(args, manifest, challenges):
    salt = get_salt(args, manifest)
    students = load_students(args.students)
    rows = [["student_id", "challenge", "flag"]]
    for sid in students:
        for ch in challenges:
            rows.append([sid, ch, make_flag(sid, ch, salt)])
    with open(args.out, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"Wrote {len(rows) - 1} flags for {len(students)} students -> {args.out}")


def cmd_env(args, manifest, challenges):
    salt = get_salt(args, manifest)
    print(f"# Local .env for student {args.student_id} — used by their docker compose build")
    print(f"STUDENT_ID={args.student_id}")
    for ch in challenges:
        print(f"FLAG_{ch.upper()}={make_flag(args.student_id, ch, salt)}")


def cmd_verify(args, manifest, challenges):
    salt = get_salt(args, manifest)
    students = load_students(args.students)
    for sid in students:
        for ch in challenges:
            if make_flag(sid, ch, salt) == args.flag.strip():
                print(f"MATCH: {args.flag} was issued to student {sid} (challenge: {ch})")
                return
    print(f"NO MATCH: {args.flag} is not a valid issued flag (forged, wrong cohort/salt, or typo).")


def main(argv=None):
    p = argparse.ArgumentParser(description="Per-student attributable flags for any course in this library.")
    p.add_argument("--course", required=True, help="path to the course manifest, e.g. courses/security-cryptography.yml")
    p.add_argument("--lessons", default="lessons")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen", help="generate the student x challenge flag table (CSV)")
    g.add_argument("students")
    g.add_argument("-o", "--out", default="flags.csv")
    g.add_argument("--salt")
    g.set_defaults(func=cmd_gen)

    e = sub.add_parser("env", help="print a .env of flags for one student")
    e.add_argument("student_id")
    e.add_argument("--salt")
    e.set_defaults(func=cmd_env)

    v = sub.add_parser("verify", help="reverse-look-up which student a flag belongs to")
    v.add_argument("flag")
    v.add_argument("students")
    v.add_argument("--salt")
    v.set_defaults(func=cmd_verify)

    args = p.parse_args(argv)
    manifest, challenges = load_course(args.course, args.lessons)
    args.func(args, manifest, challenges)


if __name__ == "__main__":
    main()
