# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- The coverage view is now labelled *Annex A mapping coverage* and explains that each bar counts the 93 Annex A controls with at least one mapping, not compliance with the target framework.

### Added
- `docs/mapping-rationale.md`, `docs/limitations.md` and `docs/review.md` (independent review status: none recorded yet).
- "Source and mapping changes" log in `docs/sources.md`, with the open source questions to re-check at each update.
- `tests/test_overlays.py`, run in CI with `pytest`: rationale required on every `medium` row, UAE IAR structure and priorities, worked-example figures checked against the overlay, sources and review pages complete.
- The worked example is dated (fictional assessment period and report date) and names the data version it uses.

### Changed
- Rationale added to 16 `medium` rows that had none (8 UAE IAR, 4 DESC ISR, 4 ISO 22301). No identifier, mapping or rating changed.

### Added (web explorer)
- Web explorer (`index.html`, `assets/`, `data/crosswalk.js`): search and filter the 93 controls, show or hide framework and overlay columns, start from any framework or overlay identifier, overlay tables with confidence and verification, coverage view, CSV export, light and dark themes, strict CSP. Hosted on GitHub Pages.
- `scripts/build_web_data.py` generates `data/crosswalk.js` from the validated sources; CI checks it is current, syntax-checks the app and validates the HTML.

## [1.1.0] — 2026-11-01

### Added
- UAE and sector overlays in `data/overlays/`, each row keyed to ISO/IEC 27001:2022 Annex A controls and ISMS
  clauses, with `confidence` (high/medium) and `verification` (verified/secondary/unverified) columns:
  - UAE Information Assurance Regulation v1.1 (TDRA): 66 sub-families, M1–M6 and T1–T9, with P1–P4 priorities.
  - Dubai Information Security Regulation (DESC), ISR version 3 domain structure: 13 domains (unverified titles).
  - UAE PDPL (Federal Decree-Law No. 45 of 2021): 12 obligations with article numbers.
  - PCI DSS v4.0.1: the 12 principal requirements.
  - NIST SP 800-53 Rev. 5: the 20 control families.
  - ISO 22301:2019: 17 clauses and sub-clauses relevant to Annex A 5.29, 5.30, 8.13 and 8.14.
- Generated outputs for the overlays: `data/by-framework/<overlay>.csv`, `data/iso27001-overlays.csv`, an
  `overlays` block per control and a top-level `overlays` section in `data/crosswalk.yaml`, and the
  `02_ISO_to_overlays` and `ov_*` workbook sheets.
- `scripts/validate_crosswalk.py`, run in CI. It fails on unknown Annex A IDs or ISMS clauses, on duplicate or
  empty overlay identifiers, and on a crosswalk that is not exactly the 93 Annex A controls.
- `docs/sources.md` (sources, URLs and access dates), `docs/uae-readiness.md` (one-page UAE readiness summary) and
  `examples/uae-iar-gap-assessment-contoso-logistics.md` (fictional sample gap assessment).
- `SECURITY.md` with a private vulnerability-reporting process and the project's security commitments.
- Continuous integration on every push and pull request (see `.github/workflows/`).
- Dependabot for GitHub Actions versions.
- This changelog.

### Changed
- `data/crosswalk.yaml` version 1.1. The existing `maps_to` keys are unchanged, so existing consumers keep working.
- The workbook is now written with fixed timestamps, so rebuilding unchanged data gives an identical file.
- CI also fails if the build creates generated files that are not committed.

## [1.0.0] — 2026-10-31

### Added
- Initial public release.
