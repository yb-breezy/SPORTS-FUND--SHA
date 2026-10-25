"""Database helpers: open a connection, close it, rebuild it.

We use Python's built-in sqlite3 module. Every query in the app uses "?"
placeholders, e.g.  db.execute("SELECT * FROM users WHERE email = ?", (email,))
SQLite fills the "?" in safely, which protects against SQL injection.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import current_app, g

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def now_text():
    """Current local time as text, e.g. '2026-10-25 14:30:00'."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def connect(path):
    """Open a SQLite connection with the settings this app relies on."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row             # rows behave like dicts: row["email"]
    conn.execute("PRAGMA foreign_keys = ON")   # SQLite needs this to enforce links
    return conn


def get_db():
    """Return this request's connection, opening it the first time it is needed.

    Flask's `g` object lives for one request, so each request gets one connection.
    """
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"])
    return g.db


def close_db(_error=None):
    """Called automatically by Flask at the end of every request."""
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def rebuild_database(conn):
    """Delete every table, recreate them, and load the fictional sample data.

    Used on first start-up, by the Settings page "Reset demo", and by
    the command:  flask --app run reset-demo
    """
    from .seed import seed_demo_data  # imported here to avoid a circular import

    conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
    seed_demo_data(conn)
    conn.commit()


def database_is_ready(path):
    """True if the database file exists and already contains the roles table."""
    if not Path(path).exists():
        return False
    conn = connect(path)
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'roles'"
        ).fetchone()
        if row[0] == 0:
            return False
        return conn.execute("SELECT COUNT(*) FROM roles").fetchone()[0] > 0
    finally:
        conn.close()


def log_activity(conn, actor_id, action, summary, entity_type=None, entity_id=None):
    """Write one line to the prototype activity log. The caller commits."""
    conn.execute(
        "INSERT INTO activity_log (actor_id, action, entity_type, entity_id, summary, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (actor_id, action, entity_type, entity_id, summary, now_text()),
    )
