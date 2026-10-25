"""Fictional sample data for the demo.

EVERYTHING HERE IS INVENTED. Names are random combinations of common first
and last names; they do not describe real people. Phone numbers are stored
masked, emails use the reserved "example.org" / ".example" domains, and all
reference numbers start with DEMO- or SIM-.

The random generator uses a fixed seed (2026), so a reset always produces the
same records. Dates are calculated relative to the day of the reset, so the
data always looks current during a presentation.
"""
import random
from datetime import date, datetime, timedelta

from werkzeug.security import generate_password_hash

from . import constants as C
from .permissions import ROLES

SEED = 2026
DEMO_PASSWORD = "Demo@2026"   # demo-only password shared by all fictional accounts
EMAIL_DOMAIN = "sfsha-demo.example"

# featured=True accounts appear as quick sign-in buttons on the login page.
DEMO_USERS = [
    {"name": "Grace Wanjiku",   "email": f"admin@{EMAIL_DOMAIN}",               "role": "admin",               "active": True,  "featured": True},
    {"name": "Brian Otieno",    "email": f"beneficiary.officer@{EMAIL_DOMAIN}", "role": "beneficiary_officer", "active": True,  "featured": True},
    {"name": "Mercy Chebet",    "email": f"mercy.chebet@{EMAIL_DOMAIN}",        "role": "beneficiary_officer", "active": True,  "featured": False},
    {"name": "Daniel Mwangi",   "email": f"programme.officer@{EMAIL_DOMAIN}",   "role": "programme_officer",   "active": True,  "featured": True},
    {"name": "Faith Akinyi",    "email": f"faith.akinyi@{EMAIL_DOMAIN}",        "role": "programme_officer",   "active": True,  "featured": False},
    {"name": "Kevin Kiprono",   "email": f"coverage.officer@{EMAIL_DOMAIN}",    "role": "coverage_officer",    "active": True,  "featured": True},
    {"name": "Lilian Nyambura", "email": f"lilian.nyambura@{EMAIL_DOMAIN}",     "role": "coverage_officer",    "active": True,  "featured": False},
    {"name": "Ruth Muthoni",    "email": f"management@{EMAIL_DOMAIN}",          "role": "management",          "active": True,  "featured": True},
    {"name": "Peter Omondi",    "email": f"peter.omondi@{EMAIL_DOMAIN}",        "role": "management",          "active": True,  "featured": False},
    {"name": "Former Demo Officer", "email": f"inactive.user@{EMAIL_DOMAIN}",   "role": "beneficiary_officer", "active": False, "featured": False},
]

# (code, name, description, discipline, focus group, status, start months ago, length in months)
PROGRAMMES = [
    ("DEMO-P01", "Grassroots Football Development (Demo)",
     "Fictional programme supporting emerging footballers in community leagues.",
     "Football", "Sportspersons & athletes", "Active", 16, 30),
    ("DEMO-P02", "Women in Athletics Support (Demo)",
     "Fictional programme supporting women distance and track athletes.",
     "Athletics", "Women & emerging athletes", "Active", 14, 24),
    ("DEMO-P03", "Coaches Capacity Building (Demo)",
     "Fictional training and welfare programme for coaches and technical personnel.",
     "Multi-discipline", "Coaches & technical personnel", "Active", 12, 24),
    ("DEMO-P04", "Match Officials Welfare (Demo)",
     "Fictional welfare programme for referees, judges and other match officials.",
     "Multi-discipline", "Officials & sports administrators", "Active", 10, 18),
    ("DEMO-P05", "Para-Sports Inclusion (Demo)",
     "Fictional inclusion programme for para-athletes and other eligible groups.",
     "Para-athletics", "Other eligible & vulnerable groups", "Active", 9, 24),
    ("DEMO-P06", "Volleyball Talent Pathway (Demo)",
     "Fictional talent identification pathway for young volleyball players.",
     "Volleyball", "Women & emerging athletes", "Active", 8, 18),
    ("DEMO-P07", "Youth Boxing Development (Demo)",
     "Fictional pilot that has finished its first cycle.",
     "Boxing", "Sportspersons & athletes", "Completed", 15, 12),
    ("DEMO-P08", "County Rugby Sevens Development (Demo)",
     "Fictional programme planned to start next quarter.",
     "Rugby", "Sportspersons & athletes", "Planned", -2, 18),
]

FIRST_NAMES_F = ["Achieng", "Wanjiru", "Chepkoech", "Nafula", "Akinyi", "Mwende", "Njeri", "Atieno",
                 "Jebet", "Kemunto", "Halima", "Zawadi", "Nyokabi", "Wairimu", "Cherono", "Auma",
                 "Faith", "Mercy", "Joy", "Esther", "Irene", "Lucy", "Sharon", "Brenda"]
FIRST_NAMES_M = ["Otieno", "Kiprotich", "Mutua", "Kamau", "Wafula", "Omondi", "Kiptoo", "Njoroge",
                 "Barasa", "Mohamed", "Juma", "Odhiambo", "Kibet", "Muriuki", "Ochieng", "Kirui",
                 "Brian", "Dennis", "Collins", "Victor", "Samuel", "Kevin", "Eric", "Joseph"]
LAST_NAMES = ["Mwangi", "Otieno", "Kiprono", "Wanjala", "Mutiso", "Onyango", "Chebet", "Kariuki",
              "Ndungu", "Abdi", "Wekesa", "Kimani", "Rotich", "Owino", "Maina", "Langat", "Nyaga",
              "Ouma", "Korir", "Mbugua", "Simiyu", "Kiplagat", "Muthoni", "Hassan", "Gitau", "Kosgei"]

# Counties weighted towards places with many sports programmes, so charts look varied but realistic.
COUNTY_WEIGHTS = {
    "Nairobi": 14, "Uasin Gishu": 10, "Elgeyo-Marakwet": 8, "Nakuru": 8, "Kisumu": 7,
    "Mombasa": 6, "Kakamega": 6, "Nandi": 6, "Kiambu": 5, "Machakos": 4, "Bungoma": 4,
    "Kericho": 3, "Nyeri": 3, "Kilifi": 3, "Kisii": 3, "Meru": 3, "Baringo": 3,
}

COVERAGE_NEXT_STEPS = {
    "Confirmed in demo": "No action needed in the demo. A real result would require authorised SHA verification.",
    "Pending review": "Re-check in the demo after the review period.",
    "Further action required": "Open an enrolment-support case and contact the beneficiary.",
    "Unable to confirm": "Check the beneficiary's details and open a verification follow-up case.",
}
SIMULATION_NOTE = "Simulated result generated for demonstration. Not verified by SHA."


def _ts(d, rng, start_hour=8, end_hour=17):
    """Turn a date into a timestamp text with a random working-hours time."""
    t = datetime(d.year, d.month, d.day, rng.randint(start_hour, end_hour - 1), rng.randint(0, 59), rng.randint(0, 59))
    return t.strftime("%Y-%m-%d %H:%M:%S")


def _months_ago(today, months):
    return today - timedelta(days=int(months * 30.4))


def seed_demo_data(conn):
    rng = random.Random(SEED)
    today = date.today()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------- roles ----------
    role_ids = {}
    for key, role in ROLES.items():
        cur = conn.execute(
            "INSERT INTO roles (key, name, description) VALUES (?, ?, ?)",
            (key, role["name"], role["description"]),
        )
        role_ids[key] = cur.lastrowid

    # ---------- users ----------
    user_ids = {}
    for u in DEMO_USERS:
        cur = conn.execute(
            "INSERT INTO users (full_name, email, password_hash, role_id, is_active, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (u["name"], u["email"], generate_password_hash(DEMO_PASSWORD),
             role_ids[u["role"]], 1 if u["active"] else 0, now),
        )
        user_ids.setdefault(u["role"], []).append((cur.lastrowid, u["active"]))
    admin_id = user_ids["admin"][0][0]
    bo_ids = [i for i, a in user_ids["beneficiary_officer"] if a]
    po_ids = [i for i, a in user_ids["programme_officer"] if a]
    co_ids = [i for i, a in user_ids["coverage_officer"] if a]

    # ---------- programmes ----------
    programmes = []
    for code, name, desc, disc, focus, status, start_ago, length in PROGRAMMES:
        start = _months_ago(today, start_ago)
        end = start + timedelta(days=int(length * 30.4))
        cur = conn.execute(
            "INSERT INTO programmes (code, name, description, discipline, focus_group, status,"
            " start_date, end_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (code, name, desc, disc, focus, status, start.isoformat(), end.isoformat(), now),
        )
        programmes.append({"id": cur.lastrowid, "code": code, "discipline": disc, "focus": focus,
                           "status": status, "start": start, "end": end})
    open_programmes = [p for p in programmes if p["status"] != "Planned"]
    prog_weights = [5, 5, 3, 3, 2, 3, 2][: len(open_programmes)]

    counties = list(COUNTY_WEIGHTS) + [c for c in C.COUNTIES if c not in COUNTY_WEIGHTS]
    county_w = list(COUNTY_WEIGHTS.values()) + [1] * (len(C.COUNTIES) - len(COUNTY_WEIGHTS))

    # ---------- beneficiaries + participations ----------
    beneficiaries = []
    used_names = set()
    for n in range(1, 161):
        prog = rng.choices(open_programmes, weights=prog_weights)[0]
        if prog["focus"] == "Women & emerging athletes":
            gender = "Female"
        else:
            gender = rng.choices(["Female", "Male", "Not recorded"], weights=[44, 53, 3])[0]
        category = prog["focus"] if rng.random() < 0.85 else rng.choice(C.CATEGORIES)
        if category == "Women & emerging athletes" and gender == "Male":
            category = "Sportspersons & athletes"
        discipline = prog["discipline"] if prog["discipline"] in C.DISCIPLINES else rng.choice(C.DISCIPLINES)

        while True:
            first = rng.choice(FIRST_NAMES_F if gender == "Female" else
                               FIRST_NAMES_M if gender == "Male" else FIRST_NAMES_F + FIRST_NAMES_M)
            last = rng.choice(LAST_NAMES)
            if (first, last) not in used_names:
                used_names.add((first, last))
                break

        earliest = max(prog["start"], today - timedelta(days=420))
        span = max((min(prog["end"], today) - earliest).days, 1)
        reg = earliest + timedelta(days=rng.randint(0, span))
        age_days = (today - reg).days
        if age_days < 21:
            status = rng.choices(C.REGISTRATION_STATUSES, weights=[70, 30, 0])[0]
        else:
            status = rng.choices(C.REGISTRATION_STATUSES, weights=[4, 89, 7])[0]
        consent = 1 if status != "Pending validation" or rng.random() < 0.5 else 0
        ref = f"DEMO-BEN-{n:04d}"
        cur = conn.execute(
            "INSERT INTO beneficiaries (demo_ref, first_name, last_name, gender, category, discipline,"
            " county, phone_masked, email, registration_date, status, consent_recorded, consent_date,"
            " validated_by, notes, created_by, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ref, first, last, gender, category, discipline,
             rng.choices(counties, weights=county_w)[0],
             f"07•• ••• {rng.randint(100, 999)}",
             f"{first}.{last}.{n}@example.org".lower() if rng.random() < 0.6 else None,
             reg.isoformat(), status, consent, reg.isoformat() if consent else None,
             f"{discipline} Federation (fictional)" if status != "Pending validation" else None,
             "Fictional demo record.", rng.choice(bo_ids), _ts(reg, rng), _ts(reg, rng)),
        )
        b = {"id": cur.lastrowid, "ref": ref, "reg": reg, "status": status, "programmes": [prog]}
        conn.execute(
            "INSERT INTO participations (beneficiary_id, programme_id, joined_on, status) VALUES (?, ?, ?, ?)",
            (b["id"], prog["id"], reg.isoformat(),
             "Completed" if prog["status"] == "Completed" else ("Withdrawn" if status == "Inactive" else "Active")),
        )
        if rng.random() < 0.18:   # some people take part in a second programme
            other = rng.choice([p for p in open_programmes if p is not prog and p["status"] == "Active"])
            joined = max(reg, other["start"]) + timedelta(days=rng.randint(0, 60))
            if joined <= today:
                conn.execute(
                    "INSERT INTO participations (beneficiary_id, programme_id, joined_on, status) VALUES (?, ?, ?, ?)",
                    (b["id"], other["id"], joined.isoformat(), "Active"),
                )
                b["programmes"].append(other)
        beneficiaries.append(b)

    # ---------- simulated coverage checks ----------
    check_no = 0

    def add_check(b, outcome, when):
        nonlocal check_no
        check_no += 1
        actor = rng.choice(co_ids)
        stamp = _ts(when, rng)
        cur = conn.execute(
            "INSERT INTO coverage_checks (beneficiary_id, outcome, sample_ref, checked_at, checked_by,"
            " note, next_step, is_simulated) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
            (b["id"], outcome, f"SIM-CHK-{check_no:05d}", stamp, actor, SIMULATION_NOTE,
             COVERAGE_NEXT_STEPS[outcome]),
        )
        conn.execute(
            "INSERT INTO activity_log (actor_id, action, entity_type, entity_id, summary, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (actor, "Simulated coverage check", "beneficiary", b["id"],
             f"{b['ref']}: simulated outcome '{outcome}'", stamp),
        )
        return cur.lastrowid

    for b in beneficiaries:
        b["outcome"] = None
        if b["status"] == "Pending validation" or rng.random() > 0.82:
            continue
        final = rng.choices(C.COVERAGE_OUTCOMES, weights=[56, 14, 20, 10])[0]
        first_day = b["reg"] + timedelta(days=rng.randint(1, 20))
        if first_day > today:
            first_day = today
        if final == "Confirmed in demo" and rng.random() < 0.3:
            add_check(b, rng.choice(["Pending review", "Further action required"]), first_day)
            first_day = min(first_day + timedelta(days=rng.randint(10, 40)), today)
        add_check(b, final, first_day)
        b["outcome"] = final
        b["checked_on"] = first_day

    # ---------- follow-up cases with history ----------
    case_no = 0
    titles = {
        "Enrolment support": "Support beneficiary to complete enrolment",
        "Coverage verification follow-up": "Follow up unconfirmed coverage result",
        "Record correction": "Correct registration details",
        "Consent & documentation": "Obtain consent record and documents",
        "Facility access guidance": "Provide guidance on accessing an accredited facility",
    }

    def add_case(b, category, opened):
        nonlocal case_no
        case_no += 1
        opened = min(opened, today)
        creator = rng.choice(bo_ids + co_ids)
        assignee = rng.choice(co_ids if category in ("Enrolment support", "Coverage verification follow-up") else bo_ids + po_ids)
        age = (today - opened).days
        if age > 45:
            status = rng.choices(C.CASE_STATUSES, weights=[8, 10, 12, 70])[0]
        elif age > 14:
            status = rng.choices(C.CASE_STATUSES, weights=[20, 35, 20, 25])[0]
        else:
            status = rng.choices(C.CASE_STATUSES, weights=[55, 30, 10, 5])[0]
        priority = rng.choices(C.CASE_PRIORITIES, weights=[25, 50, 25])[0]
        due = opened + timedelta(days={"High": 7, "Medium": 14, "Low": 30}[priority])
        created = _ts(opened, rng)
        resolved_at = None
        if status == "Resolved":
            resolved_day = min(opened + timedelta(days=rng.randint(3, 40)), today)
            resolved_at = _ts(resolved_day, rng)
            if resolved_at < created:
                resolved_at = created
        ref = f"DEMO-CASE-{case_no:04d}"
        cur = conn.execute(
            "INSERT INTO follow_up_cases (case_ref, beneficiary_id, programme_id, category, priority, status,"
            " title, description, due_date, assigned_to, created_by, created_at, resolved_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ref, b["id"], b["programmes"][0]["id"], category, priority, status, titles[category],
             "Fictional follow-up case created for the demonstration.", due.isoformat(),
             assignee, creator, created, resolved_at),
        )
        case_id = cur.lastrowid

        def act(kind, when, note=None, frm=None, to=None, actor=assignee):
            conn.execute(
                "INSERT INTO case_activities (case_id, actor_id, kind, from_status, to_status, note, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)", (case_id, actor, kind, frm, to, note, when))

        act("Created", created, "Case opened in the demo.", None, "Open", creator)
        act("Assigned", created, "Assigned to a demo officer.", actor=creator)
        conn.execute(
            "INSERT INTO activity_log (actor_id, action, entity_type, entity_id, summary, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (creator, "Case created", "case", case_id, f"{ref} opened for {b['ref']} ({category})", created))
        path = {"Open": [], "In progress": ["In progress"],
                "Awaiting information": ["In progress", "Awaiting information"],
                "Resolved": ["In progress", "Resolved"]}[status]
        prev, step_day = "Open", opened
        for nxt in path:
            step_day = min(step_day + timedelta(days=rng.randint(1, 6)), today)
            when = resolved_at if nxt == "Resolved" else _ts(step_day, rng)
            act("Note", when, rng.choice([
                "Called the beneficiary (demo) and explained next steps.",
                "Requested missing details from the programme coordinator (demo).",
                "Shared guidance on the agreed enrolment process (demo).",
            ]))
            act("Status change", when, None, prev, nxt)
            prev = nxt
        return case_id

    for b in beneficiaries:
        if b["outcome"] in ("Further action required", "Unable to confirm") and rng.random() < 0.9:
            cat = "Enrolment support" if b["outcome"] == "Further action required" else "Coverage verification follow-up"
            add_case(b, cat, b["checked_on"] + timedelta(days=rng.randint(0, 3)))
        elif b["status"] == "Pending validation" and rng.random() < 0.5:
            add_case(b, rng.choice(["Record correction", "Consent & documentation"]), b["reg"] + timedelta(days=rng.randint(0, 5)))
        elif b["outcome"] == "Confirmed in demo" and rng.random() < 0.07:
            add_case(b, "Facility access guidance", b["checked_on"] + timedelta(days=rng.randint(5, 30)))

    # ---------- simulated referrals / guidance ----------
    facilities = [f"Sample Health Facility {i:02d} (fictional)" for i in range(1, 9)]
    confirmed = [b for b in beneficiaries if b["outcome"] == "Confirmed in demo"]
    for n, b in enumerate(rng.sample(confirmed, min(30, len(confirmed))), start=1):
        when = min(b["checked_on"] + timedelta(days=rng.randint(2, 60)), today)
        status = rng.choices(C.REFERRAL_STATUSES, weights=[35, 25, 40])[0]
        conn.execute(
            "INSERT INTO referrals (referral_ref, beneficiary_id, category, facility_name, status, notes,"
            " next_action, created_by, created_at, is_simulated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (f"DEMO-REF-{n:04d}", b["id"], rng.choices(C.REFERRAL_CATEGORIES, weights=[60, 20, 20])[0],
             rng.choice(facilities), status,
             "Simulated guidance record. Nothing was sent to any facility or institution.",
             "None" if status == "Completed in demo" else "Confirm with the beneficiary that the guidance was helpful.",
             rng.choice(co_ids), _ts(when, rng)),
        )

    # ---------- fictional financial records ----------
    txn_no = 0
    activity_names = ["Training camp", "Registration drive", "Equipment issue", "Coaching clinic",
                      "Competition support", "Outreach session"]
    for p in programmes:
        txn_no += 1
        allocation = rng.randrange(4_000_000, 18_000_001, 250_000)
        conn.execute(
            "INSERT INTO financial_records (txn_ref, programme_id, entry_type, category, description,"
            " amount_kes, entry_date, linked_activity, recorded_by, created_at)"
            " VALUES (?, ?, 'Allocation', 'Programme administration', ?, ?, ?, ?, ?, ?)",
            (f"DEMO-TXN-{txn_no:05d}", p["id"], "Fictional annual budget allocation",
             allocation, p["start"].isoformat() if p["start"] <= today else today.isoformat(),
             "Approved programme budget (demo)", rng.choice(po_ids), now),
        )
        if p["status"] == "Planned":
            continue
        target = allocation * (rng.uniform(0.9, 0.98) if p["status"] == "Completed" else rng.uniform(0.4, 0.8))
        count = rng.randint(10, 18)
        shares = [rng.random() for _ in range(count)]
        last_day = min(p["end"], today)
        for share in shares:
            txn_no += 1
            amount = max(int(target * share / sum(shares) / 1000) * 1000, 5_000)
            day = p["start"] + timedelta(days=rng.randint(0, max((last_day - p["start"]).days, 1)))
            category = rng.choice(C.FINANCE_CATEGORIES)
            linked = (f"{rng.choice(activity_names)} – {rng.choices(counties, weights=county_w)[0]} (demo)"
                      if rng.random() < 0.88 else None)   # ~12% deliberately unlinked for the §7 check
            conn.execute(
                "INSERT INTO financial_records (txn_ref, programme_id, entry_type, category, description,"
                " amount_kes, entry_date, linked_activity, recorded_by, created_at)"
                " VALUES (?, ?, 'Expenditure', ?, ?, ?, ?, ?, ?, ?)",
                (f"DEMO-TXN-{txn_no:05d}", p["id"], category, f"Fictional expenditure: {category.lower()}",
                 amount, day.isoformat(), linked, rng.choice(po_ids), now),
            )

    conn.execute(
        "INSERT INTO activity_log (actor_id, action, entity_type, entity_id, summary, created_at)"
        " VALUES (?, 'Demo data loaded', NULL, NULL, ?, ?)",
        (admin_id, "Fictional sample dataset created", now),
    )
