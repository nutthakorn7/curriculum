#!/usr/bin/env python3
"""Drift guard for the flag-key vocabulary, for ANY course in this library.

One shared tool instead of a per-repo copy. The canonical key set now comes from the course's own
manifest (tools.model.challenge_keys — every scheduled lesson's flag_keys plus the manifest's
extra_challenge_keys), not a hand-maintained CHALLENGES list. Checks that against the deployed
course repo's own instructor/ tree, which still holds the real, git-ignored operational files:

  1. the course manifest                         — the canonical source of truth (lesson flag_keys
                                                     + extra_challenge_keys)
  2. platform-build/deploy/.env.example           — AIRSEC_CHALLENGE_KEYS, the deployment-wired
     whitelist the (shared, course-agnostic) airsec_flag_bridge plugin reads at runtime.
  3. platform-build/images/challenges-import.csv  — each challenge's flag_prefix must be a
     known key, else the bridge can't mint an attributable flag for it.
  4. ctfd/challenges.yml                          — the scoreboard flags should use the same
     vocabulary.

Run from the monorepo root, pointed at a course's real instructor/ dir:
  python3 -m tools.check_flag_keys --course courses/security-cryptography.yml \\
      --instructor-dir "../KOSEN69 - security-cryptography/instructor"
(exit 0 = in sync; non-zero = drift)
"""
import argparse
import csv
import os
import re
import sys

from tools import model


def extract_env_keys(path, varname):
    """Pull `VAR=comma,or whitespace,separated,list` from a dotenv-style file. Returns the list
    (order preserved, blanks dropped), or None if absent. Ignores commented-out lines."""
    for line in open(path):
        s = line.strip()
        if s.startswith("#"):
            continue
        if s.startswith(varname + "="):
            raw = s.split("=", 1)[1].strip()
            return [k for k in re.split(r"[,\s]+", raw) if k]
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Flag-key drift guard for any course in this library.")
    ap.add_argument("--course", required=True, help="path to the course manifest")
    ap.add_argument("--lessons", default="lessons")
    ap.add_argument("--instructor-dir", required=True,
                     help="path to that course's real instructor/ dir (in its own repo, git-ignored)")
    args = ap.parse_args(argv)

    manifest = model.load_manifest(args.course)
    lessons = model.load_lessons(args.lessons)
    canon = model.challenge_keys(manifest, lessons)
    canon_set = set(canon)
    print(f"canonical keys ({len(canon)}): {', '.join(canon)}")

    errors = []
    challenge_keys_env = manifest.course.get("challenge_keys_env", "AIRSEC_CHALLENGE_KEYS")

    env_path = os.path.join(args.instructor_dir, "platform-build/deploy/.env.example")
    env_keys = extract_env_keys(env_path, challenge_keys_env)
    if env_keys is None:
        errors.append(f"{challenge_keys_env} not found in {env_path}")
    elif set(env_keys) != canon_set:
        missing = sorted(canon_set - set(env_keys))
        extra = sorted(set(env_keys) - canon_set)
        errors.append(
            f"{challenge_keys_env} in .env.example != manifest-derived challenge keys\n"
            f"    missing from .env.example: {missing}\n"
            f"    extra in .env.example:     {extra}")
    else:
        print(f"[ok] .env.example {challenge_keys_env} matches manifest-derived keys "
              f"({len(env_keys)} keys, set-equal)")

    # every platform catalog flag_prefix must be a known key
    csv_path = os.path.join(args.instructor_dir, "platform-build/images/challenges-import.csv")
    bad = []
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            key = (row.get("flag_prefix") or "").strip()
            if key and key not in canon_set:
                bad.append((row["name"], key))
    if bad:
        errors.append("challenges-import.csv has flag_prefix values not in the manifest-derived keys:\n" +
                      "\n".join(f"    {n}: {k}" for n, k in bad))
    else:
        print("[ok] challenges-import.csv: every flag_prefix is a known key")

    # every scoreboard flag base-key must be a known key
    yml_path = os.path.join(args.instructor_dir, "ctfd/challenges.yml")
    yml = open(yml_path).read()
    keys = re.findall(r"FLAG\{([a-zA-Z0-9]+?)_XXXX\}", yml)
    unknown = sorted({k for k in keys if k not in canon_set})
    if unknown:
        errors.append(f"ctfd/challenges.yml uses flag keys not in the manifest-derived keys: {unknown}")
    else:
        print(f"[ok] ctfd/challenges.yml: all {len(set(keys))} flag keys are canonical")

    if errors:
        print("\nFLAG-KEY DRIFT DETECTED:\n" + "\n".join("  - " + e for e in errors), file=sys.stderr)
        sys.exit(1)
    print("\nAll flag-key sources are in sync.")


if __name__ == "__main__":
    main()
