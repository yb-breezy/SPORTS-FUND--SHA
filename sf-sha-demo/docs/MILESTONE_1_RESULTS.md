# Milestone 1: Foundation (results)

## Built
- Project structure, app factory, Flask blueprints (`auth`, `main`)
- Full database schema for **all** planned modules, with foreign keys and allowed-value checks
- Deterministic fictional sample data: 160 beneficiaries, 8 programmes, 141 simulated checks, 40 cases (206 history entries), 30 simulated referrals, 113 financial entries, 10 demo accounts
- Sign-in / sign-out with hashed passwords, a fresh session on sign-in, and a generic error message
- Five proposed roles; **server-side** permission checks (`@permission_required`) with a friendly 403 page
- CSRF protection on every form
- Landing page with demo notice, the eight functional areas from §4, and the five phases from §8
- Signed-in layout: demo banner, sidebar (planned modules shown greyed with their milestone, not as dead links), top bar
- Home page with live counts from the database
- Settings: current user, demo notice, proposed permission table, and a reset protected by role + typed `RESET` + a confirmation dialog
- Activity log recording of sign-in, sign-out and reset
- Responsive layout (phone menu), system fonts only, no internet requests

## Tested
**Automated:** `python -m unittest discover -s tests -t . -v` gave **26 tests, all OK**. They cover:
- startup, landing and 404 pages
- sample data counts, `DEMO-`/`SIM-` references, no future dates, identical data after reset
- the database refusing a non-simulated coverage result
- sign-in for every role, wrong password, empty form, deactivated account, passwords hashed, safe redirects
- management having no editing permission, and non-admins getting 403 on reset
- reset requiring `RESET` and restoring the data
- home figures changing when the database changes
- CSRF on and off
- no `http://` or `https://` in any template, CSS or JS file

**In a real (headless) browser:** landing → login → empty-form validation messages appeared → "Use" filled the admin account → home → settings → reset with confirmation dialog → success message. Phone width (390px): no sideways scrolling, menu opens. No JavaScript console errors.

## Known limitations at this milestone
- Modules M2–M5 are planned, not yet built; they are shown greyed out in the menu.
- Chart.js is added in M4 (saved locally in the project, not loaded from the internet).
- The activity log records events but has no page to view them until M5.
- This is a laptop demo: no hosting, backups, availability monitoring or formal security review.
