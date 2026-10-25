# Requirements-to-feature matrix

Source: *Sports Fund–SHA Digital Beneficiary Management and Universal Health Coverage Integration Initiative* (concept note, "Preliminary concept for discussion").

**Category key**

| Code | Meaning |
|---|---|
| **S** | **Stated** in the concept note |
| **R** | **Recommended** design choice added to make the demo usable (not in the note) |
| **Q** | Needs **institutional clarification or agreement** before any real system |

**Milestone key:** M1 foundation · M2 beneficiary register · M3 coordination · M4 monitoring & finance · M5 reports, users & activity log · M6 testing, polish & presentation · Doc = covered in documentation / presentation, not as software.

## A. Purpose, vision and objectives

| # | Concept-note point (section) | Cat. | Demo feature | How it is demonstrated | Milestone | Open question |
|---|---|---|---|---|---|---|
| 1 | Move from fragmented beneficiary administration to a coordinated, measurable, accountable system (§2 central proposition) | S | Whole application | Presentation walkthrough follows one beneficiary from registration to coverage check, case and dashboard | M6 | — |
| 2 | Problems: delays confirming eligibility, hard to find who needs enrolment help, repeated work, poor visibility of reach and outstanding cases, weak link between spending and outcomes, slow reports (§2) | S | Each problem mapped to a module (register, coverage, cases, dashboard, finance, reports) | Walkthrough script names the problem each screen addresses | M6 / Doc | — |
| 3 | Vision and mission (§3.1–3.2) | S | Landing page text | Shown on the landing page and presentation notes | M1 / Doc | — |
| 4 | Objective 1: coordinated beneficiary registry (§3.3) | S | Beneficiary list, search, filters, register, edit, profile | Workflow A | M2 | Official data fields and eligibility rules (Q1, Q2) |
| 5 | Objective 2: facilitate authorised coverage verification and identify outstanding coverage needs (§3.3) | S | **Simulated** coverage check through a replaceable adapter; "needs action" list | Workflow B | M3 | Whether SHA would permit any integration, and how (Q8–Q12) |
| 6 | Objective 3: coordinated registration, follow-up, case management, reporting (§3.3) | S | Follow-up cases with history; reports | Workflows C and E | M3 / M5 | Official case categories and service levels (Q14) |
| 7 | Objective 4: visibility of expenditure, reach and delivery progress (§3.3) | S | Finance module linked to programmes; programme summaries | Workflow F | M4 | Real financial structure and approval rules (Q16) |
| 8 | Objective 5: collaboration framework with SHA and sports stakeholders (§3.3, §11) | S | Not software — partnership areas included in presentation material | Presentation | Doc | Governance structure (Q20) |

## B. Functional scope (§4)

| # | Concept-note point | Cat. | Demo feature | How it is demonstrated | Milestone | Open question |
|---|---|---|---|---|---|---|
| 9 | Beneficiary management: centralised registration and management | S | Beneficiary register | Workflow A | M2 | Q1, Q2 |
| 10 | Coverage coordination: authorised verification + outstanding cases | S | Simulated check, every result labelled "Simulated — not verified by SHA"; DB refuses non-simulated rows | Workflow B | M3 (DB rule already in M1) | Q8–Q12 |
| 11 | Enrolment support: coordinated follow-up | S | Case category "Enrolment support", assignment, due dates, notes, statuses | Workflow C | M3 | Q14 |
| 12 | Programme monitoring: reach, coverage progress, activities | S | Programme list and detail pages | Workflow D | M4 | — |
| 13 | Management reporting: dashboards and periodic reports | S | Dashboard + reports with date/category filters + CSV export | Workflow E | M4 / M5 | Which reports management actually needs (Q17) |
| 14 | Financial accountability: expenditure vs beneficiaries and delivery | S | Allocations, expenditure, "linked activity" field, completeness checks | Workflow F | M4 | Q16 |
| 15 | Referral coordination: guidance on accredited facilities, subject to SHA entitlements | S | **Simulated** referral/guidance records with fictional facilities | Profile + referrals page | M3 | Source of an approved facility list (Q13) |
| 16 | Institutional oversight: role-based access, controlled exchange, auditable activity | S | 5 proposed roles, server-side checks, activity log | Sign in as different roles; activity log page | M1 (roles) / M5 (log page) | Real users and permissions (Q5) |
| 17 | Final scope agreed through consultation; technical specs and integration addressed separately | S | Demo labelled throughout as a proposal | Banner on every page | M1 | — |

## C. Beneficiaries and stakeholders (§5)

| # | Concept-note point | Cat. | Demo feature | How it is demonstrated | Milestone | Open question |
|---|---|---|---|---|---|---|
| 18 | Five beneficiary groups: sportspersons & athletes; coaches & technical personnel; officials & sports administrators; women & emerging athletes; other eligible & vulnerable groups | S | `category` field with exactly these five groups | Home page breakdown (M1), filters (M2) | M1 / M2 | Eligibility criteria per group (Q1) |
| 19 | Professional and developing athletes across disciplines | S | `discipline` field | Filters and reports | M2 | Official discipline list (Q2) |
| 20 | Sports federations: identification and validation where formally authorised | S | Status "Pending validation" → "Registered", with fictional "validated by" federation | Profile | M2 | Whether federations would use the system directly (Q6) |
| 21 | County and programme stakeholders: outreach support | S | County field and county breakdowns | Reports | M2 / M5 | County roles (Q6) |
| 22 | Beneficiaries take part in registration, consent and follow-up | S | `consent_recorded` + date on each record | Profile; consent case category | M2 | Consent model and privacy notice (Q18) |
| 23 | Federation and county user accounts | R | **Not built** — demo has staff roles only | Listed as future work | Doc | Q6 |
| 24 | Beneficiary self-service ("clearer information about their status", §6.3) | S | **Not built** in the demo | Listed as future work | Doc | Q7 |

## D. Value, impact and measures (§6–7)

| # | Concept-note point | Cat. | Demo feature | How it is demonstrated | Milestone | Open question |
|---|---|---|---|---|---|---|
| 25 | Identify coverage gaps without creating a separate insurance scheme or duplicating SHA's mandate (§6.1) | S | Wording on coverage screens; no benefit or claims features | Coverage page notice | M3 | — |
| 26 | Geographical coverage gaps (§6.4) | S | Coverage outcome by county | Dashboard / report | M4 / M5 | — |
| 27 | Traceability through access controls and audit trails (§6.5) | S | Activity log of key actions | Activity log page | M1 (recording) / M5 (page) | Retention and audit requirements (Q19) |
| 28 | Scalable to more programmes, counties and groups (§6.6) | S | Programmes, counties and categories are data, not code | Explained in architecture | Doc | — |
| 29 | Platform does not guarantee healthcare approval or expand SHA benefits (§6.3) | S | Disclaimer beside every simulated result | Coverage screens | M3 | — |
| 30 | Measure: number of beneficiaries registered (§7) | S | Dashboard KPI | Dashboard | M4 | Baseline (Q17) |
| 31 | Measure: number and proportion with verified active coverage (§7) | S | KPI shown as "**Confirmed in demo** (simulated)" — never "verified" | Dashboard | M4 | Q8 |
| 32 | Measure: pending cases resolved (§7) | S | Resolved vs open cases KPI | Dashboard | M4 | — |
| 33 | Measure: registration and case-processing times (§7) | S | Average days to resolve a case; registration-to-first-check time | Dashboard / report | M4 / M5 | Agreed service targets (Q14) |
| 34 | Measure: % of programme expenditure linked to documented activities (§7) | S | Calculated from the `linked_activity` field; unlinked entries flagged | Finance page | M4 | Q16 |
| 35 | Measure: completeness of administrative audit records (§7) | S | Activity log counts; completeness check list | Activity log page | M5 | Q19 |
| 36 | Measure: coverage by county, gender and sporting discipline (§7) | S | `county`, `gender`, `discipline` fields + breakdowns | Reports | M5 | Whether gender may be collected, and categories (Q3) |
| 37 | Measure: platform availability and operational performance (§7) | S | **Not demonstrable** in a laptop demo | Listed as future work | Doc | Hosting (Q21) |
| 38 | Impact principle: judge by registration → verified coverage → resolved cases, not registrations alone (§7) | S | Dashboard "coordination funnel" chart | Dashboard | M4 | — |
| 39 | Distinguish proposed targets, pilot results and verified outcomes (§7) | S | Every figure labelled "Demo data"; no targets shown as achievements | All pages | M1 onward | Targets set after baseline (Q17) |

## E. Implementation, governance and sustainability (§8–12)

| # | Concept-note point | Cat. | Demo feature | How it is demonstrated | Milestone | Open question |
|---|---|---|---|---|---|---|
| 40 | Five implementation phases (§8) | S | Shown on landing page; demo positioned in phase 1 | Landing page | M1 | Schedule and resources (Q22) |
| 41 | Each institution keeps its statutory mandate (§9) | S | SHA features simulated; no SHA data stored | Coverage screens; architecture doc | M3 / Doc | — |
| 42 | Kenya Data Protection Act 2019, privacy assessments (§9) | S | **Cannot be met by a demo.** Demo stores fictional data only | Known limitations | Doc | DPIA, controller/processor roles (Q18) |
| 43 | Data minimisation; no detailed clinical information (§9) | S | No medical fields, no national ID, phone stored masked | Schema; profile page | M1 | Minimum official field set (Q2) |
| 44 | Controlled access by responsibility (§9) | S | Role permissions checked on the server | Permission table in Settings; 403 page | M1 | Q5 |
| 45 | Accountability: records of activities and authorised exchanges (§9) | S | Activity log | Activity log page | M1 / M5 | Q19 |
| 46 | Privacy notices, consent, data-subject rights (§9) | S | Consent flag only; rights handling not built | Profile; limitations | M2 / Doc | Q18 |
| 47 | Proportionate security safeguards (§9) | S | Hashed passwords, CSRF tokens, parameterised SQL, secure cookies, server permission checks | Tests | M1 | Formal security review (Q21) |
| 48 | Joint coordination and monitoring mechanism (§9) | S | Not software | Presentation | Doc | Q20 |
| 49 | Sustainability: institutional, technical, operational, financial (§10) | S | Not software | Presentation and roadmap | Doc | Ownership and funding (Q22) |
| 50 | Five partnership areas (§11) and seven initial engagement areas (§12) | S | Not software — structure the open-questions list | OPEN_QUESTIONS.md | Doc | — |

## F. Recommended design choices (not in the concept note)

| # | Choice | Reason |
|---|---|---|
| R1 | Flask + Python's built-in SQLite + server-rendered pages + Chart.js stored locally | One small dependency, runs offline on a laptop, easy for a beginner to read |
| R2 | Five staff roles and their permission sets | Needed to demonstrate "controlled access"; real roles need agreement |
| R3 | Illustrative coverage outcomes: Confirmed in demo / Pending review / Further action required / Unable to confirm | Shows the workflow without inventing SHA's real categories |
| R4 | Case categories, priorities and statuses (Open, In progress, Awaiting information, Resolved) | Makes follow-up demonstrable; not official |
| R5 | Reference formats `DEMO-BEN-`, `DEMO-CASE-`, `DEMO-REF-`, `DEMO-TXN-`, `SIM-CHK-` | Makes every record visibly fictional |
| R6 | Masked phone numbers and reserved example email domains | Avoids real-looking contact data |
| R7 | Database rule `is_simulated = 1` on coverage checks and referrals | The database itself cannot hold a "real" result |
| R8 | One-click demo accounts and a confirmation-protected reset | Reliable presentations |
| R9 | CSV export carrying a "demonstration data" label | Shows reporting without implying official statistics |
