import pytest
from tools import crossref, model


def _manifest():
    return model.Manifest(
        course={"brand": "KOSEN·KMITL"},
        schedule_unit="weeks", slot_label="Week {n}",
        target_repo="x/y",
        schedule=[model.Slot(2, "lesson", "hash"),
                  model.Slot(3, "lesson", "macs"),
                  model.Slot(5, "lesson", "key-exchange")],
    )


def test_ref_resolves_to_slot_label():
    ctx = crossref.context(_manifest(), current_slug="macs")
    assert crossref.render("builds on {{ ref('hash') }}", ctx) == "builds on Week 2"


def test_self_tokens():
    ctx = crossref.context(_manifest(), current_slug="macs")
    assert crossref.render("{{ slot_label }} · slides {{ slides }} · {{ brand }}", ctx) \
        == "Week 3 · slides slides/week03.md · KOSEN·KMITL"
    assert crossref.render("cd {{ labpath }}", ctx) == "cd labs/week03-macs"


def test_prev_next():
    ctx = crossref.context(_manifest(), current_slug="macs")
    assert crossref.render("{{ prev }} / {{ next }}", ctx) == "Week 2 / Week 5"


def test_ref_link():
    ctx = crossref.context(_manifest(), current_slug="key-exchange")
    assert crossref.render("{{ ref('hash', link=True) }}", ctx) == "../week02-hash/"


def test_unscheduled_ref_raises():
    ctx = crossref.context(_manifest(), current_slug="macs")
    with pytest.raises(crossref.CrossRefError):
        crossref.render("{{ ref('not-in-course') }}", ctx)


def test_plain_markdown_untouched():
    ctx = crossref.context(_manifest(), current_slug="hash")
    assert crossref.render("# Hashing\nNo tokens here.\n", ctx) == "# Hashing\nNo tokens here.\n"


def test_labname_has_no_labs_prefix():
    ctx = crossref.context(_manifest(), current_slug="macs")
    assert crossref.render("{{ labname }}", ctx) == "week03-macs"
    assert crossref.render("{{ labpath }}", ctx) == "labs/week03-macs"
