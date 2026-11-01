# Mapping rationale

How each overlay row was mapped to ISO/IEC 27001:2022, and how to read the result. The rules below apply to every
overlay in `data/overlays/`; the per-row reasoning is in the `notes` column.

## Unit of mapping

| Overlay | Unit | Example |
|---------|------|---------|
| UAE IAR v1.1 (TDRA) | control **sub-family** | `T5.2` User Access Management |
| DESC ISR | **domain** | `Domain 5` Access Control |
| UAE PDPL | **obligation**, with article numbers | `PDPL-08` |
| PCI DSS v4.0.1 | **principal requirement** | `Req. 8` |
| NIST SP 800-53 Rev. 5 | control **family** | `AC` |
| ISO 22301:2019 | clause or sub-clause | `8.4.3` |

Each row lists the ISO/IEC 27001:2022 **Annex A controls** that pursue the same objective and, where the overlay
item is about the management system rather than a control, the **ISMS clauses** (4 to 10). Sub-family level is a
deliberate choice for the IAR: Annex B of the regulation gives 188 controls, and a control-level mapping would
claim a precision that a title-based reading cannot support.

## Steps followed for each row

1. Read the identifier and title in the source named in [sources.md](sources.md) (never the full text into the
   repository: identifiers and short titles only).
2. State the objective of the item in one line: what it is meant to achieve.
3. List the Annex A controls whose purpose falls inside that objective; add ISMS clauses when the item concerns
   the management system (context, leadership, risk process, performance evaluation).
4. Rate the match:
   * **high**: the ISO controls listed achieve the same objective with a similar scope;
   * **medium**: partial overlap, or the overlay item adds a requirement ISO 27001 does not have. A medium row
     **must** carry a note saying what is missing or different (enforced by `tests/test_overlays.py`).
5. Record the source status in `verification` (`verified`, `secondary`, `unverified`), defined in
   [sources.md](sources.md).
6. For the IAR, record in `priority` every P1 to P4 level found among the sub-family's controls in Annex B.

## Recurring patterns

| Pattern | Rating | Why |
|---------|--------|-----|
| A family-level policy (`M5.1`, `T1.1`, `T2.1`, `T3.1`, `T4.1`, `T7.1`, `T9.1`) | medium | ISO 27001 expects topic-specific policies under A.5.1 but no separate policy per topic; the IAR asks for one per family. |
| Risk sub-families (`M2.2` to `M2.4`) and performance review (`M6.3`) | high, clauses only | They describe the ISMS risk process and review, which ISO 27001 places in clauses 6.1, 8.2, 8.3 and 9.3, not in Annex A. |
| An item that names a UAE body or duty (information sharing, regulator reporting) | medium | ISO 27001 covers the internal process (for example A.5.5, A.5.24) but not the external obligation. |
| DESC ISR domains | medium where the scope could differ | The ISR text is provided on request only; the mapping relies on domain titles (see sources). |

## What the mapping is not

* Not an official mapping by TDRA, DESC, the UAE Data Office, the PCI SSC, NIST or ISO.
* Not a statement that implementing the listed ISO controls makes an entity compliant: see
  [limitations.md](limitations.md).
* Not legal advice on whether a regulation applies to an organisation.

## Changing a mapping

Edit the row in `data/overlays/<overlay>.csv`, explain the change in `notes`, run
`python scripts/validate_crosswalk.py`, `pytest` and `python scripts/build_crosswalk.py`, and record the change
in the "Source and mapping changes" section of [sources.md](sources.md) and in the changelog.
