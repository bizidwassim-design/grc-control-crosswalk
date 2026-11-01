# UAE readiness: what an ISO 27001 organisation still has to add

A one-page summary for organisations that already run an ISO/IEC 27001:2022 ISMS and now face UAE or
payment-sector requirements. The detail is in the overlay data (`data/overlays/*.csv`, generated views in
`data/by-framework/` and the `ov_*` sheets of the workbook). The sources and verification status are in
[sources.md](sources.md). A worked, fictional example is in
[examples/uae-iar-gap-assessment-contoso-logistics.md](../examples/uae-iar-gap-assessment-contoso-logistics.md).

## Overlays in this repository

| Overlay | Edition used | Rows | Granularity | Verification |
|---------|--------------|-----:|-------------|--------------|
| UAE Information Assurance Regulation (TDRA) | v1.1, March 2020 | 66 | sub-family (M1.1 … T9.3), with P1–P4 priorities | verified |
| Dubai Information Security Regulation (DESC) | ISR version 3 domain structure | 13 | domain | unverified (text on request only) |
| UAE PDPL (Federal Decree-Law No. 45 of 2021) | as enacted | 12 | obligation, with article numbers | secondary |
| PCI DSS | v4.0.1, June 2024 | 12 | principal requirement | verified |
| NIST SP 800-53 | Rev. 5 | 20 | control family | verified |
| ISO 22301 | 2019 | 17 | clause / sub-clause | verified |

In the UAE IAR overlay, 43 of the 66 sub-families map to ISO 27001 with `high` confidence. Every Annex A control
except A.5.8, A.7.4, A.8.10, A.8.11 and A.8.23 is referenced by at least one IAR sub-family. A working ISMS covers
most of the IAR catalogue. The extra effort lies in the points below.

## What to add, by framework

**UAE IAR (TDRA)**
* Confirm applicability. The regulation is mandatory for UAE government entities and entities designated as
  critical; TDRA recommends it to everyone else.
* Build an IAR applicability matrix next to the Statement of Applicability. The 34 "Always Applicable" management
  controls, and every one of their sub-controls, cannot be omitted. Excluding any other control, or deviating
  from one of its sub-controls, needs a justification and documented risk acceptance. Without an entity risk
  assessment, every control counts as applicable.
* Plan in priority order (P1 → P4). P1 controls may be strengthened but never demoted.
* Add what ISO 27001 does not ask for: a policy control in every family, sector and national
  information-sharing (T4.4, M5.2, M5.5), situational-awareness reporting (T8.3) and more prescriptive
  supply-chain controls (T7.8).

**DESC ISR (Dubai government entities and their suppliers)**
* Obtain the current ISR text from DESC first. It is provided on request, and the domain titles in this repository
  are `unverified`.
* Expect the version 3 changes reported in public sources: a UAE National heading the information security
  function, named roles (security champions, internal auditors, incident response team), problem management,
  data-centre controls, cyber resilience in continuity planning, minimum requirements for external parties and
  managed services, and no storage or processing of critical information outside the UAE.

**PCI DSS v4.0.1 (anyone storing, processing or transmitting card data)**
* Scope the cardholder data environment and prove segmentation. PCI scope is set by data flows, not by the
  ISMS scope statement.
* Replace "risk-based" with "prescribed" where PCI says so: MFA into the CDE, defined log retention, and scanning
  and penetration testing at fixed intervals. Keep targeted risk analyses for requirements that allow a flexible
  frequency.
* Map evidence to the assessment route your acquirer or brand requires (report on compliance or self-assessment
  questionnaire).

**UAE PDPL (federal mainland and free zones without their own data protection law)**
* Decide which regime applies. DIFC (DIFC Law No. 5 of 2020) and ADGM (Data Protection Regulations 2021) have
  their own laws, and some sectors (for example health and credit data) have specific laws.
* Add the privacy operating model that A.5.34 alone rarely delivers: lawful basis and consent records, a
  record of processing for controller and processor, data subject request handling, DPIA before high-risk
  processing, DPO appointment where triggered, breach notification to the regulator and data subjects, and a
  cross-border transfer assessment.
* **Enforcement detail depends on the Executive Regulations.** Their publication status was unclear at the time
  of writing. Check the current status before setting deadlines.

## Top 5 typical gaps for an ISO 27001-certified organisation

1. **Exclusions that the regulation does not allow.** ISO lets you exclude Annex A controls with justification.
   IAR "Always Applicable" controls cannot be excluded, and every other exclusion or sub-control deviation needs
   recorded risk acceptance by an accountable person.
2. **Granularity of evidence.** One consolidated ISMS policy set does not show family-level policies and
   sub-control evidence (IAR, DESC ISR) or requirement-level evidence (PCI DSS).
3. **Data location.** Cloud inventories that do not record hosting region cannot answer DESC version 3 data
   residency or PDPL cross-border questions (A.5.23 and A.5.14 need a location field).
4. **Privacy operations.** Records of processing, data subject requests, DPIAs and regulator breach notification
   are missing or informal. A.5.34 is usually a policy, not a process.
5. **External reporting and information sharing.** Incident processes stop at internal escalation. Regulators,
   sector CERTs and information-sharing platforms (IAR T4.4 and T8.3, PDPL Art. 9) need named contacts,
   templates and tested timelines (A.5.5, A.5.24–A.5.26).

## Disclaimer

The overlays are informative expert-judgement mappings for planning and gap analysis. They are **not legal
advice**, not an official mapping by TDRA, DESC, the UAE Data Office, the PCI SSC, NIST or ISO, and not a
substitute for the current official texts. Identifiers and short titles only are used; no standard or regulation
text is reproduced. Regulations change: check the current version and status of each one (in particular the PDPL
Executive Regulations and the DESC ISR version in force) before relying on this page.
