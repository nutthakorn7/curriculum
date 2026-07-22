import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_REPO = ROOT.parent / "KOSEN69 - cloud-infrastructure-security"
SRC_LABS = SRC_REPO / "labs"

LESSON_DIRS = {
    "aws-fundamentals-intro": "lesson01-03-aws-fundamentals-intro",
    "ec2-lambda-beanstalk": "lesson04-ec2-lambda-beanstalk",
    "s3-static-site-lambda-sns": "lesson05-s3-static-site-lambda-sns",
    "load-balancing-autoscaling": "lesson06-load-balancing-autoscaling",
    "iam-policy-evaluation": "lesson07-iam-policy-evaluation",
    "cloudtrail-monitoring": "lesson07b-cloudtrail-monitoring",
    "vpc-networking": "lesson10-vpc-networking",
    "kms-envelope-encryption": "lesson11-kms-envelope-encryption",
    "s3-versioning-lifecycle-replication": "lesson13-s3-versioning-lifecycle-replication",
    "config-lambda-remediation": "lesson14-config-lambda-remediation",
}

# This course was deliberately renumbered from AWS Academy's own module numbers (embedded in the
# source directory names, e.g. "lesson13-...") to a clean sequential schedule (our own slots 1-10) —
# see docs/superpowers/plans/2026-07-22-cloud-infrastructure-security-full-import.md. Every lesson's
# self-title/self-path and the two same-course cross-references change accordingly; this is intentional,
# not a parity bug. Everything else in every file must still match source exactly. Each entry below was
# derived from a manually reviewed, complete diff of every one of the 10 lessons (not guessed) — do not
# add an entry without first confirming the corresponding diff is exactly this substitution and nothing
# else.
SOURCE_REPLACEMENTS = {
    "aws-fundamentals-intro": [
        ("# Lessons 1–3 — AWS Fundamentals", "# Lesson 1 — AWS Fundamentals"),
        ("same precedent as `lesson11`'s KMS envelope-encryption", "same precedent as Lesson 8's KMS envelope-encryption"),
        ("# Worksheet — Lessons 1–3: AWS Fundamentals", "# Worksheet — Lesson 1: AWS Fundamentals"),
    ],
    "ec2-lambda-beanstalk": [
        ("# Lesson 4 — EC2 Instance Roles", "# Lesson 2 — EC2 Instance Roles"),
        ("cd labs/lesson04-ec2-lambda-beanstalk", "cd labs/lesson02-ec2-lambda-beanstalk"),
        ("# Worksheet — Lesson 4: EC2 Instance Roles", "# Worksheet — Lesson 2: EC2 Instance Roles"),
    ],
    "s3-static-site-lambda-sns": [
        ("# Lesson 5 — S3 Static Website Hosting", "# Lesson 3 — S3 Static Website Hosting"),
        ("cd labs/lesson05-s3-static-site-lambda-sns", "cd labs/lesson03-s3-static-site-lambda-sns"),
        ("# Worksheet — Lesson 5: S3 Static Website Hosting", "# Worksheet — Lesson 3: S3 Static Website Hosting"),
    ],
    "load-balancing-autoscaling": [
        ("# Lesson 6 — Load Balancing", "# Lesson 4 — Load Balancing"),
        ("cd labs/lesson06-load-balancing-autoscaling", "cd labs/lesson04-load-balancing-autoscaling"),
        ("# Worksheet — Lesson 6: Load Balancing", "# Worksheet — Lesson 4: Load Balancing"),
    ],
    "iam-policy-evaluation": [
        ("# Lesson 7 — IAM Policy Evaluation", "# Lesson 5 — IAM Policy Evaluation"),
        ("cd labs/lesson07-iam-policy-evaluation", "cd labs/lesson05-iam-policy-evaluation"),
        ("# Worksheet — Lesson 7: IAM Policy Evaluation", "# Worksheet — Lesson 5: IAM Policy Evaluation"),
    ],
    "cloudtrail-monitoring": [
        ("# Lesson 7 (2nd topic) — CloudTrail", "# Lesson 6 — CloudTrail"),
        ("cd labs/lesson07b-cloudtrail-monitoring", "cd labs/lesson06-cloudtrail-monitoring"),
        ("# Worksheet — Lesson 7 (2nd topic): CloudTrail", "# Worksheet — Lesson 6: CloudTrail"),
        # NOTE: worksheet.md's "the two topics of Lesson 7 deliberately split across blocks" is a
        # deliberate, documented exception (explanatory text about AWS's own historical numbering) and
        # must NOT be replaced — it stays literal "Lesson 7" in both source and rendered.
    ],
    "vpc-networking": [
        ("# Lesson 10 — VPC Networking", "# Lesson 7 — VPC Networking"),
        ("cd labs/lesson10-vpc-networking", "cd labs/lesson07-vpc-networking"),
        ("# Worksheet — Lesson 10: VPC Networking", "# Worksheet — Lesson 7: VPC Networking"),
    ],
    "kms-envelope-encryption": [
        ("# Lesson 11 — S3 Server-Side Encryption", "# Lesson 8 — S3 Server-Side Encryption"),
        ("# Worksheet — Lesson 11: S3 Server-Side Encryption", "# Worksheet — Lesson 8: S3 Server-Side Encryption"),
    ],
    "s3-versioning-lifecycle-replication": [
        ("# Lesson 13 — S3 Data Protection", "# Lesson 9 — S3 Data Protection"),
        ("same precedent as Lesson 11).", "same precedent as Lesson 8)."),
        ("# Worksheet — Lesson 13: S3 Versioning", "# Worksheet — Lesson 9: S3 Versioning"),
    ],
    "config-lambda-remediation": [
        ("# Lesson 14 — AWS Config", "# Lesson 10 — AWS Config"),
        ("cd labs/lesson14-config-lambda-remediation", "cd labs/lesson10-config-lambda-remediation"),
        ("# Worksheet — Lesson 14: AWS Config", "# Worksheet — Lesson 10: AWS Config"),
        ("(Lesson 14 falls in Block 2.)", "(Lesson 10 falls in Block 2.)"),
    ],
}


def _expected_text(slug, raw_source_text):
    # Each (old, new) pair applies to exactly one of a lesson's files (README.md vs worksheet.md) —
    # .replace() is a harmless no-op on the file where `old` doesn't appear. If a pair never matches
    # ANY file, the final rendered-vs-expected equality assertion still fails (the untouched "old" text
    # stays in `expected` and won't match the actually-rendered "new" text), so silent typos are not
    # possible — this just skips the noisier per-file assertion.
    text = raw_source_text
    for old, new in SOURCE_REPLACEMENTS.get(slug, []):
        text = text.replace(old, new)
    return text


pytestmark = pytest.mark.skipif(not SRC_LABS.is_dir(), reason="source cloud-infrastructure-security repo not present")


def _render(tmp):
    from tools import render
    render.render_course(str(ROOT / "courses" / "cloud-infrastructure-security.yml"),
                         lessons_root=str(ROOT / "lessons"), out_dir=str(tmp / "out"))
    return tmp / "out"


def test_no_unresolved_tokens(tmp_path):
    out = _render(tmp_path)
    for md in out.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        assert "{{" not in text and "{%" not in text, f"unresolved token in {md}"


@pytest.mark.parametrize("slug,srcdir", sorted(LESSON_DIRS.items()))
def test_lab_code_byte_identical(tmp_path, slug, srcdir):
    out = _render(tmp_path)
    src_lab = SRC_LABS / srcdir
    out_lab = next(out.glob(f"labs/lesson*-{slug}"))
    for src in src_lab.rglob("*"):
        if src.is_dir() or src.suffix == ".md" or "__pycache__" in src.parts:
            continue
        rel = src.relative_to(src_lab)
        dst = out_lab / rel
        assert dst.is_file(), f"{slug}: missing rendered file {rel}"
        assert dst.read_bytes() == src.read_bytes(), f"{slug}: lab code drifted: {rel}"


@pytest.mark.parametrize("slug,srcdir", sorted(LESSON_DIRS.items()))
def test_markdown_matches_source(tmp_path, slug, srcdir):
    out = _render(tmp_path)
    src_lab = SRC_LABS / srcdir
    out_lab = next(out.glob(f"labs/lesson*-{slug}"))
    for src in src_lab.rglob("*.md"):
        rel = src.relative_to(src_lab)
        dst = out_lab / rel
        assert dst.is_file(), f"{slug}: missing rendered {rel}"
        expected = _expected_text(slug, src.read_text(encoding="utf-8"))
        assert dst.read_text(encoding="utf-8") == expected, \
            f"{slug}: rendered {rel} != expected (source + known renumbering substitutions)"
