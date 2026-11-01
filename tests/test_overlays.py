"""Consistency tests for the overlays and the worked example.

They check structure and coherence, not whether a mapping is right (that is the independent review, see
docs/review.md). Run:  pytest
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from validate_crosswalk import OVERLAYS, load_all, split_list  # noqa: E402

PRIORITIES = {"P1", "P2", "P3", "P4"}
IAR_FAMILIES = [f"M{i}" for i in range(1, 7)] + [f"T{i}" for i in range(1, 10)]


@pytest.fixture(scope="module")
def data():
    rows, overlays = load_all()
    return rows, overlays


def test_validator_accepts_the_sources(data):
    rows, overlays = data
    assert len(rows) == 93
    assert set(overlays) == set(OVERLAYS)


@pytest.mark.parametrize("key", sorted(OVERLAYS))
def test_every_row_maps_to_something(data, key):
    _, overlays = data
    empty = [r["ref"] for r in overlays[key] if not split_list(r.get("iso27001_2022")) and not split_list(r.get("iso27001_clauses"))]
    assert not empty, f"{key}: rows with neither Annex A controls nor ISMS clauses: {empty}"


@pytest.mark.parametrize("key", sorted(OVERLAYS))
def test_ratings_and_statuses_are_known(data, key):
    _, overlays = data
    for r in overlays[key]:
        assert r["confidence"] in {"high", "medium"}, (key, r["ref"], r["confidence"])
        assert r["verification"] in {"verified", "secondary", "unverified"}, (key, r["ref"], r["verification"])


@pytest.mark.parametrize("key", sorted(OVERLAYS))
def test_every_partial_match_explains_itself(data, key):
    _, overlays = data
    silent = [r["ref"] for r in overlays[key] if r["confidence"] == "medium" and not (r.get("notes") or "").strip()]
    assert not silent, f"{key}: medium-confidence rows need a note saying what differs: {silent}"


def test_uae_iar_structure(data):
    _, overlays = data
    rows = overlays["uae_iar"]
    refs = [r["ref"] for r in rows]
    assert len(rows) == 66, len(rows)
    assert len(set(refs)) == len(refs)
    assert all(re.fullmatch(r"[MT][1-9]\.\d{1,2}", ref) for ref in refs), refs
    families = sorted({ref.split(".")[0] for ref in refs}, key=lambda f: (f[0] != "M", int(f[1:])))
    assert families == IAR_FAMILIES
    for r in rows:
        prios = set(split_list(r["priority"]))
        assert prios and prios <= PRIORITIES, (r["ref"], r["priority"])
        assert r["group"].startswith(r["ref"].split(".")[0] + " "), (r["ref"], r["group"])


def test_uae_iar_is_verified_against_the_publisher(data):
    _, overlays = data
    assert {r["verification"] for r in overlays["uae_iar"]} == {"verified"}


def test_worked_example_figures_match_the_overlay(data):
    _, overlays = data
    rows = overlays["uae_iar"]
    text = (ROOT / "examples" / "uae-iar-gap-assessment-contoso-logistics.md").read_text(encoding="utf-8")
    high = sum(1 for r in rows if r["confidence"] == "high")
    assert f"of the {len(rows)} IAR sub-families" in text
    assert f"{high} sub-families map to ISO 27001 with `high` confidence" in text
    met, partial, gap = (int(x) for x in re.search(r"(\d+) were \*Met\*.*?(\d+) were \*Partial\* and (\d+) were \*Gap\*", text, re.S).groups())
    assert met + partial + gap == len(rows)
    assert re.search(r"Assessment period \(fictional\) \| .*2026", text), "the worked example must be dated"
    for fam in IAR_FAMILIES:
        assert re.search(rf"^\| {fam} ", text, re.M), f"worked example has no finding row for {fam}"


def test_sources_cover_every_overlay_and_record_changes():
    text = (ROOT / "docs" / "sources.md").read_text(encoding="utf-8")
    for key in OVERLAYS:
        assert f"`{key}`" in text, f"docs/sources.md has no section for {key}"
    assert "accessed on **2026-11-01**" in text
    assert "## Source and mapping changes" in text


def test_review_page_does_not_claim_a_review_that_did_not_happen():
    text = (ROOT / "docs" / "review.md").read_text(encoding="utf-8")
    for key, meta in OVERLAYS.items():
        assert meta["label"].split()[0] in text, f"review status missing for {key}"
    rows = [line for line in text.splitlines() if line.startswith("| ") and "not yet reviewed" not in line and "Overlay" not in line]
    for line in rows:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) == 6 and cells[3] not in {"", "—"}:
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[4]), f"a recorded review needs a date: {line}"
