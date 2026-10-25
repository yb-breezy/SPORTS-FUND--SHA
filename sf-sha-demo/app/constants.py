"""Fixed lists used across the demo.

Every list here is a PROPOSED DESIGN CHOICE for the demo unless marked
"from concept note". Official categories would need institutional agreement.
The allowed values must match the CHECK (...) lists in schema.sql.
"""

APP_NAME = "Sports Fund–SHA Beneficiary Management Demo"

DEMO_NOTICE = (
    "This is a demonstration prototype exploring a proposed approach to beneficiary "
    "management and health coverage coordination. It is not an official Sports Fund "
    "or SHA system. All displayed records and integration results are simulated."
)

# From concept note §5 (target beneficiary groups).
CATEGORIES = [
    "Sportspersons & athletes",
    "Coaches & technical personnel",
    "Officials & sports administrators",
    "Women & emerging athletes",
    "Other eligible & vulnerable groups",
]

# Gender is recorded because concept note §7 measures inclusion "by county, gender
# and sporting discipline". The option list itself is a proposed design choice.
GENDERS = ["Female", "Male", "Not recorded"]

DISCIPLINES = [
    "Athletics", "Football", "Rugby", "Volleyball", "Boxing",
    "Basketball", "Para-athletics", "Swimming", "Handball",
]

REGISTRATION_STATUSES = ["Pending validation", "Registered", "Inactive"]

# Illustrative outcomes only — NOT SHA's real status categories.
COVERAGE_OUTCOMES = [
    "Confirmed in demo", "Pending review", "Further action required", "Unable to confirm",
]

CASE_CATEGORIES = [
    "Enrolment support", "Coverage verification follow-up", "Record correction",
    "Consent & documentation", "Facility access guidance",
]
CASE_PRIORITIES = ["Low", "Medium", "High"]
CASE_STATUSES = ["Open", "In progress", "Awaiting information", "Resolved"]

REFERRAL_CATEGORIES = ["Facility access guidance", "Enrolment desk referral", "Entitlement information"]
REFERRAL_STATUSES = ["Guidance recorded", "Follow-up pending", "Completed in demo"]

PROGRAMME_STATUSES = ["Planned", "Active", "Completed"]

FINANCE_CATEGORIES = [
    "Athlete support", "Training camps & events", "Equipment",
    "Coaching & officiating", "Outreach & registration", "Programme administration",
]

# Kenya's 47 counties (public geographic information).
COUNTIES = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita-Taveta", "Garissa",
    "Wajir", "Mandera", "Marsabit", "Isiolo", "Meru", "Tharaka-Nithi", "Embu",
    "Kitui", "Machakos", "Makueni", "Nyandarua", "Nyeri", "Kirinyaga", "Murang'a",
    "Kiambu", "Turkana", "West Pokot", "Samburu", "Trans-Nzoia", "Uasin Gishu",
    "Elgeyo-Marakwet", "Nandi", "Baringo", "Laikipia", "Nakuru", "Narok", "Kajiado",
    "Kericho", "Bomet", "Kakamega", "Vihiga", "Bungoma", "Busia", "Siaya", "Kisumu",
    "Homa Bay", "Migori", "Kisii", "Nyamira", "Nairobi",
]
