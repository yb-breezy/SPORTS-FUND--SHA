"""Server-side checks for the beneficiary form.

The browser also checks the form (app.js), but a browser check can be skipped,
so the SERVER always checks again here before anything is saved.

validate_beneficiary(form, db) returns two things:
  data   -> a clean dictionary ready to save
  errors -> {"field_name": "message to show"}; empty means everything is valid
The rules marked "proposed" are design choices for the demo, not official rules.
"""
import re
from datetime import date

from . import constants as C

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z' \-]{1,59}$")          # letters, spaces, ' and -
PHONE_RE = re.compile(r"^(?:\+?254|0)(?:7|1)\d{8}$")            # Kenyan mobile formats
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
EARLIEST_DATE = date(2020, 1, 1)


def mask_phone(phone):
    """Keep only the last 3 digits: 0712345678 -> 07•• ••• 678 (data minimisation)."""
    digits = re.sub(r"\D", "", phone)
    return f"07•• ••• {digits[-3:]}"


def validate_beneficiary(form, db, editing_id=None):
    errors = {}
    get = lambda name: (form.get(name) or "").strip()

    first, last = get("first_name"), get("last_name")
    for field, value, label in (("first_name", first, "First name"), ("last_name", last, "Last name")):
        if not value:
            errors[field] = f"{label} is required."
        elif not NAME_RE.match(value):
            errors[field] = f"{label} must be 2–60 letters (spaces, hyphens and apostrophes allowed)."

    gender, category, discipline, county, status = (
        get("gender"), get("category"), get("discipline"), get("county"), get("status"))
    if gender not in C.GENDERS:
        errors["gender"] = "Choose a gender option."
    if category not in C.CATEGORIES:
        errors["category"] = "Choose a beneficiary group."
    if discipline not in C.DISCIPLINES:
        errors["discipline"] = "Choose a sporting discipline."
    if county not in C.COUNTIES:
        errors["county"] = "Choose a county from the list."
    if status not in C.REGISTRATION_STATUSES:
        errors["status"] = "Choose a record status."

    phone = re.sub(r"[\s\-]", "", get("phone"))
    if phone and not PHONE_RE.match(phone):
        errors["phone"] = "Enter a Kenyan mobile number such as 0712345678, or leave it blank."

    email = get("email").lower()
    if email and not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address, or leave it blank."
    elif len(email) > 120:
        errors["email"] = "Email is too long."

    reg_text = get("registration_date")
    reg_date = None
    try:
        reg_date = date.fromisoformat(reg_text)
    except ValueError:
        errors["registration_date"] = "Enter the registration date."
    else:
        if reg_date > date.today():
            errors["registration_date"] = "The registration date cannot be in the future."
        elif reg_date < EARLIEST_DATE:
            errors["registration_date"] = "The registration date must be in 2020 or later."

    consent = form.get("consent_recorded") == "on"
    # Proposed rule: a record can only be "Registered" once consent has been recorded (concept note §5, §9).
    if status == "Registered" and not consent:
        errors["consent_recorded"] = "Record consent before marking the beneficiary as Registered."

    notes = get("notes")
    if len(notes) > 500:
        errors["notes"] = "Notes must be 500 characters or fewer."

    programme_id = None
    if editing_id is None:   # the programme is chosen only when registering
        try:
            programme_id = int(get("programme_id"))
        except ValueError:
            errors["programme_id"] = "Choose the programme this beneficiary joins."
        else:
            prog = db.execute("SELECT status FROM programmes WHERE id = ?", (programme_id,)).fetchone()
            if prog is None:
                errors["programme_id"] = "Choose the programme this beneficiary joins."
            elif prog["status"] != "Active":
                errors["programme_id"] = "New beneficiaries can only join an Active programme."

    # Proposed rule: warn about a likely duplicate (same full name in the same county).
    if not errors.get("first_name") and not errors.get("last_name") and county in C.COUNTIES:
        dup = db.execute(
            "SELECT demo_ref FROM beneficiaries WHERE lower(first_name) = lower(?) AND lower(last_name) = lower(?)"
            " AND county = ? AND id IS NOT ?",
            (first, last, county, editing_id),
        ).fetchone()
        if dup:
            errors["first_name"] = f"A beneficiary with this name already exists in {county} ({dup['demo_ref']})."

    data = {
        "first_name": first, "last_name": last, "gender": gender, "category": category,
        "discipline": discipline, "county": county, "status": status,
        "phone_masked": mask_phone(phone) if phone else None,
        "phone_changed": bool(phone),
        "email": email or None,
        "registration_date": reg_text,
        "consent_recorded": 1 if consent else 0,
        "notes": notes or None,
        "programme_id": programme_id,
    }
    return data, errors
