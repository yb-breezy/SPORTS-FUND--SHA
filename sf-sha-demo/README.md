# Sports Fund–SHA Beneficiary Management Demo

> **Independent demonstration prototype.** This is not an official Sports Fund or SHA system, it has not been approved or endorsed by either institution, and it is not connected to their systems. Every record is fictional and every coverage or referral result is simulated.

A professional, interactive demo of the proposed *Sports Fund–SHA Digital Beneficiary Management and Universal Health Coverage Integration Initiative*. It is built to help the Head of Sports Fund explain the concept and start an informed discussion with SHA.

## What you need (once)
- **Python 3.10 or newer**. Check with `python --version` (Windows) or `python3 --version` (Mac/Linux).
- **VS Code** (or any editor).
- Internet **only for the one-time install** below. After that, the demo runs fully offline.

## Set up (first time only)

Open the `sf-sha-demo` folder in VS Code, then open a terminal (**Terminal → New Terminal**).

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If PowerShell says scripts are disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y`, then repeat the second line.

**Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You'll know the virtual environment is active when your prompt starts with `(.venv)`.

## Run the demo
```
python run.py
```
Expected output:
```
  Sports Fund–SHA Beneficiary Management Demo (fictional data)
  Open http://127.0.0.1:5000 in your browser. Press CTRL+C to stop.
 * Running on http://127.0.0.1:5000
```
The first run creates `instance/demo.db` and fills it with the fictional sample data automatically.

## Demo accounts
All use the password **`Demo@2026`**. The login page has a **Use** button for each.

| Proposed role | Email |
|---|---|
| Administrator | admin@sfsha-demo.example |
| Beneficiary management officer | beneficiary.officer@sfsha-demo.example |
| Programme officer | programme.officer@sfsha-demo.example |
| Coverage coordination officer | coverage.officer@sfsha-demo.example |
| Management (view-only) | management@sfsha-demo.example |

## Reset the sample data
- **In the app:** sign in as Administrator → **Settings** → type `RESET` → **Reset demo data**.
- **From the terminal** (with the server stopped): `flask --app run reset-demo`

## Run the automated tests
```
python -m unittest discover -s tests -t . -v
```
Expected last lines: `Ran 26 tests …` then `OK`.

## Documentation
- `docs/HOW_IT_FITS_TOGETHER.md`: a guided tour of the code
- `docs/ARCHITECTURE.md`: technology choices, architecture, ERD, tables
- `docs/REQUIREMENTS_MATRIX.md`: every concept-note point mapped to a feature
- `docs/OPEN_QUESTIONS.md`: questions for the Sports Fund and SHA
- `docs/MILESTONE_1_RESULTS.md`: what was built and tested in milestone 1

## Build status
| Milestone | Scope | Status |
|---|---|---|
| M1 | Foundation: sign-in, 5 roles, layout, sample data, reset | ✅ Done and tested |
| M2 | Beneficiary register and profiles | Planned |
| M3 | Simulated coverage checks, follow-up cases, referrals | Planned |
| M4 | Dashboard, programmes, financial accountability | Planned |
| M5 | Reports & CSV export, users & roles, activity log | Planned |
| M6 | Full testing, polish, presentation walkthrough | Planned |
