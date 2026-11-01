# Limitations

Read these before using the crosswalk or its overlays for planning, an assessment or a client deliverable.

## About the sources

* **Editions are fixed.** Each overlay uses one edition, named in [sources.md](sources.md) with the access date
  (2026-11-01). A later edition of a regulation or standard may renumber, merge or add items. The overlays are
  not updated automatically.
* **UAE IAR v1.1 (March 2020)** is the edition mapped. Whether a newer edition exists, and how the IAR relates to
  the earlier NESA *UAE Information Assurance Standards*, is **not verified** here.
* **DESC ISR titles are unverified.** DESC provides the ISR text on email request only; domain titles come from
  secondary sources.
* **UAE PDPL Executive Regulations:** their publication status was unclear on the access date. Deadlines that
  the law delegates to them (for example breach notification periods) are deliberately left out.
* Only identifiers and short titles were taken from the sources. Requirements must be read in the official text.

## About the mappings

* **Expert judgement, not equivalence.** Every mapping is the maintainer's reading of objectives. A `high` rating
  means the same objective and a similar scope, not identical requirements.
* **Granularity is coarse on purpose.** The IAR is mapped at sub-family level (66 rows), not at control level
  (188 controls). Control-level gaps inside a sub-family are not visible.
* **One direction.** Overlays point to ISO 27001. They do not say whether an IAR sub-family is fully satisfied
  by the ISO controls listed; a `medium` row says something is missing, a `high` row can still need
  UAE-specific evidence (applicability rules, regulator reporting, priorities).
* **Target frameworks** (NIST CSF 2.0, CIS v8, ISO 42001, SOC 2) hold the single closest match per ISO control.
  Real relationships are many-to-many.

## About applicability

* The crosswalk does not decide whether a regulation applies to an organisation. IAR applicability, free-zone
  data regimes (DIFC, ADGM) and sector regulators must be confirmed with legal counsel or the regulator.

## About quality assurance

* Automated checks (`scripts/validate_crosswalk.py`, `tests/`) prove structure and consistency: valid
  identifiers, no duplicates, a rationale on every partial match, figures in the worked example that match the
  data. They do not prove that a mapping is correct.
* An independent review is tracked in [review.md](review.md). Until it is recorded there, treat the overlays as a
  maintainer draft.

## About the worked example

* [`examples/uae-iar-gap-assessment-contoso-logistics.md`](../examples/uae-iar-gap-assessment-contoso-logistics.md)
  is **fictional**: the organisation, findings and ratings are invented to show the method.
