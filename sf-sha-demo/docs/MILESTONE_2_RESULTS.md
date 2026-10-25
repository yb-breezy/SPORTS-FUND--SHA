# Milestone 2: Beneficiary register (results)

Covers concept note §3.3 objective 1 ("coordinated beneficiary registry") and Workflow A.

## Built
- **List** (`/beneficiaries/`): 20 per page, newest first, with each person's group, programme(s), county, record status and latest **simulated** coverage outcome.
- **Search** by name or `DEMO-BEN-` number. Typed `%` and `_` are treated as plain text.
- **Filters**: programme, group, county, record status, latest coverage outcome (including "Not yet checked"). Filters stay in the web address and are kept when you change page. **Clear** resets them.
- **Add beneficiary**: grouped form (basic information, programme and group, registration) with checks in the browser **and** on the server. Typed values are kept if there is an error.
- **Edit**: the same form, pre-filled. Only changed fields are recorded in the activity log. Leaving the phone blank keeps the current number.
- **Profile**: basic information, registration and consent, programme participation, simulated coverage history, follow-up cases, referrals and activity history. Actions for later milestones are described in text, not shown as buttons.
- The **Beneficiaries** menu item is now a live link, and the Home page's build progress is updated.

## Proposed rules (recommended for the demo, not from the concept note)
| Rule | Reason |
|---|---|
| A record can only be **Registered** once consent is recorded | Concept note §5 and §9 mention consent |
| New beneficiaries can only join an **Active** programme | Avoids joining planned or finished programmes |
| Same full name in the same county is flagged as a **possible duplicate** | Registry quality |
| Only the last 3 digits of a phone number are kept | Data minimisation (§9) |
| Names: 2–60 letters, spaces, hyphens, apostrophes | Basic data quality |
| Registration date: 2020 or later, not in the future | Basic data quality |
| No medical, clinical or ID fields | §9: avoid detailed clinical information |

These rules, and the official field list, need institutional agreement (see OPEN_QUESTIONS Q1, Q2, Q18).

## Who can do what
| Role | View list/profiles | Add / edit |
|---|---|---|
| Administrator, Beneficiary management officer | ✓ | ✓ |
| Programme officer, Coverage officer, Management | ✓ | ✗ (server answers 403) |

## Tested
**Automated:** `python -m unittest discover -s tests -t . -v` gave **49 tests, all OK** (26 from milestone 1 + 23 new). The new tests cover:
- paging, including bad and out-of-range page numbers
- search by reference and full name, with wildcards treated as text
- each filter's count matching a direct database count
- filters kept when paging, and hostile filter values handled safely
- a valid registration: new reference, masked phone, programme link, activity log, profile, list and Home count updated
- 10 kinds of invalid input rejected with the right message and nothing saved
- typed values kept after an error
- duplicates flagged, and "Pending validation" allowed without consent
- HTML in notes shown as text, not run
- edits saved and logged, and "no changes" detected
- every profile section and simulation label present, and Management sees no Edit button
- a missing profile gives 404
- Management, Programme officer and Coverage officer refused on all add/edit routes (GET and POST)
- signed-out visitors redirected to sign in
- reset removing records added during a demo

**In a real (headless) browser, as Beneficiary management officer:**
1. Opened the list and filtered by "Pending validation" (10 results).
2. Clicked *Add beneficiary* and submitted it empty: 7 field messages appeared.
3. Filled the form with status Registered but no consent: the server rejected it with the consent message.
4. Ticked consent and saved: **DEMO-BEN-0161** was created, and the profile opened with the success message.
5. Edited the notes and saved: an "updated" message appeared and the activity history showed 2 entries.
6. Searched for the new name: 1 result. Home showed **161**.

Phone width (390px): no sideways scrolling on the list or profile. The only browser console entry was the expected 400 response from the rejected form.

## Known limitations
- Programme participation can't be changed from the edit form; that comes with the Programmes module (M4).
- Running a coverage check and opening cases from the profile comes in M3.
- Beneficiaries can't be deleted. This is deliberate for an audit-friendly registry; records can be set to *Inactive* instead.
