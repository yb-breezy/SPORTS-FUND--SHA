"""The application factory: create_app() builds and wires up the whole app.

Reading order for beginners:
  run.py            -> calls create_app()
  app/__init__.py   -> (this file) settings, database, blueprints, error pages
  app/auth.py       -> /login and /logout
  app/main.py       -> /, /home, /settings, /settings/reset
  app/templates/    -> the HTML each route returns
  app/static/       -> CSS and JavaScript the HTML loads
"""
import os
import secrets
from datetime import timedelta
from pathlib import Path

import click
from flask import Flask, render_template

from . import constants
from .db import close_db, connect, database_is_ready, rebuild_database
from .permissions import ROLES
from .security import can, check_csrf, csrf_token, load_logged_in_user


# Sidebar items. endpoint=None means "planned for a later milestone": it is
# shown greyed out with its milestone number and is NOT a clickable link.
NAV_ITEMS = [
    {"label": "Home",                  "endpoint": "main.home",     "permission": None,                 "milestone": 1},
    {"label": "Dashboard",             "endpoint": None,            "permission": "view_dashboard",     "milestone": 4},
    {"label": "Beneficiaries",         "endpoint": "beneficiaries.list_beneficiaries", "permission": "view_beneficiaries", "milestone": 2},
    {"label": "Coverage coordination", "endpoint": None,            "permission": "view_coverage",      "milestone": 3},
    {"label": "Follow-up cases",       "endpoint": None,            "permission": "view_cases",         "milestone": 3},
    {"label": "Referrals",             "endpoint": None,            "permission": "view_referrals",     "milestone": 3},
    {"label": "Programmes",            "endpoint": None,            "permission": "view_programmes",    "milestone": 4},
    {"label": "Finance",               "endpoint": None,            "permission": "view_finance",       "milestone": 4},
    {"label": "Reports",               "endpoint": None,            "permission": "view_reports",       "milestone": 5},
    {"label": "Users & roles",         "endpoint": None,            "permission": "manage_users",       "milestone": 5},
    {"label": "Activity log",          "endpoint": None,            "permission": "view_activity_log",  "milestone": 5},
    {"label": "Settings",              "endpoint": "main.settings", "permission": None,                 "milestone": 1},
]


def _secret_key(instance_path):
    """Use SECRET_KEY from the environment, or create one and keep it in instance/."""
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    key_file = Path(instance_path) / "secret_key"
    if not key_file.exists():
        key_file.write_text(secrets.token_hex(32))
    return key_file.read_text().strip()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)   # instance/ holds the database

    app.config.update(
        DATABASE=str(Path(app.instance_path) / "demo.db"),
        CSRF_ENABLED=True,
        SESSION_COOKIE_HTTPONLY=True,     # JavaScript cannot read the session cookie
        SESSION_COOKIE_SAMESITE="Lax",    # extra protection against cross-site requests
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = _secret_key(app.instance_path)

    # First start-up (or deleted database): build it and load the sample data.
    if not database_is_ready(app.config["DATABASE"]):
        conn = connect(app.config["DATABASE"])
        try:
            rebuild_database(conn)
        finally:
            conn.close()
        app.logger.info("Created the demo database with fictional sample data.")

    # ----- things that run around every request -----
    app.teardown_appcontext(close_db)
    app.before_request(lambda: check_csrf(app))
    app.before_request(load_logged_in_user)

    # ----- values every template can use -----
    @app.context_processor
    def inject_globals():
        return {
            "APP_NAME": constants.APP_NAME,
            "DEMO_NOTICE": constants.DEMO_NOTICE,
            "csrf_token": csrf_token,
            "can": can,
            "nav_items": NAV_ITEMS,
            "role_names": {k: v["name"] for k, v in ROLES.items()},
            "COMPLETED_MILESTONE": constants.COMPLETED_MILESTONE,
        }

    # ----- routes, grouped in blueprints -----
    from . import auth, beneficiaries, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(beneficiaries.bp)

    # ----- friendly error pages (no technical details shown to the viewer) -----
    @app.errorhandler(400)
    def bad_request(err):
        return render_template("errors/error.html", code=400, title="Request not accepted",
                               message=getattr(err, "description", "")), 400

    @app.errorhandler(403)
    def forbidden(_err):
        return render_template("errors/error.html", code=403, title="Not permitted for this role",
                               message="Your demo role does not include this action. Proposed roles and "
                                       "permissions would need agreement from the institutions."), 403

    @app.errorhandler(404)
    def not_found(_err):
        return render_template("errors/error.html", code=404, title="Page not found",
                               message="This page does not exist in the demo."), 404

    @app.errorhandler(500)
    def server_error(_err):
        return render_template("errors/error.html", code=500, title="Something went wrong",
                               message="The demo hit an unexpected error. The details are in the terminal."), 500

    # ----- terminal command: flask --app run reset-demo -----
    @app.cli.command("reset-demo")
    def reset_demo_command():
        """Delete all demo data and reload the original fictional sample data."""
        conn = connect(app.config["DATABASE"])
        try:
            rebuild_database(conn)
        finally:
            conn.close()
        click.echo("Demo database reset to the original fictional sample data.")

    return app
