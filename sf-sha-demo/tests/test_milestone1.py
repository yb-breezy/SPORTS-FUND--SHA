"""Automated checks for milestone 1.

Run from the project folder:   python -m unittest discover -s tests -v

Each test builds a fresh copy of the app with its own temporary database,
so the tests never touch your real demo data in instance/demo.db.
"""
import re
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.permissions import PERMISSIONS, ROLES
from app.seed import DEMO_PASSWORD, DEMO_USERS

PROJECT = Path(__file__).resolve().parent.parent


def email_for(role):
    return next(u["email"] for u in DEMO_USERS if u["role"] == role and u["featured"])


class DemoTestCase(unittest.TestCase):
    csrf = False   # most tests switch CSRF off to keep them short; one class tests it

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = str(Path(self.tmp) / "test.db")
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path,
                               "SECRET_KEY": "test-only", "CSRF_ENABLED": self.csrf})
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def query(self, sql, args=()):
        conn = sqlite3.connect(self.db_path)
        try:
            return conn.execute(sql, args).fetchone()[0]
        finally:
            conn.close()

    def login(self, role):
        return self.client.post("/login", data={"email": email_for(role), "password": DEMO_PASSWORD})


class StartupAndPages(DemoTestCase):
    def test_landing_page_shows_demo_notice(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        html = r.get_data(as_text=True)
        self.assertIn("not an official Sports Fund or SHA system", html)
        self.assertIn("Enter the demo", html)

    def test_unknown_page_gives_friendly_404(self):
        r = self.client.get("/no-such-page")
        self.assertEqual(r.status_code, 404)
        self.assertIn("Page not found", r.get_data(as_text=True))

    def test_static_files_are_served(self):
        for path in ("/static/css/app.css", "/static/js/app.js"):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200)
            r.close()


class SampleData(DemoTestCase):
    def test_expected_record_counts(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM roles"), 5)
        self.assertEqual(self.query("SELECT COUNT(*) FROM users"), len(DEMO_USERS))
        self.assertEqual(self.query("SELECT COUNT(*) FROM programmes"), 8)
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries"), 160)
        for table in ("coverage_checks", "follow_up_cases", "case_activities", "referrals", "financial_records"):
            self.assertGreater(self.query(f"SELECT COUNT(*) FROM {table}"), 20, table)

    def test_every_reference_is_marked_as_demo(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries WHERE demo_ref NOT LIKE 'DEMO-%'"), 0)
        self.assertEqual(self.query("SELECT COUNT(*) FROM coverage_checks WHERE sample_ref NOT LIKE 'SIM-%'"), 0)
        self.assertEqual(self.query("SELECT COUNT(*) FROM follow_up_cases WHERE case_ref NOT LIKE 'DEMO-%'"), 0)
        self.assertEqual(self.query("SELECT COUNT(*) FROM financial_records WHERE txn_ref NOT LIKE 'DEMO-%'"), 0)
        self.assertEqual(self.query(
            "SELECT COUNT(*) FROM beneficiaries WHERE email IS NOT NULL AND email NOT LIKE '%@example.org'"), 0)

    def test_database_refuses_non_simulated_coverage_results(self):
        conn = sqlite3.connect(self.db_path)
        with self.assertRaises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO coverage_checks (beneficiary_id, outcome, sample_ref, checked_at, is_simulated)"
                         " VALUES (1, 'Confirmed in demo', 'X-1', '2026-01-01', 0)")
        conn.close()

    def test_no_dates_in_the_future(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries WHERE registration_date > date('now','localtime')"), 0)
        self.assertEqual(self.query("SELECT COUNT(*) FROM coverage_checks WHERE date(checked_at) > date('now','localtime')"), 0)

    def test_sample_data_is_identical_after_rebuild(self):
        first = self.query("SELECT group_concat(first_name || last_name || county, ',') FROM beneficiaries")
        self.login("admin")
        self.client.post("/settings/reset", data={"confirm_text": "RESET"})
        self.assertEqual(self.query("SELECT group_concat(first_name || last_name || county, ',') FROM beneficiaries"), first)


class SignIn(DemoTestCase):
    def test_protected_page_redirects_to_login(self):
        r = self.client.get("/home")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.headers["Location"])

    def test_every_featured_role_can_sign_in(self):
        for role in ROLES:
            with self.subTest(role=role):
                r = self.login(role)
                self.assertEqual(r.status_code, 302)
                home = self.client.get("/home").get_data(as_text=True)
                self.assertIn(ROLES[role]["name"].replace("&", "&amp;"), home)
                self.client.post("/logout")

    def test_wrong_password_is_rejected(self):
        r = self.client.post("/login", data={"email": email_for("admin"), "password": "wrong"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("was not recognised", r.get_data(as_text=True))
        self.assertEqual(self.client.get("/home").status_code, 302)

    def test_empty_form_is_rejected(self):
        r = self.client.post("/login", data={"email": "", "password": ""})
        self.assertEqual(r.status_code, 400)
        self.assertIn("Enter both", r.get_data(as_text=True))

    def test_deactivated_account_cannot_sign_in(self):
        r = self.client.post("/login", data={"email": "inactive.user@sfsha-demo.example", "password": DEMO_PASSWORD})
        self.assertEqual(r.status_code, 400)
        self.assertIn("deactivated", r.get_data(as_text=True))

    def test_passwords_are_hashed(self):
        self.assertEqual(self.query("SELECT COUNT(*) FROM users WHERE password_hash = ?", (DEMO_PASSWORD,)), 0)

    def test_sign_in_and_out_are_logged(self):
        before = self.query("SELECT COUNT(*) FROM activity_log WHERE action IN ('Signed in','Signed out')")
        self.login("management")
        self.client.post("/logout")
        after = self.query("SELECT COUNT(*) FROM activity_log WHERE action IN ('Signed in','Signed out')")
        self.assertEqual(after - before, 2)

    def test_redirect_after_login_stays_inside_app(self):
        r = self.client.post("/login", data={"email": email_for("admin"), "password": DEMO_PASSWORD,
                                             "next": "//evil.example/steal"})
        self.assertTrue(r.headers["Location"].endswith("/home"))


class Permissions(DemoTestCase):
    def test_management_is_view_only(self):
        changing = [p for p in ROLES["management"]["permissions"]
                    if p.startswith(("edit_", "run_", "manage_", "reset_"))]
        self.assertEqual(changing, [])

    def test_every_role_permission_exists(self):
        for role in ROLES.values():
            self.assertTrue(role["permissions"] <= set(PERMISSIONS))

    def test_non_admin_roles_are_refused_reset_by_the_server(self):
        for role in ("beneficiary_officer", "programme_officer", "coverage_officer", "management"):
            with self.subTest(role=role):
                self.login(role)
                r = self.client.post("/settings/reset", data={"confirm_text": "RESET"})
                self.assertEqual(r.status_code, 403)
                self.client.post("/logout")

    def test_reset_button_only_shown_to_admin(self):
        self.login("management")
        self.assertNotIn("Reset demo data</button>", self.client.get("/settings").get_data(as_text=True))
        self.client.post("/logout")
        self.login("admin")
        self.assertIn("Reset demo data</button>", self.client.get("/settings").get_data(as_text=True))


class Reset(DemoTestCase):
    def test_reset_needs_typed_confirmation(self):
        self.login("admin")
        self.client.post("/settings/reset", data={"confirm_text": "yes"})
        # nothing was rebuilt, so the sign-in entry is still there
        self.assertEqual(self.query("SELECT COUNT(*) FROM activity_log WHERE action = 'Signed in'"), 1)

    def test_reset_restores_original_data(self):
        original = self.query("SELECT COUNT(*) FROM beneficiaries")
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM beneficiaries WHERE id <= 10")
        conn.commit(); conn.close()
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries"), original - 10)

        self.login("admin")
        r = self.client.post("/settings/reset", data={"confirm_text": "RESET"}, follow_redirects=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn("has been reset", r.get_data(as_text=True))
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries"), original)
        self.assertEqual(self.query("SELECT COUNT(*) FROM activity_log WHERE action = 'Demo reset'"), 1)


class HomeFiguresComeFromDatabase(DemoTestCase):
    def test_home_counts_match_and_update(self):
        self.login("management")
        n = self.query("SELECT COUNT(*) FROM beneficiaries")
        html = self.client.get("/home").get_data(as_text=True)
        self.assertRegex(html, rf'Beneficiaries</span><span class="stat-value">{n}<')

        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM beneficiaries WHERE id = 1")
        conn.commit(); conn.close()
        html = self.client.get("/home").get_data(as_text=True)
        self.assertRegex(html, rf'Beneficiaries</span><span class="stat-value">{n - 1}<')


class CsrfProtection(DemoTestCase):
    csrf = True

    def test_post_without_token_is_rejected(self):
        r = self.client.post("/login", data={"email": email_for("admin"), "password": DEMO_PASSWORD})
        self.assertEqual(r.status_code, 400)

    def test_post_with_token_is_accepted(self):
        page = self.client.get("/login").get_data(as_text=True)
        token = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
        r = self.client.post("/login", data={"email": email_for("admin"), "password": DEMO_PASSWORD,
                                             "csrf_token": token})
        self.assertEqual(r.status_code, 302)


class WorksOffline(unittest.TestCase):
    def test_no_external_urls_in_templates_css_or_js(self):
        found = []
        for folder in ("app/templates", "app/static/css", "app/static/js"):
            for f in (PROJECT / folder).rglob("*"):
                if f.is_file() and re.search(r"https?://", f.read_text(encoding="utf-8")):
                    found.append(str(f.relative_to(PROJECT)))
        self.assertEqual(found, [], "These files load something from the internet")


if __name__ == "__main__":
    unittest.main()
