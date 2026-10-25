"""General pages: landing, home, settings and demo reset (the "main" blueprint)."""
from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for

from .constants import CATEGORIES
from .db import get_db, log_activity, rebuild_database
from .permissions import PERMISSIONS, ROLES
from .security import login_required, permission_required

bp = Blueprint("main", __name__)

# The eight functional areas from concept note §4, with how this demo treats each.
FUNCTIONAL_AREAS = [
    ("Beneficiary management", "Centralised registration and management of eligible programme beneficiaries.", "Demonstrated"),
    ("Coverage coordination", "Verification of coverage status and identification of outstanding cases.", "Simulated"),
    ("Enrolment support", "Coordinated follow-up for beneficiaries who need enrolment assistance.", "Demonstrated"),
    ("Programme monitoring", "Consolidated view of reach, coverage progress and programme activity.", "Demonstrated"),
    ("Management reporting", "Dashboards and periodic reports to support decision-making.", "Demonstrated"),
    ("Financial accountability", "Visibility of programme expenditure against beneficiaries and activities.", "Demonstrated"),
    ("Referral coordination", "Guidance on accessing accredited facilities, subject to SHA entitlements.", "Simulated"),
    ("Institutional oversight", "Role-based access and a traceable record of administrative activity.", "Demonstrated"),
]

# Concept note §8 — the proposed implementation phases.
IMPLEMENTATION_PHASES = [
    ("Institutional engagement and alignment", "Agreed concept and preliminary institutional framework."),
    ("Feasibility and requirements assessment", "Validated requirements and an agreed implementation scope."),
    ("Platform development and institutional integration", "A tested system ready for controlled deployment."),
    ("Controlled pilot implementation", "Pilot evaluation and recommendations."),
    ("Evaluation and phased expansion", "An evidence-based scale-up plan."),
]


@bp.route("/")
def index():
    return render_template("landing.html", areas=FUNCTIONAL_AREAS, phases=IMPLEMENTATION_PHASES)


@bp.route("/home")
@login_required
def home():
    db = get_db()
    # One query that counts every table. Every number on the page comes from the database.
    counts = db.execute(
        """SELECT
             (SELECT COUNT(*) FROM beneficiaries)                         AS beneficiaries,
             (SELECT COUNT(*) FROM beneficiaries WHERE status = 'Registered') AS registered,
             (SELECT COUNT(*) FROM programmes)                            AS programmes,
             (SELECT COUNT(*) FROM coverage_checks)                       AS coverage_checks,
             (SELECT COUNT(*) FROM follow_up_cases)                       AS cases,
             (SELECT COUNT(*) FROM follow_up_cases WHERE status <> 'Resolved') AS open_cases,
             (SELECT COUNT(*) FROM referrals)                             AS referrals,
             (SELECT COUNT(*) FROM financial_records)                     AS financial_records,
             (SELECT COUNT(*) FROM users)                                 AS users,
             (SELECT COUNT(*) FROM activity_log)                          AS activity"""
    ).fetchone()
    rows = db.execute(
        "SELECT category, COUNT(*) AS n FROM beneficiaries GROUP BY category"
    ).fetchall()
    by_category = {r["category"]: r["n"] for r in rows}
    category_breakdown = [(c, by_category.get(c, 0)) for c in CATEGORIES]
    largest = max([n for _, n in category_breakdown] + [1])

    my_permissions = [
        (key, label) for key, label in PERMISSIONS.items()
        if key in ROLES[g.user["role_key"]]["permissions"]
    ]
    return render_template(
        "main/home.html",
        counts=counts,
        category_breakdown=category_breakdown,
        largest=largest,
        my_permissions=my_permissions,
    )


@bp.route("/settings")
@login_required
def settings():
    return render_template("main/settings.html", roles=ROLES, permissions=PERMISSIONS)


@bp.route("/settings/reset", methods=["POST"])
@permission_required("reset_demo")      # only the Administrator role; others get 403
def reset_demo():
    # Second safety check: the person must type RESET exactly.
    if request.form.get("confirm_text", "").strip() != "RESET":
        flash("Reset cancelled. Type RESET in the box to confirm.", "error")
        return redirect(url_for("main.settings"))

    actor_name = g.user["full_name"]
    db = get_db()
    rebuild_database(db)
    # The reset recreates the same demo accounts, so the administrator stays signed in.
    admin = db.execute("SELECT id FROM users WHERE email = ?", (g.user["email"],)).fetchone()
    log_activity(db, admin["id"] if admin else None, "Demo reset",
                 f"{actor_name} restored the original fictional sample dataset")
    db.commit()
    current_app.logger.info("Demo database reset to original sample data.")
    flash("The demo has been reset to the original fictional sample data.", "success")
    return redirect(url_for("main.settings"))
