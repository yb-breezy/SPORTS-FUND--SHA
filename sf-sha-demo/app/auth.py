"""Sign-in and sign-out pages (the "auth" blueprint).

A blueprint is a group of related routes. This one owns /login and /logout.
"""
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db, log_activity
from .seed import DEMO_PASSWORD, DEMO_USERS
from .permissions import ROLES
from .security import is_safe_next

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.get("user"):
        return redirect(url_for("main.home"))

    error = None
    email = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Input validation on the server (the browser also checks, but never trust only that).
        if not email or not password:
            error = "Enter both an email address and a password."
        else:
            db = get_db()
            user = db.execute(
                "SELECT id, full_name, password_hash, is_active FROM users WHERE email = ?",
                (email,),
            ).fetchone()
            # One generic message, so the page doesn't reveal which emails exist.
            if user is None or not check_password_hash(user["password_hash"], password):
                error = "That email and password combination was not recognised."
            elif not user["is_active"]:
                error = "This demo account has been deactivated by the administrator."
            else:
                session.clear()                 # fresh session on every sign-in
                session["user_id"] = user["id"]
                session.permanent = True
                log_activity(db, user["id"], "Signed in", f"{user['full_name']} signed in", "user", user["id"])
                db.commit()
                flash(f"Welcome, {user['full_name']}. You are using fictional demo data.", "success")
                target = request.form.get("next", "")
                return redirect(target if is_safe_next(target) else url_for("main.home"))

    # Demo accounts listed on the login page so a presenter can switch roles quickly.
    demo_accounts = [
        {"name": u["name"], "email": u["email"], "role": ROLES[u["role"]]["name"]}
        for u in DEMO_USERS if u["featured"]
    ]
    return render_template(
        "auth/login.html",
        error=error,
        email=email,
        next=request.args.get("next", request.form.get("next", "")),
        demo_accounts=demo_accounts,
        demo_password=DEMO_PASSWORD,
    ), (400 if error else 200)


@bp.route("/logout", methods=["POST"])
def logout():
    if g.get("user"):
        db = get_db()
        log_activity(db, g.user["id"], "Signed out", f"{g.user['full_name']} signed out", "user", g.user["id"])
        db.commit()
    session.clear()
    flash("You have signed out of the demo.", "info")
    return redirect(url_for("main.index"))
