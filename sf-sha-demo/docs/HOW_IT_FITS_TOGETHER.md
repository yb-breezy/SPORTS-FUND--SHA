# How the code fits together (a guided tour)

Read this alongside the code in VS Code. Open each file as it is mentioned.

## The project folder

```
sf-sha-demo/
├── run.py                  ← START HERE: "python run.py" starts the website
├── requirements.txt        ← the one package to install (Flask)
├── app/
│   ├── __init__.py         ← create_app(): wires everything together
│   ├── constants.py        ← fixed lists (groups, counties, statuses) + demo notice text
│   ├── permissions.py      ← the 5 proposed roles and what each may do
│   ├── schema.sql          ← the database tables, in plain SQL
│   ├── seed.py             ← creates the fictional sample data
│   ├── db.py               ← open/close the database, rebuild it, write the activity log
│   ├── security.py         ← who is signed in, permission checks, CSRF protection
│   ├── auth.py             ← /login and /logout pages
│   ├── main.py             ← /, /home, /settings, /settings/reset
│   ├── beneficiaries.py    ← M2: /beneficiaries list, /new, /<id> profile, /<id>/edit
│   ├── validation.py       ← M2: server-side checks for the beneficiary form
│   ├── templates/          ← HTML pages (Jinja templates)
│   │   ├── base.html           outer shell + demo banner (every page)
│   │   ├── app_layout.html     sidebar + top bar (signed-in pages)
│   │   ├── landing.html, auth/login.html, main/home.html, main/settings.html
│   │   ├── beneficiaries/      list.html, form.html (add + edit), profile.html
│   │   ├── errors/error.html   friendly 400/403/404/500 page
│   │   └── partials/           _flash.html messages, _macros.html badges, _pagination.html
│   └── static/
│       ├── css/app.css     ← the whole design system
│       └── js/app.js       ← small browser helpers (fill demo login, confirm reset, validation, mobile menu)
├── instance/               ← created automatically: demo.db (the database) + secret_key
├── tests/                ← test_milestone1.py, test_milestone2.py
└── docs/                   ← this documentation
```

## Following one request: "show me the Home page"

1. **You type** `http://127.0.0.1:5000/home`. Your browser sends a request to the Flask server started by `run.py`.
2. **`run.py`** called `create_app()` in **`app/__init__.py`** when it started. That function registered two "before every request" checks and the routes.
3. **Before the route runs**, `check_csrf` (in `security.py`) checks forms, then `load_logged_in_user` reads the signed cookie and loads the user from the `users` table into `g.user`.
4. **Flask finds the route** for `/home`: the `home()` function in **`app/main.py`**. It has `@login_required` above it. If `g.user` is empty you are sent to `/login`.
5. **`home()` runs SQL** through `get_db()` (in **`db.py`**): it counts rows in each table and groups beneficiaries by category. These numbers are never typed in by hand.
6. **`render_template("main/home.html", counts=…)`** fills the template. `home.html` says `{% extends "app_layout.html" %}`, which extends `base.html`, so you get banner + sidebar + top bar + this page's content.
7. **The browser** receives the HTML and loads `/static/css/app.css` and `/static/js/app.js` from your own laptop, so no internet is needed.

## Following a protected action: "Reset demo data"

1. In **`settings.html`**, the reset form only appears if `can("reset_demo")` is true. That hides it from other roles **for tidiness only**.
2. Submitting sends a POST to `/settings/reset`, including the hidden `csrf_token`.
3. In **`main.py`**, `reset_demo()` has `@permission_required("reset_demo")`. **This is the real protection**: if a non-admin sends the request anyway, the server answers 403. A test proves this.
4. It checks you typed `RESET`, then `rebuild_database()` (in `db.py`) runs `schema.sql` (drop and recreate tables) and `seed.py` (reload the fictional data), then writes a "Demo reset" line to `activity_log`.

## Where to look when you want to change…

| I want to change… | Edit |
|---|---|
| The demo notice wording | `app/constants.py` → `DEMO_NOTICE` |
| What a role is allowed to do | `app/permissions.py` → `ROLES` |
| Colours, spacing, fonts | `app/static/css/app.css` → `:root` tokens at the top |
| The sidebar menu | `app/__init__.py` → `NAV_ITEMS` |
| How many sample beneficiaries there are | `app/seed.py` → `range(1, 161)` then reset the demo |
| A table's columns | `app/schema.sql`, then reset the demo |

## Following a form: "Register a beneficiary" (milestone 2)

1. **`list.html`** shows the **+ Add beneficiary** button only if `can("edit_beneficiaries")`.
2. It links to `/beneficiaries/new`, handled by `new_beneficiary()` in **`beneficiaries.py`**. `@permission_required("edit_beneficiaries")` refuses other roles with a 403.
3. **GET** shows the empty **`form.html`**. When you click *Register*, **`app.js`** first checks the boxes in the browser (required fields, name pattern, email format, date not in the future).
4. The browser **POSTs** the form. The server runs **`validate_beneficiary()`** in **`validation.py`** — the same rules again, plus ones a browser can't check (is the programme Active? is this a likely duplicate? is consent recorded before "Registered"?).
5. **If anything is wrong** the form comes back with the typed values kept and a red message under each problem field (status 400).
6. **If everything is right**, it works out the next `DEMO-BEN-` number, `INSERT`s into `beneficiaries` and `participations`, writes a line to `activity_log`, `commit()`s, and redirects to the new profile with a green message.
7. Because the Home page counts rows live, its Beneficiaries number goes up by one automatically.

The phone number you type is never stored in full: `mask_phone()` keeps only the last 3 digits.
