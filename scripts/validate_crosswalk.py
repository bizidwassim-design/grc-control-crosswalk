#!/usr/bin/env python3
"""
Validate the hand-edited sources of the GRC Control Crosswalk before anything is generated.

Checks
    data/crosswalk.csv          exactly the 93 ISO/IEC 27001:2022 Annex A controls, no gaps, no duplicates,
                                every target cell filled
    data/overlays/<key>.csv     every overlay row has a unique, non-empty identifier and title, references only
                                Annex A controls that exist in the 93-control list (and only ISMS clauses 4-10 that
                                exist in ISO/IEC 27001:2022), carries an allowed confidence and verification value,
                                and fills its overlay-specific columns

Usage
    python scripts/validate_crosswalk.py        exit code 0 when everything is valid, 1 otherwise

scripts/build_crosswalk.py imports load_all() from this module, so the build refuses to run on invalid data.
No personal data. MIT License.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "crosswalk.csv"
OVERLAY_DIR = ROOT / "data" / "overlays"

# The 93 Annex A controls of ISO/IEC 27001:2022: 5.1-5.37, 6.1-6.8, 7.1-7.14, 8.1-8.34.
ANNEX_A = [f"A.{theme}.{n}" for theme, count in ((5, 37), (6, 8), (7, 14), (8, 34)) for n in range(1, count + 1)]

# ISMS requirement clauses of ISO/IEC 27001:2022 (identifiers only).
ISMS_CLAUSES = {
    "4.1", "4.2", "4.3", "4.4",
    "5.1", "5.2", "5.3",
    "6.1", "6.1.1", "6.1.2", "6.1.3", "6.2", "6.3",
    "7.1", "7.2", "7.3", "7.4", "7.5",
    "8.1", "8.2", "8.3",
    "9.1", "9.2", "9.3",
    "10.1", "10.2",
}

CROSSWALK_COLUMNS = ["domain", "iso27001_2022", "iso27001_title", "nist_csf_2", "cis_v8", "iso42001", "soc2_tsc", "notes"]

OVERLAY_COLUMNS = ["ref", "title", "group", "iso27001_2022", "iso27001_clauses", "confidence", "verification", "notes"]
OVERLAY_REQUIRED = ["ref", "title", "confidence", "verification"]
CONFIDENCE = {"high", "medium"}
VERIFICATION = {
    "verified": "Identifier and title checked against the publisher's own public text.",
    "secondary": "Checked against a published translation or reputable secondary sources; the official text could not be retrieved.",
    "unverified": "Taken from secondary descriptions only; the publisher's text is not publicly available.",
}

# Overlay registry: key -> display metadata and overlay-specific columns (required, non-empty).
# Order here is the order used in every generated output.
OVERLAYS = {
    "uae_iar": {
        "name": "UAE Information Assurance Regulation",
        "edition": "v1.1 (March 2020), TDRA",
        "label": "UAE IAR",
        "granularity": "control sub-family (e.g. T5.2)",
        "extra": ["priority"],
    },
    "desc_isr": {
        "name": "Dubai Information Security Regulation",
        "edition": "ISR version 3 domain structure, DESC",
        "label": "DESC ISR",
        "granularity": "domain",
        "extra": [],
    },
    "uae_pdpl": {
        "name": "UAE Personal Data Protection Law",
        "edition": "Federal Decree-Law No. 45 of 2021",
        "label": "UAE PDPL",
        "granularity": "obligation (with article numbers)",
        "extra": ["articles"],
    },
    "pci_dss_4": {
        "name": "PCI DSS",
        "edition": "v4.0.1 (June 2024), PCI SSC",
        "label": "PCI DSS v4.0.1",
        "granularity": "principal requirement",
        "extra": [],
    },
    "nist_800_53": {
        "name": "NIST SP 800-53",
        "edition": "Rev. 5",
        "label": "NIST SP 800-53 Rev. 5",
        "granularity": "control family",
        "extra": [],
    },
    "iso22301": {
        "name": "ISO 22301",
        "edition": "2019",
        "label": "ISO 22301:2019",
        "granularity": "clause / sub-clause",
        "extra": [],
    },
}


def split_list(cell: str) -> list[str]:
    """'A.5.1; A.5.2' -> ['A.5.1', 'A.5.2']; empty cell -> []."""
    return [p.strip() for p in (cell or "").split(";") if p.strip()]


def load_crosswalk(errors: list[str]) -> list[dict]:
    with SRC.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != CROSSWALK_COLUMNS:
            errors.append(f"{SRC.name}: header must be {CROSSWALK_COLUMNS}, found {reader.fieldnames}")
            return []
        rows = list(reader)
    for r in rows:
        missing = [k for k in CROSSWALK_COLUMNS if not (r.get(k) or "").strip()]
        if missing:
            errors.append(f"{SRC.name}: row {r.get('iso27001_2022')} is missing {missing}")
    ids = [r["iso27001_2022"] for r in rows]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        errors.append(f"{SRC.name}: duplicate ISO 27001 control identifiers {dupes}")
    unknown = [i for i in ids if i not in ANNEX_A]
    if unknown:
        errors.append(f"{SRC.name}: identifiers not in ISO/IEC 27001:2022 Annex A {unknown}")
    absent = [i for i in ANNEX_A if i not in ids]
    if absent:
        errors.append(f"{SRC.name}: Annex A controls missing from the crosswalk {absent}")
    return rows


def load_overlay(key: str, meta: dict, errors: list[str]) -> list[dict]:
    path = OVERLAY_DIR / f"{key}.csv"
    if not path.exists():
        errors.append(f"overlays/{key}.csv: file not found")
        return []
    expected = OVERLAY_COLUMNS[:-1] + meta["extra"] + OVERLAY_COLUMNS[-1:]
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != expected:
            errors.append(f"overlays/{key}.csv: header must be {expected}, found {reader.fieldnames}")
            return []
        rows = list(reader)
    if not rows:
        errors.append(f"overlays/{key}.csv: no rows")
    seen: set[str] = set()
    for n, r in enumerate(rows, start=2):  # line 1 is the header
        where = f"overlays/{key}.csv line {n}"
        for k in expected:
            r[k] = (r.get(k) or "").strip()
        for k in OVERLAY_REQUIRED + meta["extra"]:
            if not r[k]:
                errors.append(f"{where}: empty '{k}'")
        ref = r["ref"]
        if ref:
            if ref in seen:
                errors.append(f"{where}: duplicate overlay identifier '{ref}'")
            seen.add(ref)
        controls = split_list(r["iso27001_2022"])
        clauses = split_list(r["iso27001_clauses"])
        if not controls and not clauses:
            errors.append(f"{where}: '{ref}' maps to no Annex A control and no ISMS clause")
        for c in controls:
            if c not in ANNEX_A:
                errors.append(f"{where}: '{ref}' references '{c}', which is not one of the 93 Annex A controls")
        for c in clauses:
            if c not in ISMS_CLAUSES:
                errors.append(f"{where}: '{ref}' references clause '{c}', which is not an ISO/IEC 27001:2022 clause")
        for label, items in (("Annex A control", controls), ("clause", clauses)):
            dupes = sorted({i for i in items if items.count(i) > 1})
            if dupes:
                errors.append(f"{where}: '{ref}' lists {label}(s) {dupes} more than once")
        if r["confidence"] and r["confidence"] not in CONFIDENCE:
            errors.append(f"{where}: confidence must be one of {sorted(CONFIDENCE)}, found '{r['confidence']}'")
        if r["verification"] and r["verification"] not in VERIFICATION:
            errors.append(f"{where}: verification must be one of {sorted(VERIFICATION)}, found '{r['verification']}'")
    return rows


def load_all() -> tuple[list[dict], dict[str, list[dict]]]:
    """Return (crosswalk rows, {overlay key: rows}) or exit with every validation error listed."""
    errors: list[str] = []
    rows = load_crosswalk(errors)
    overlays = {key: load_overlay(key, meta, errors) for key, meta in OVERLAYS.items()}
    extra_files = sorted(p.stem for p in OVERLAY_DIR.glob("*.csv") if p.stem not in OVERLAYS)
    if extra_files:
        errors.append(f"data/overlays: files not registered in OVERLAYS {extra_files}")
    if errors:
        raise SystemExit("Validation failed:\n  - " + "\n  - ".join(errors))
    return rows, overlays


def main() -> int:
    rows, overlays = load_all()
    print(f"crosswalk.csv: {len(rows)} ISO/IEC 27001:2022 Annex A controls, all present and unique.")
    for key, items in overlays.items():
        print(f"overlays/{key}.csv: {len(items)} rows valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
