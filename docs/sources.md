# Sources for the UAE and sector overlays

All sources were accessed on **2026-11-01**. Only identifiers and short titles were taken from them. No
standard or regulation text is reproduced in this repository.

Each overlay row has a `verification` value:

| Value | Meaning |
|-------|---------|
| `verified` | Identifier and title checked against the publisher's own public text. |
| `secondary` | Checked against a published translation or reputable secondary sources, because the official text could not be retrieved. |
| `unverified` | Taken from secondary descriptions only, because the publisher does not make the text publicly available. |

The mappings to ISO/IEC 27001:2022 are the maintainer's own expert judgement in every case. They are not
taken from any source below. See the `confidence` column (`high` / `medium`).

## UAE Information Assurance Regulation (IAR), TDRA (`uae_iar`, verified)

| Source | Used for |
|--------|----------|
| TDRA, *UAE Information Assurance Regulation*, Version 1.1, March 2020. <https://tdra.gov.ae/-/media/About/regulations-and-ruling/EN/UAE-Information-Assurance-Regulation-v1-1-pdf.ashx> | Family names M1–M6 and T1–T9, sub-family identifiers and titles (Chapter 5), the P1–P4 prioritisation concept (section 3.4), "Always Applicable" controls (Annex A) and the priority of each control (Annex B: 39 P1, 69 P2, 35 P3 and 45 P4, 188 controls in total). |
| Same document as listed in search results at `government.ae/-/media/guidelines/Guidelines-2020/UAE-IA-Regulation-v11-1.pdf` | Not retrieved: the host's TLS certificate did not match on the access date. The TDRA copy above was used. |

How the priority column was built: Annex B gives one priority per control (for example T5.2.1). The overlay
works at sub-family level (for example T5.2), so its `priority` column lists every priority level found among
that sub-family's controls. Section 3.4 states that entities start with P1 controls and may re-prioritise
after risk assessment, except that P1 controls may not be demoted.

**Unverified:** that the IAR is the successor of the earlier NESA *UAE Information Assurance Standards*. That
lineage is widely reported, but the TDRA v1.1 text does not mention it. The text names the
TRA (now TDRA) as issuer and says it was built on ISO/IEC 27001/27002:2005, NIST SP 800-53 Rev. 4, ADSIC
standards and the SANS 20 controls.

## Dubai Information Security Regulation (ISR), DESC (`desc_isr`, unverified)

| Source | Used for |
|--------|----------|
| DESC, *Standards & Policies*. <https://www.desc.gov.ae/regulations/standards-policies/> | Confirms that the ISR is a DESC standard issued under Executive Council Resolution No. 13 of 2012. The document is provided **on email request only**, so the official domain list could not be checked. |
| News report, "DESC to launch Information Security Regulation Version 3.0", 1 August 2023. <https://www.gdnonline.com/Details/1287749/DESC-to-launch-Information-Security-Regulation-Version-30-> | Version 3 has 13 domains in three classes (Governance, Operation, Assurance). Reported version 3 changes used in the notes: UAE National heading the security function, problem management, data-centre controls, a cyber-resilience requirement, and no storage of critical information outside the UAE. |
| Vendor compliance guide for the Dubai Government ISR (refers to ISR version 3.1). <https://www.kiteworks.com/sites/default/files/resources/kiteworks-compliance-guide-dubai-government-isr.pdf> | Domain numbers and titles 1–8 and 11–13. |
| Coverage of the first ISR (12 domains, 2013), reproduced at <https://thecre.com/fnews/?p=7182> | Titles of domains 9 (Environmental and Physical Security) and 10 (Human Resource Security), which keep the same numbering. Also the earlier title "Performance Measurement" for domain 12. |
| Press release on ISR version 2.0 (2017). <https://www.zawya.com/en/press-release/dubai-electronic-security-center-highlights-the-key-changes-of-information-security-regulation-isr-rhnaloru> | Version 2 moved to 13 domains and added cloud security. |

Version used: the **ISR version 3 domain structure** (13 domains). The domain titles could not be checked
against DESC's own text, so every row is marked `unverified`. The class of each domain (Governance,
Operation or Assurance) is left out because no source reliably assigns domains to classes. One vendor
page gives a different 13-domain list (with separate Cryptography, Operations Security and Third-party domains
and no Cloud Security domain). It conflicts with the sources above and was **not used**.

## UAE Personal Data Protection Law (PDPL) (`uae_pdpl`, secondary)

| Source | Used for |
|--------|----------|
| Official text: <https://uaelegislation.gov.ae/en/legislations/1972> | Not retrievable: the site blocked automated access on the access date. |
| Unofficial bilingual (English/Japanese) translation of Federal Decree-Law No. 45 of 2021, hosted at <https://protection-data.ae/wp-content/uploads/2023/10/federal-decret-law-45-uae.pdf> | Article numbers and headings 1–31. Record-keeping duties in Art. 7 (item 4) and Art. 8 (item 7). The free-zone exclusion in Art. 2. Executive Regulations in Art. 28. The six-month regularisation period after the Executive Regulations in Art. 29. |
| U.S. International Trade Administration, "United Arab Emirates allows cross-border data flows of personal data", 22 January 2024. <https://www.trade.gov/market-intelligence/united-arab-emirates-allows-cross-border-data-flows-personal-data> | Independent cross-check of Art. 22 and Art. 23 (cross-border transfers). |
| u.ae, *Data protection laws*. <https://u.ae/en/about-the-uae/digital-uae/data/data-protection-laws> | The PDPL came into force on 2 January 2022. The UAE Data Office is the federal regulator (Federal Decree-Law No. 44 of 2021). The DIFC regime is DIFC Law No. 5 of 2020. |
| ADGM, "ADGM enacts its new Data Protection Regulations 2021". <https://www.adgm.com/media/announcements/adgm-enacts-its-new-data-protection-regulations-2021> | The ADGM regime is the ADGM Data Protection Regulations 2021. |

**Status of the Executive Regulations: unverified.** On the access date, several 2026 secondary sources
said they had still not been published, and one said they had. None of them cited the Official Gazette.
Reports from 2026 also describe changes to the federal data regulator's structure; these were not verified.
**Check the current status before relying on this overlay.** Specific deadlines (for example a breach-notification
period) are deliberately left out because the law delegates them to the Executive Regulations.

## PCI DSS v4.0.1 (`pci_dss_4`, verified)

| Source | Used for |
|--------|----------|
| PCI Security Standards Council, *Payment Card Industry Data Security Standard: Requirements and Testing Procedures*, v4.0.1, June 2024, Table 1 "Principal PCI DSS Requirements". Official library: <https://www.pcisecuritystandards.org/document_library/>. The copy read was a university-hosted copy of the SSC document at <https://www.middlebury.edu/sites/default/files/2025-01/PCI-DSS-v4_0_1.pdf> | The 12 principal requirement titles and the six goals used in the `group` column. |

## NIST SP 800-53 Rev. 5 (`nist_800_53`, verified)

| Source | Used for |
|--------|----------|
| NIST CSRC, *SP 800-53 Rev. 5, Security and Privacy Controls for Information Systems and Organizations*. <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final> | The 20 control family names. The page also notes release 5.2.0 (27 August 2025) with new and revised controls; check it for control-level changes. |
| NIST SP 800-53 Rev. 5, Table 1 "Security and privacy control families". <https://doi.org/10.6028/NIST.SP.800-53r5> | The two-letter family identifiers (AC … SR). |

## ISO 22301:2019 (`iso22301`, verified)

| Source | Used for |
|--------|----------|
| DIN (German standards body), published table of contents of ISO 22301:2019-10 (E). <https://www.din.de/de/mitwirken/normenausschuesse/naorg/veroeffentlichungen/wdc-beuth:din21:316071769/toc-3122157/download> | Clause and sub-clause numbers and titles (clauses 4–10, including 8.2.2–8.6). |

## ISO/IEC 27001:2022 clause identifiers

The `iso27001_clauses` column uses ISO/IEC 27001:2022 requirement clause numbers only (4.1–10.2). Note that the
2022 edition places continual improvement in 10.1 and nonconformity and corrective action in 10.2. The list
of allowed clause identifiers is in `scripts/validate_crosswalk.py`.
