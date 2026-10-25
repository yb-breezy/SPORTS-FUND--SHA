"""The beneficiary register (milestone 2) — the "beneficiaries" blueprint.

Routes (every URL starts with /beneficiaries because of url_prefix):
  GET        /beneficiaries/              list with search, filters and pages
  GET, POST  /beneficiaries/new           register a new fictional beneficiary
  GET        /beneficiaries/<id>          profile page
  GET, POST  /beneficiaries/<id>/edit     update a record
"""
from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from . import constants as C
from .db import get_db, log_activity, now_text
from .security import permission_required
from .validation import validate_beneficiary

bp = Blueprint("beneficiaries", __name__, url_prefix="/beneficiaries")

PER_PAGE = 20

# The most recent simulated coverage outcome for each beneficiary. Worked out from
# coverage_checks every time, so it can never disagree with the check history.
LATEST_OUTCOME_SQL = (
    "(SELECT c.outcome FROM coverage_checks c WHERE c.beneficiary_id = b.id"
    " ORDER BY c.checked_at DESC, c.id DESC LIMIT 1)"
)


def _like(text):
    """Make user text safe inside LIKE: % and _ are treated as ordinary characters."""
    return "%" + text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


def _form_options(db, active_only=False):
    sql = "SELECT id, code, name, status FROM programmes"
    if active_only:
        sql += " WHERE status = 'Active'"
    return {
        "programmes": db.execute(sql + " ORDER BY code").fetchall(),
        "genders": C.GENDERS, "categories": C.CATEGORIES, "disciplines": C.DISCIPLINES,
        "counties": sorted(C.COUNTIES), "statuses": C.REGISTRATION_STATUSES,
        "outcomes": C.COVERAGE_OUTCOMES,
    }


@bp.route("/")
@permission_required("view_beneficiaries")
def list_beneficiaries():
    db = get_db()
    args = request.args
    filters = {
        "q": args.get("q", "").strip()[:80],
        "programme": args.get("programme", ""),
        "category": args.get("category", ""),
        "county": args.get("county", ""),
        "status": args.get("status", ""),
        "coverage": args.get("coverage", ""),
    }

    # Build the WHERE part step by step. Every value goes in through a "?" placeholder.
    where, params = [], []
    if filters["q"]:
        where.append("(b.demo_ref LIKE ? ESCAPE '\\' OR (b.first_name || ' ' || b.last_name) LIKE ? ESCAPE '\\')")
        params += [_like(filters["q"]), _like(filters["q"])]
    if filters["programme"].isdigit():
        where.append("EXISTS (SELECT 1 FROM participations pa WHERE pa.beneficiary_id = b.id AND pa.programme_id = ?)")
        params.append(int(filters["programme"]))
    for key in ("category", "county", "status"):
        if filters[key]:
            where.append(f"b.{key} = ?")      # key comes from our own fixed list, never from the user
            params.append(filters[key])
    if filters["coverage"] == "none":
        where.append(f"{LATEST_OUTCOME_SQL} IS NULL")
    elif filters["coverage"] in C.COVERAGE_OUTCOMES:
        where.append(f"{LATEST_OUTCOME_SQL} = ?")
        params.append(filters["coverage"])
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    total = db.execute(f"SELECT COUNT(*) FROM beneficiaries b {where_sql}", params).fetchone()[0]
    pages = max(1, -(-total // PER_PAGE))            # round up
    try:
        page = min(max(int(args.get("page", 1)), 1), pages)
    except ValueError:
        page = 1

    rows = db.execute(
        f"""SELECT b.id, b.demo_ref, b.first_name, b.last_name, b.category, b.county,
                   b.registration_date, b.status, {LATEST_OUTCOME_SQL} AS latest_outcome,
                   (SELECT group_concat(p.name, '|') FROM participations pa
                      JOIN programmes p ON p.id = pa.programme_id
                     WHERE pa.beneficiary_id = b.id) AS programme_names
              FROM beneficiaries b {where_sql}
             ORDER BY b.registration_date DESC, b.id DESC
             LIMIT ? OFFSET ?""",
        params + [PER_PAGE, (page - 1) * PER_PAGE],
    ).fetchall()

    active_filters = {k: v for k, v in filters.items() if v}
    return render_template(
        "beneficiaries/list.html", rows=rows, total=total, page=page, pages=pages,
        filters=filters, active_filters=active_filters, per_page=PER_PAGE,
        **_form_options(db),
    )


@bp.route("/new", methods=["GET", "POST"])
@permission_required("edit_beneficiaries")
def new_beneficiary():
    db = get_db()
    errors, form = {}, request.form
    if request.method == "POST":
        data, errors = validate_beneficiary(form, db)
        if not errors:
            last = db.execute("SELECT MAX(CAST(substr(demo_ref, 10) AS INTEGER)) FROM beneficiaries").fetchone()[0] or 0
            ref = f"DEMO-BEN-{last + 1:04d}"
            stamp = now_text()
            cur = db.execute(
                "INSERT INTO beneficiaries (demo_ref, first_name, last_name, gender, category, discipline,"
                " county, phone_masked, email, registration_date, status, consent_recorded, consent_date,"
                " validated_by, notes, created_by, created_at, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?)",
                (ref, data["first_name"], data["last_name"], data["gender"], data["category"],
                 data["discipline"], data["county"], data["phone_masked"], data["email"],
                 data["registration_date"], data["status"], data["consent_recorded"],
                 data["registration_date"] if data["consent_recorded"] else None,
                 data["notes"], g.user["id"], stamp, stamp),
            )
            new_id = cur.lastrowid
            db.execute(
                "INSERT INTO participations (beneficiary_id, programme_id, joined_on, status) VALUES (?, ?, ?, 'Active')",
                (new_id, data["programme_id"], data["registration_date"]),
            )
            log_activity(db, g.user["id"], "Beneficiary registered",
                         f"{ref} {data['first_name']} {data['last_name']} registered (demo record)",
                         "beneficiary", new_id)
            db.commit()
            flash(f"Fictional beneficiary {ref} was registered.", "success")
            return redirect(url_for("beneficiaries.profile", beneficiary_id=new_id))
        flash("Please correct the highlighted fields.", "error")

    values = form if request.method == "POST" else {
        "registration_date": date.today().isoformat(), "status": "Pending validation"}
    return render_template("beneficiaries/form.html", mode="new", values=values, errors=errors,
                           today=date.today().isoformat(), **_form_options(db, active_only=True)), (
        400 if errors else 200)


def _load(db, beneficiary_id):
    row = db.execute("SELECT * FROM beneficiaries WHERE id = ?", (beneficiary_id,)).fetchone()
    if row is None:
        abort(404)
    return row


@bp.route("/<int:beneficiary_id>")
@permission_required("view_beneficiaries")
def profile(beneficiary_id):
    db = get_db()
    b = _load(db, beneficiary_id)
    created_by = db.execute("SELECT full_name FROM users WHERE id = ?", (b["created_by"],)).fetchone()
    programmes = db.execute(
        "SELECT p.id, p.code, p.name, p.status AS programme_status, pa.joined_on, pa.status"
        "  FROM participations pa JOIN programmes p ON p.id = pa.programme_id"
        " WHERE pa.beneficiary_id = ? ORDER BY pa.joined_on", (beneficiary_id,)).fetchall()
    checks = db.execute(
        "SELECT c.*, u.full_name AS checked_by_name FROM coverage_checks c"
        "  LEFT JOIN users u ON u.id = c.checked_by"
        " WHERE c.beneficiary_id = ? ORDER BY c.checked_at DESC, c.id DESC", (beneficiary_id,)).fetchall()
    cases = db.execute(
        "SELECT fc.*, u.full_name AS assignee FROM follow_up_cases fc"
        "  LEFT JOIN users u ON u.id = fc.assigned_to"
        " WHERE fc.beneficiary_id = ? ORDER BY fc.created_at DESC", (beneficiary_id,)).fetchall()
    referrals = db.execute(
        "SELECT * FROM referrals WHERE beneficiary_id = ? ORDER BY created_at DESC", (beneficiary_id,)).fetchall()
    activity = db.execute(
        """SELECT a.created_at, a.action, a.summary, u.full_name AS actor
             FROM activity_log a LEFT JOIN users u ON u.id = a.actor_id
            WHERE (a.entity_type = 'beneficiary' AND a.entity_id = ?)
               OR (a.entity_type = 'case' AND a.entity_id IN
                     (SELECT id FROM follow_up_cases WHERE beneficiary_id = ?))
            ORDER BY a.created_at DESC, a.id DESC LIMIT 25""",
        (beneficiary_id, beneficiary_id)).fetchall()
    return render_template(
        "beneficiaries/profile.html", b=b, created_by=created_by, programmes=programmes,
        checks=checks, latest=checks[0] if checks else None, cases=cases,
        open_cases=[c for c in cases if c["status"] != "Resolved"],
        referrals=referrals, activity=activity)


@bp.route("/<int:beneficiary_id>/edit", methods=["GET", "POST"])
@permission_required("edit_beneficiaries")
def edit_beneficiary(beneficiary_id):
    db = get_db()
    b = _load(db, beneficiary_id)
    errors = {}
    if request.method == "POST":
        data, errors = validate_beneficiary(request.form, db, editing_id=beneficiary_id)
        if not errors:
            phone = data["phone_masked"] if data["phone_changed"] else b["phone_masked"]
            if data["consent_recorded"] and not b["consent_recorded"]:
                consent_date = date.today().isoformat()      # consent recorded today
            elif data["consent_recorded"]:
                consent_date = b["consent_date"]
            else:
                consent_date = None
            fields = ("first_name", "last_name", "gender", "category", "discipline", "county",
                      "email", "registration_date", "status", "consent_recorded", "notes")
            changed = [f.replace("_", " ") for f in fields if (b[f] or None) != (data[f] or None)]
            if phone != b["phone_masked"]:
                changed.append("phone")
            if changed:
                db.execute(
                    "UPDATE beneficiaries SET first_name = ?, last_name = ?, gender = ?, category = ?,"
                    " discipline = ?, county = ?, phone_masked = ?, email = ?, registration_date = ?,"
                    " status = ?, consent_recorded = ?, consent_date = ?, notes = ?, updated_at = ?"
                    " WHERE id = ?",
                    (data["first_name"], data["last_name"], data["gender"], data["category"],
                     data["discipline"], data["county"], phone, data["email"], data["registration_date"],
                     data["status"], data["consent_recorded"], consent_date, data["notes"], now_text(),
                     beneficiary_id),
                )
                log_activity(db, g.user["id"], "Beneficiary updated",
                             f"{b['demo_ref']}: changed {', '.join(changed)}", "beneficiary", beneficiary_id)
                db.commit()
                flash(f"{b['demo_ref']} was updated.", "success")
            else:
                flash("No changes were made.", "info")
            return redirect(url_for("beneficiaries.profile", beneficiary_id=beneficiary_id))
        flash("Please correct the highlighted fields.", "error")

    values = request.form if request.method == "POST" else {
        **dict(b), "consent_recorded": "on" if b["consent_recorded"] else "", "phone": ""}
    return render_template("beneficiaries/form.html", mode="edit", b=b, values=values, errors=errors,
                           today=date.today().isoformat(), **_form_options(db)), (400 if errors else 200)
