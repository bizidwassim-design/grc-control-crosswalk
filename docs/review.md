# Independent review

An independent review is a check of the overlays by someone other than the maintainer, against the official
texts. It is the step that turns the overlays from a maintainer draft into a reviewed reference.

## Status

| Overlay | Edition | Rows | Reviewer | Date | Result |
|---------|---------|-----:|----------|------|--------|
| UAE IAR | v1.1, March 2020 (TDRA) | 66 | **not yet reviewed** | — | — |
| DESC ISR | version 3 domain structure | 13 | not yet reviewed | — | — |
| UAE PDPL | Federal Decree-Law No. 45 of 2021 | 12 | not yet reviewed | — | — |
| PCI DSS | v4.0.1 | 12 | not yet reviewed | — | — |
| NIST SP 800-53 | Rev. 5 | 20 | not yet reviewed | — | — |
| ISO 22301 | 2019 | 17 | not yet reviewed | — | — |

No overlay has been independently reviewed yet. This page will name the reviewer, the date, the scope and the
outcome when one is done. Nothing here should be read as a review that has not happened.

## What a reviewer checks

For a sample, or for every row of an overlay:

1. **Identifier and title** match the official text of the edition named in [sources.md](sources.md).
2. **Objective**: the ISO/IEC 27001:2022 controls and clauses listed pursue the same objective.
3. **Rating**: `high` versus `medium` is justified; every `medium` row has a note that says what differs.
4. **Missing mappings**: an ISO control that obviously supports the item and is not listed.
5. **Priority** (IAR only): the P1 to P4 levels match Annex B for the sub-family's controls.
6. **Limitations**: anything the reviewer believes users must be told, added to [limitations.md](limitations.md).

## How to record a review

1. Open an issue titled `Review: <overlay> <edition>` with your name or handle, your relevant qualification or
   experience, the rows checked and the official copy used (edition and date).
2. Record each disagreement as one line: row, current mapping, proposed mapping, reason.
3. The maintainer applies or answers each line, updates the CSV and the notes, and records the result in the
   status table above and in the "Source and mapping changes" section of [sources.md](sources.md).

Reviewers are credited by name in this table unless they prefer not to be.
