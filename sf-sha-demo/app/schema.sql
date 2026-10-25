-- =====================================================================
-- Sports Fund–SHA Beneficiary Management Demo — database schema
-- DEMONSTRATION ONLY. Every row in this database is fictional.
--
-- How to read this file:
--   * Each CREATE TABLE makes one table (like one sheet in a spreadsheet).
--   * "id INTEGER PRIMARY KEY" gives every row a unique number.
--   * "REFERENCES other_table(id)" is a FOREIGN KEY: it links a row to a row
--     in another table, and SQLite refuses links to rows that don't exist.
--   * "CHECK (...)" makes SQLite refuse values that are not in the allowed list.
--   * Dates are stored as text in ISO format: '2026-10-25' or '2026-10-25 14:30:00'.
-- Running this file deletes and recreates every table (used by "reset demo").
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS activity_log;
DROP TABLE IF EXISTS financial_records;
DROP TABLE IF EXISTS referrals;
DROP TABLE IF EXISTS case_activities;
DROP TABLE IF EXISTS follow_up_cases;
DROP TABLE IF EXISTS coverage_checks;
DROP TABLE IF EXISTS participations;
DROP TABLE IF EXISTS beneficiaries;
DROP TABLE IF EXISTS programmes;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

-- Proposed demo roles. Their permissions live in app/permissions.py.
CREATE TABLE roles (
    id          INTEGER PRIMARY KEY,
    key         TEXT NOT NULL UNIQUE,          -- short code used in Python, e.g. 'admin'
    name        TEXT NOT NULL,                 -- label shown on screen
    description TEXT NOT NULL
);

-- Fictional staff accounts. Passwords are stored only as secure hashes.
CREATE TABLE users (
    id            INTEGER PRIMARY KEY,
    full_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id       INTEGER NOT NULL REFERENCES roles(id),
    is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at    TEXT NOT NULL
);

-- Fictional Sports Fund programmes.
CREATE TABLE programmes (
    id          INTEGER PRIMARY KEY,
    code        TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    description TEXT NOT NULL,
    discipline  TEXT NOT NULL,
    focus_group TEXT NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('Planned', 'Active', 'Completed')),
    start_date  TEXT NOT NULL,
    end_date    TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

-- The beneficiary registry (concept note §3.3 objective 1).
-- Deliberately NO clinical/medical fields and NO national ID (data minimisation, §9).
CREATE TABLE beneficiaries (
    id                INTEGER PRIMARY KEY,
    demo_ref          TEXT NOT NULL UNIQUE,     -- e.g. DEMO-BEN-0001
    first_name        TEXT NOT NULL,
    last_name         TEXT NOT NULL,
    gender            TEXT NOT NULL CHECK (gender IN ('Female', 'Male', 'Not recorded')),
    category          TEXT NOT NULL CHECK (category IN (
                          'Sportspersons & athletes',
                          'Coaches & technical personnel',
                          'Officials & sports administrators',
                          'Women & emerging athletes',
                          'Other eligible & vulnerable groups')),
    discipline        TEXT NOT NULL,
    county            TEXT NOT NULL,
    phone_masked      TEXT,                     -- shown masked on purpose, e.g. 07•• ••• 482
    email             TEXT,
    registration_date TEXT NOT NULL,
    status            TEXT NOT NULL CHECK (status IN ('Pending validation', 'Registered', 'Inactive')),
    consent_recorded  INTEGER NOT NULL DEFAULT 0 CHECK (consent_recorded IN (0, 1)),
    consent_date      TEXT,
    validated_by      TEXT,                     -- fictional federation that validated the record
    notes             TEXT,
    created_by        INTEGER REFERENCES users(id),
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
);

-- Which beneficiary takes part in which programme (many-to-many link table).
CREATE TABLE participations (
    id             INTEGER PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,
    programme_id   INTEGER NOT NULL REFERENCES programmes(id) ON DELETE CASCADE,
    joined_on      TEXT NOT NULL,
    status         TEXT NOT NULL CHECK (status IN ('Active', 'Completed', 'Withdrawn')),
    UNIQUE (beneficiary_id, programme_id)
);

-- SIMULATED coverage checks. is_simulated can ONLY be 1 — the database itself
-- refuses to store a "real" verification result in this demo.
CREATE TABLE coverage_checks (
    id             INTEGER PRIMARY KEY,
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,
    outcome        TEXT NOT NULL CHECK (outcome IN (
                       'Confirmed in demo', 'Pending review',
                       'Further action required', 'Unable to confirm')),
    sample_ref     TEXT NOT NULL UNIQUE,        -- e.g. SIM-CHK-00001
    checked_at     TEXT NOT NULL,
    checked_by     INTEGER REFERENCES users(id),
    note           TEXT,
    next_step      TEXT,
    is_simulated   INTEGER NOT NULL DEFAULT 1 CHECK (is_simulated = 1)
);

-- Follow-up / enrolment-support cases (concept note §4 "Enrolment support").
CREATE TABLE follow_up_cases (
    id             INTEGER PRIMARY KEY,
    case_ref       TEXT NOT NULL UNIQUE,        -- e.g. DEMO-CASE-0001
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,
    programme_id   INTEGER REFERENCES programmes(id),
    category       TEXT NOT NULL CHECK (category IN (
                       'Enrolment support', 'Coverage verification follow-up',
                       'Record correction', 'Consent & documentation',
                       'Facility access guidance')),
    priority       TEXT NOT NULL CHECK (priority IN ('Low', 'Medium', 'High')),
    status         TEXT NOT NULL CHECK (status IN ('Open', 'In progress', 'Awaiting information', 'Resolved')),
    title          TEXT NOT NULL,
    description    TEXT,
    due_date       TEXT,
    assigned_to    INTEGER REFERENCES users(id),
    created_by     INTEGER REFERENCES users(id),
    created_at     TEXT NOT NULL,
    resolved_at    TEXT
);

-- The history of each case: created, assigned, status changes, notes.
CREATE TABLE case_activities (
    id          INTEGER PRIMARY KEY,
    case_id     INTEGER NOT NULL REFERENCES follow_up_cases(id) ON DELETE CASCADE,
    actor_id    INTEGER REFERENCES users(id),
    kind        TEXT NOT NULL CHECK (kind IN ('Created', 'Assigned', 'Status change', 'Note')),
    from_status TEXT,
    to_status   TEXT,
    note        TEXT,
    created_at  TEXT NOT NULL
);

-- SIMULATED referral / guidance records (concept note §4 "Referral coordination").
-- Nothing is sent to any real facility. is_simulated can ONLY be 1.
CREATE TABLE referrals (
    id             INTEGER PRIMARY KEY,
    referral_ref   TEXT NOT NULL UNIQUE,        -- e.g. DEMO-REF-0001
    beneficiary_id INTEGER NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,
    category       TEXT NOT NULL CHECK (category IN (
                       'Facility access guidance', 'Enrolment desk referral',
                       'Entitlement information')),
    facility_name  TEXT,                        -- always a fictional facility
    status         TEXT NOT NULL CHECK (status IN ('Guidance recorded', 'Follow-up pending', 'Completed in demo')),
    notes          TEXT,
    next_action    TEXT,
    created_by     INTEGER REFERENCES users(id),
    created_at     TEXT NOT NULL,
    is_simulated   INTEGER NOT NULL DEFAULT 1 CHECK (is_simulated = 1)
);

-- Fictional programme budget allocations and expenditure (concept note §3.3 objective 4).
-- Amounts are whole Kenya shillings. No link to any bank or payment system.
CREATE TABLE financial_records (
    id              INTEGER PRIMARY KEY,
    txn_ref         TEXT NOT NULL UNIQUE,       -- e.g. DEMO-TXN-00001
    programme_id    INTEGER NOT NULL REFERENCES programmes(id),
    entry_type      TEXT NOT NULL CHECK (entry_type IN ('Allocation', 'Expenditure')),
    category        TEXT NOT NULL,
    description     TEXT NOT NULL,
    amount_kes      INTEGER NOT NULL CHECK (amount_kes > 0),
    entry_date      TEXT NOT NULL,
    linked_activity TEXT,                       -- empty = not linked to a documented activity (§7)
    recorded_by     INTEGER REFERENCES users(id),
    created_at      TEXT NOT NULL
);

-- Prototype activity log (NOT a production security audit trail).
CREATE TABLE activity_log (
    id          INTEGER PRIMARY KEY,
    actor_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action      TEXT NOT NULL,
    entity_type TEXT,
    entity_id   INTEGER,
    summary     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

-- Indexes make look-ups by these columns fast.
CREATE INDEX idx_participations_programme ON participations(programme_id);
CREATE INDEX idx_checks_beneficiary       ON coverage_checks(beneficiary_id);
CREATE INDEX idx_cases_beneficiary        ON follow_up_cases(beneficiary_id);
CREATE INDEX idx_cases_status             ON follow_up_cases(status);
CREATE INDEX idx_activities_case          ON case_activities(case_id);
CREATE INDEX idx_referrals_beneficiary    ON referrals(beneficiary_id);
CREATE INDEX idx_finance_programme        ON financial_records(programme_id);
CREATE INDEX idx_activity_log_created     ON activity_log(created_at);
