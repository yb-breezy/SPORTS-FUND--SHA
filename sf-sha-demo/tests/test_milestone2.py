"""Automated checks for milestone 2: the beneficiary register.

Run all tests from the project folder:   python -m unittest discover -s tests -t . -v
"""
from datetime import date, timedelta

from tests.test_milestone1 import DemoTestCase


def valid_form(**changes):
    """A complete, valid set of fictional form values. Pass changes to break one field."""
    form = {
        "first_name": "Zuri", "last_name": "Testcase", "gender": "Female", "county": "Nakuru",
        "phone": "0712345678", "email": "zuri.test@example.org",
        "category": "Women & emerging athletes", "discipline": "Athletics",
        "programme_id": "2", "registration_date": date.today().isoformat(),
        "status": "Registered", "consent_recorded": "on", "notes": "Created by an automated test.",
    }
    form.update(changes)
    return {k: v for k, v in form.items() if v is not None}


class ListSearchFilter(DemoTestCase):
    def setUp(self):
        super().setUp()
        self.login("management")

    def test_list_shows_first_page_of_20(self):
        html = self.client.get("/beneficiaries/").get_data(as_text=True)
        self.assertIn("160 beneficiaries", html)
        self.assertIn("Showing 1–20 of 160", html)
        self.assertEqual(html.count('class="row-link"'), 20)

    def test_last_page(self):
        html = self.client.get("/beneficiaries/?page=8").get_data(as_text=True)
        self.assertIn("Showing 141–160 of 160", html)
        self.assertNotIn("Next →", html)

    def test_bad_page_number_is_handled(self):
        self.assertEqual(self.client.get("/beneficiaries/?page=abc").status_code, 200)
        self.assertIn("Page 8 of 8", self.client.get("/beneficiaries/?page=999").get_data(as_text=True))

    def test_search_by_reference(self):
        html = self.client.get("/beneficiaries/?q=DEMO-BEN-0007").get_data(as_text=True)
        self.assertIn("1 beneficiary", html)
        self.assertIn("DEMO-BEN-0007", html)

    def test_search_by_full_name(self):
        first, last = self.query("SELECT first_name || '|' || last_name FROM beneficiaries WHERE id = 5").split("|")
        html = self.client.get(f"/beneficiaries/?q={first} {last}").get_data(as_text=True)
        self.assertIn("DEMO-BEN-0005", html)

    def test_search_wildcards_are_treated_as_text(self):
        html = self.client.get("/beneficiaries/?q=%25").get_data(as_text=True)   # a literal "%"
        self.assertIn("No beneficiaries match", html)

    def test_filters_match_database_counts(self):
        cases = {
            "status=Pending+validation": "SELECT COUNT(*) FROM beneficiaries WHERE status = 'Pending validation'",
            "county=Nairobi": "SELECT COUNT(*) FROM beneficiaries WHERE county = 'Nairobi'",
            "programme=2": "SELECT COUNT(*) FROM participations WHERE programme_id = 2",
            "coverage=none": "SELECT COUNT(*) FROM beneficiaries b WHERE NOT EXISTS "
                             "(SELECT 1 FROM coverage_checks c WHERE c.beneficiary_id = b.id)",
        }
        for query, sql in cases.items():
            with self.subTest(filter=query):
                expected = self.query(sql)
                html = self.client.get(f"/beneficiaries/?{query}").get_data(as_text=True)
                self.assertRegex(html, rf"<strong>{expected} beneficiar")

    def test_filters_combine_and_survive_paging(self):
        html = self.client.get("/beneficiaries/?status=Registered&page=1").get_data(as_text=True)
        self.assertIn("status=Registered", html)   # the Next link keeps the filter

    def test_unknown_filter_values_are_ignored_safely(self):
        r = self.client.get("/beneficiaries/?status=';DROP TABLE beneficiaries;--")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries"), 160)


class Register(DemoTestCase):
    def setUp(self):
        super().setUp()
        self.login("beneficiary_officer")

    def test_register_valid_beneficiary(self):
        r = self.client.post("/beneficiaries/new", data=valid_form())
        self.assertEqual(r.status_code, 302)
        self.assertIn("/beneficiaries/161", r.headers["Location"])
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries"), 161)
        self.assertEqual(self.query("SELECT demo_ref FROM beneficiaries WHERE id = 161"), "DEMO-BEN-0161")
        self.assertEqual(self.query("SELECT phone_masked FROM beneficiaries WHERE id = 161"), "07•• ••• 678")
        self.assertEqual(self.query("SELECT programme_id FROM participations WHERE beneficiary_id = 161"), 2)
        self.assertEqual(self.query("SELECT COUNT(*) FROM activity_log WHERE action = 'Beneficiary registered'"), 1)

        profile = self.client.get(r.headers["Location"]).get_data(as_text=True)
        self.assertIn("Zuri Testcase", profile)
        self.assertIn("was registered", profile)
        home = self.client.get("/home").get_data(as_text=True)
        self.assertRegex(home, r'Beneficiaries</span><span class="stat-value">161<')
        listing = self.client.get("/beneficiaries/?q=Testcase").get_data(as_text=True)
        self.assertIn("DEMO-BEN-0161", listing)

    def test_invalid_inputs_are_rejected_with_messages(self):
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        bad = {
            "missing first name": ({"first_name": ""}, "First name is required"),
            "digits in name": ({"last_name": "R2D2"}, "must be 2–60 letters"),
            "bad email": ({"email": "not-an-email"}, "valid email"),
            "bad phone": ({"phone": "12345"}, "Kenyan mobile"),
            "future date": ({"registration_date": tomorrow}, "cannot be in the future"),
            "unknown county": ({"county": "Atlantis"}, "county from the list"),
            "no consent but registered": ({"consent_recorded": None}, "Record consent"),
            "planned programme": ({"programme_id": "8"}, "Active programme"),
            "missing programme": ({"programme_id": ""}, "Choose the programme"),
            "notes too long": ({"notes": "x" * 501}, "500 characters"),
        }
        for label, (change, message) in bad.items():
            with self.subTest(case=label):
                r = self.client.post("/beneficiaries/new", data=valid_form(**change))
                self.assertEqual(r.status_code, 400)
                self.assertIn(message, r.get_data(as_text=True))
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries"), 160)

    def test_typed_values_are_kept_after_an_error(self):
        r = self.client.post("/beneficiaries/new", data=valid_form(email="bad"))
        self.assertIn('value="Zuri"', r.get_data(as_text=True))

    def test_duplicate_name_in_same_county_is_flagged(self):
        first, last, county = self.query(
            "SELECT first_name || '|' || last_name || '|' || county FROM beneficiaries WHERE id = 3").split("|")
        r = self.client.post("/beneficiaries/new", data=valid_form(first_name=first, last_name=last, county=county))
        self.assertEqual(r.status_code, 400)
        self.assertIn("already exists", r.get_data(as_text=True))

    def test_pending_without_consent_is_allowed(self):
        r = self.client.post("/beneficiaries/new",
                             data=valid_form(status="Pending validation", consent_recorded=None))
        self.assertEqual(r.status_code, 302)

    def test_html_in_notes_is_shown_as_text_not_run(self):
        r = self.client.post("/beneficiaries/new", data=valid_form(notes="<script>alert(1)</script>"))
        html = self.client.get(r.headers["Location"]).get_data(as_text=True)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)


class EditAndProfile(DemoTestCase):
    def test_edit_updates_record_and_logs_changes(self):
        self.login("beneficiary_officer")
        form = self.client.get("/beneficiaries/10/edit").get_data(as_text=True)
        self.assertIn("Edit DEMO-BEN-0010", form)
        current = dict(zip(
            ["first_name", "last_name", "gender", "county", "category", "discipline", "registration_date", "status"],
            self.query("SELECT first_name||'|'||last_name||'|'||gender||'|'||county||'|'||category||'|'||"
                       "discipline||'|'||registration_date||'|'||status FROM beneficiaries WHERE id = 10").split("|")))
        current.update({"county": "Kisumu", "status": "Registered", "consent_recorded": "on"})
        r = self.client.post("/beneficiaries/10/edit", data=current)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.query("SELECT county FROM beneficiaries WHERE id = 10"), "Kisumu")
        summary = self.query("SELECT summary FROM activity_log WHERE action = 'Beneficiary updated'")
        self.assertIn("county", summary)
        # phone left blank keeps the existing masked number
        self.assertIsNotNone(self.query("SELECT phone_masked FROM beneficiaries WHERE id = 10"))

    def test_saving_without_changes_says_so(self):
        self.login("admin")
        row = self.query("SELECT first_name||'|'||last_name||'|'||gender||'|'||county||'|'||category||'|'||"
                         "discipline||'|'||registration_date||'|'||status||'|'||consent_recorded||'|'||"
                         "coalesce(notes,'')||'|'||coalesce(email,'') FROM beneficiaries WHERE id = 20").split("|")
        keys = ["first_name", "last_name", "gender", "county", "category", "discipline",
                "registration_date", "status", "consent_recorded", "notes", "email"]
        data = dict(zip(keys, row))
        data["consent_recorded"] = "on" if data["consent_recorded"] == "1" else ""
        r = self.client.post("/beneficiaries/20/edit", data=data, follow_redirects=True)
        self.assertIn("No changes were made", r.get_data(as_text=True))

    def test_profile_shows_all_sections_and_simulation_labels(self):
        self.login("management")
        bid = self.query("SELECT beneficiary_id FROM follow_up_cases LIMIT 1")
        html = self.client.get(f"/beneficiaries/{bid}").get_data(as_text=True)
        for heading in ("Basic information", "Registration details", "Programme participation",
                        "Coverage-coordination history", "Follow-up cases", "Referral and support history",
                        "Activity history"):
            self.assertIn(heading, html)
        self.assertIn("not verified by SHA", html)
        self.assertNotIn("Edit record", html)   # management is view-only

    def test_missing_profile_is_404(self):
        self.login("management")
        self.assertEqual(self.client.get("/beneficiaries/99999").status_code, 404)


class Permissions(DemoTestCase):
    def test_view_only_and_other_roles_cannot_change_records(self):
        for role in ("management", "programme_officer", "coverage_officer"):
            with self.subTest(role=role):
                self.login(role)
                self.assertEqual(self.client.get("/beneficiaries/new").status_code, 403)
                self.assertEqual(self.client.post("/beneficiaries/new", data=valid_form()).status_code, 403)
                self.assertEqual(self.client.get("/beneficiaries/1/edit").status_code, 403)
                self.assertEqual(self.client.post("/beneficiaries/1/edit", data=valid_form()).status_code, 403)
                self.assertNotIn("+ Add beneficiary", self.client.get("/beneficiaries/").get_data(as_text=True))
                self.client.post("/logout")
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries"), 160)

    def test_signed_out_visitors_are_sent_to_login(self):
        r = self.client.get("/beneficiaries/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login", r.headers["Location"])

    def test_menu_link_is_live(self):
        self.login("beneficiary_officer")
        html = self.client.get("/home").get_data(as_text=True)
        self.assertIn('href="/beneficiaries/"', html)


class ResetAfterChanges(DemoTestCase):
    def test_reset_removes_beneficiaries_added_during_demo(self):
        self.login("admin")
        self.client.post("/beneficiaries/new", data=valid_form())
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries"), 161)
        self.client.post("/settings/reset", data={"confirm_text": "RESET"})
        self.assertEqual(self.query("SELECT COUNT(*) FROM beneficiaries"), 160)
