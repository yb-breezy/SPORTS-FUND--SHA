"""Login checks, permission checks and CSRF protection.

Three ideas live here:

1. load_logged_in_user() runs before EVERY request. It reads the user id
   saved in the signed session cookie and loads that user into `g.user`.

2. login_required / permission_required are "decorators": you put them
   above a route function and they run first. If the user may not do the
   action, the server stops the request with a 403 error, so hiding a
   button is never the only protection.

3. CSRF protection: every form includes a secret token. A form posted from
   another website won't have it, so we reject it.
"""
import secrets
from functools import wraps

from flask import abort, flash, g, redirect, request, session, url_for

from .db import get_db
from .permissions import role_has


def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is None:
        return
    row = get_db().execute(
        "SELECT users.id, users.full_name, users.email, users.is_active,"
        "       roles.key AS role_key, roles.name AS role_name"
        "  FROM users JOIN roles ON roles.id = users.role_id"
        " WHERE users.id = ?",
        (user_id,),
    ).fetchone()
    if row is None or not row["is_active"]:
        # Account deleted (e.g. after a reset) or deactivated: sign them out.
        session.clear()
        return
    g.user = row


def can(permission):
    """True if the signed-in user's role has `permission`. Usable in templates."""
    return g.get("user") is not None and role_has(g.user["role_key"], permission)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.get("user") is None:
            flash("Please sign in to continue.", "info")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def permission_required(permission):
    """Decorator factory: @permission_required("reset_demo")."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not can(permission):
                abort(403)   # server-side refusal — the real protection
            return view(*args, **kwargs)
        return wrapped
    return decorator


# ---------- CSRF ----------

def csrf_token():
    """Return (and remember) this session's CSRF token. Used in every form."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def check_csrf(app):
    """Runs before every request; rejects POSTs without the right token."""
    if not app.config.get("CSRF_ENABLED", True):
        return
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        sent = request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        if not expected or not secrets.compare_digest(sent, expected):
            abort(400, description="The form expired or was not sent from this demo. Please try again.")


def is_safe_next(target):
    """Only allow redirects to pages inside this app (prevents open redirects)."""
    return bool(target) and target.startswith("/") and not target.startswith("//")
