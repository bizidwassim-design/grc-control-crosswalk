# Sample gap assessment: Contoso Logistics FZ-LLC against the UAE IA Regulation

> **Fictional example.** Contoso Logistics FZ-LLC, its people, systems and findings are invented to show the
> method. Any resemblance to a real organisation is coincidental. This is not legal advice and not an official
> TDRA assessment format.

It uses the [UAE IAR overlay](../data/by-framework/uae_iar.csv) of this repository (TDRA UAE IA Regulation v1.1)
and the ISO 27001 → IAR view in [`data/iso27001-overlays.csv`](../data/iso27001-overlays.csv). See also the
[UAE readiness summary](../docs/uae-readiness.md).

## Scenario

| Item | Fictional data |
|------|----------------|
| Organisation | Contoso Logistics FZ-LLC: freight forwarding and three warehouses, about 350 staff, head office in a UAE free zone |
| Current certification | ISO/IEC 27001:2022, scope: IT operations, the warehouse management system (WMS) and the customer portal |
| Trigger | A federal government customer requires alignment with the UAE IA Regulation within 12 months. Management also wants to be ready in case the company is designated a critical entity in the transport sector. |
| Method | Document review and interviews per IAR family. Each of the 66 sub-families in the overlay was rated *Met*, *Partial* or *Gap*. Priorities are the IAR Annex B priorities of the controls concerned. |

## Findings by family

| Family | Current state | Gap | IAR priority | Owner role | Remediation | ISO 27001 already in place |
|--------|---------------|-----|:-----------:|------------|-------------|----------------------------|
| M1 Strategy and Planning | ISMS scope, policy and roles approved by the board | No security sign-off before new systems go live (M1.3); no standard security terms for customers | P2 | CISO | Add a security approval gate to the project and change process; add a customer security clause | Clauses 4–5, A.5.1, A.5.2, A.5.8, A.5.20 |
| M2 Risk Management | ISO risk method, risk register and SoA | SoA has no IAR column; the 34 "Always Applicable" controls are not tracked; exclusions lack recorded risk acceptance | P1 | GRC manager | Extend the SoA into an IAR applicability matrix; flag Always Applicable controls; record risk acceptance for every exclusion | Clauses 6.1.2, 6.1.3, 8.2, 8.3: method reused unchanged |
| M3 Awareness and Training | Annual e-learning and quarterly phishing simulations | No role-based training needs analysis (M3.3); results not recorded per person | P1 | HR learning lead with CISO | Role-based training needs analysis; keep completion and results records | A.6.3 |
| M4 Human Resources Security | Screening, NDAs and leaver process in place | Contractor leaver evidence is held by the staffing agency | P1 | HR manager | Bring contractor offboarding into the identity workflow | A.6.1, A.6.2, A.6.5, A.5.11, A.5.18 |
| M5 Compliance | Legal register maintained by Legal | Register lacks the IAR, the PDPL applicability decision and cryptography rules (M5.2) | P2 | Legal counsel with GRC manager | Update the register and record the PDPL / free-zone regime decision | A.5.31, A.5.34, A.5.36 |
| M6 Performance Evaluation and Improvement | ISMS KPIs, internal audit and management review | No performance evaluation policy (M6.1); KPIs not linked to IAR controls | P3 | GRC manager | Short policy; add IAR metrics to the KPI set | Clauses 9.1–10.2 |
| T1 Asset Management | Asset inventory and classification scheme | USB storage open on warehouse PCs (T1.4); BYOD use not documented (T1.2) | P1 | IT operations manager | Block removable storage by default with an exception process; publish a BYOD standard | A.5.9, A.5.10, A.5.12, A.7.10 |
| T2 Physical and Environmental Security | Badge access at head office and the server room | Warehouse communications rooms have no access logs (T2.2); racks next to the loading area | P2 | Facilities manager | Install logged badge readers; relocate or enclose racks | A.7.1–A.7.4 |
| T3 Operations Management | EDR on all endpoints, daily backups, SIEM for servers | Restore tests not documented (T3.5); WMS logs not in the SIEM (T3.6) | P1 | IT operations manager and SOC lead | Quarterly restore test with records; onboard WMS logs and alerts | A.8.7, A.8.13, A.8.15, A.8.16 |
| T4 Communications | Segmented network and managed firewalls | Guest Wi-Fi shares a segment with handheld scanners (T4.5); no link to sector information sharing (T4.4) | P2 | Network lead | Separate wireless networks; join the sector information-sharing channel when invited | A.8.20–A.8.22 |
| T5 Access Control | Single sign-on with MFA for cloud apps; quarterly reviews for finance | WMS and privileged accounts not reviewed (T5.2); shared admin account on warehouse controllers (T5.5) | P1 | IAM lead | Extend access reviews; individual admin accounts with a password vault | A.5.15–A.5.18, A.8.2, A.8.5 |
| T6 Third-Party Security | Supplier questionnaire; cloud provider assessed at onboarding | No periodic service-delivery review (T6.2); cloud agreements lack a data location clause (T6.3) | P2 | Procurement lead with GRC manager | Annual supplier reviews; contract addendum on data location | A.5.19–A.5.23 |
| T7 Acquisition, Development and Maintenance | Vendor-built WMS; monthly vulnerability scans | Patch backlog on warehouse controllers (T7.7); no supply-chain protection strategy (T7.8) | P1 | Head of applications | Patch plan with compensating controls; short supply-chain strategy | A.8.8, A.8.25–A.8.30, A.5.21 |
| T8 Incident Management | Incident response plan; external incident-response retainer | No external reporting matrix for authorities; incident classification not aligned to the regulator's scheme (T8.2); no situational-awareness feed (T8.3) | P2–P4 | SOC lead | Add an external reporting matrix and templates; run a tabletop exercise that includes regulator notification | A.5.24–A.5.28, A.6.8 |
| T9 Information Systems Continuity | Business continuity plan for head office; DR site for ERP | No continuity plan for the WMS (T9.2); plans not tested (T9.3) | P3 | Business continuity manager | WMS continuity plan and an annual test | A.5.29, A.5.30, A.8.14 (see the ISO 22301 overlay) |

## Roadmap

| Wave | Window | Scope |
|------|--------|-------|
| 1 | Months 0–3 | All P1 findings: applicability matrix and risk acceptance (M2), training needs (M3), contractor offboarding (M4), removable media (T1), restore tests and WMS logging (T3), access reviews and shared admin accounts (T5), patch plan (T7) |
| 2 | Months 3–6 | P2 findings: system sign-off gate (M1), legal register (M5), physical access logging (T2), wireless separation (T4), supplier reviews and cloud clauses (T6), external incident reporting (T8) |
| 3 | Months 6–12 | P3 and P4 findings: performance evaluation policy (M6), WMS continuity plan and test (T9), supply-chain strategy (T7.8), information sharing and situational awareness (T4.4, T8.3), then an internal IAR audit |

## How ISO 27001 reduced the effort

* **Rating result (fictional):** of the 66 IAR sub-families, 41 were *Met* using existing ISO 27001 evidence,
  18 were *Partial* and 7 were *Gap*. In the overlay, 43 sub-families map to ISO 27001 with `high` confidence;
  most *Met* ratings came from that group.
* **No second risk method.** The IAR risk sub-families (M2.1–M2.4) map to ISO 27001 clauses 6.1 and 8.2–8.3. The
  existing method and register were kept, and only an IAR column and risk-acceptance records were added.
* **One evidence library.** The `iso27001-overlays.csv` view lists, for each Annex A control, the IAR
  sub-families it supports. Evidence for A.8.15/A.8.16 (logging and monitoring), for example, was tagged once
  and reused for T3.6, DESC ISR Domain 6 and PCI DSS Requirement 10.
* **Effort went to the real differences:** applicability rules (Always Applicable controls), granularity
  (family policies, sub-control evidence) and UAE-specific external duties (information sharing, regulator
  reporting).

*Fictional data for illustration only. Check the current IAR version and its applicability to your organisation
with the regulator before planning real work.*
