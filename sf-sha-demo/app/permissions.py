"""Proposed demo roles and what each one is allowed to do.

PROPOSED DESIGN CHOICE: final roles and permissions would need agreement
from Sports Fund and SHA. Keeping them in one dictionary makes them easy
to review and change.

How it is used:
  * In Python routes:   @permission_required("edit_beneficiaries")
    -> the SERVER refuses the request (403) if the role lacks it.
  * In templates:       {% if can("edit_beneficiaries") %} ... {% endif %}
    -> only hides buttons. Hiding is for tidiness, NOT security.
"""

PERMISSIONS = {
    "view_dashboard":       "View the management dashboard",
    "view_beneficiaries":   "View beneficiary records and profiles",
    "edit_beneficiaries":   "Register and update beneficiary records",
    "view_coverage":        "View simulated coverage-check history",
    "run_coverage_check":   "Run a simulated coverage check",
    "view_cases":           "View follow-up and enrolment-support cases",
    "edit_cases":           "Create, assign and update cases",
    "view_referrals":       "View simulated referral and guidance records",
    "edit_referrals":       "Record simulated referrals and guidance",
    "view_programmes":      "View programmes and participation",
    "edit_programmes":      "Update programme participation",
    "view_finance":         "View fictional financial records",
    "edit_finance":         "Record fictional financial entries",
    "view_reports":         "View and export reports",
    "view_activity_log":    "View the prototype activity log",
    "manage_users":         "Manage demo users and roles",
    "reset_demo":           "Reset the database to the original sample data",
}

ROLES = {
    "admin": {
        "name": "Administrator",
        "description": "Manages demo users, roles and the demo environment.",
        "permissions": set(PERMISSIONS),  # every permission
    },
    "beneficiary_officer": {
        "name": "Beneficiary management officer",
        "description": "Registers and updates beneficiaries and opens follow-up cases.",
        "permissions": {
            "view_dashboard", "view_beneficiaries", "edit_beneficiaries",
            "view_coverage", "view_cases", "edit_cases",
            "view_referrals", "view_programmes",
        },
    },
    "programme_officer": {
        "name": "Programme officer",
        "description": "Monitors programmes, participation, follow-up and programme spending.",
        "permissions": {
            "view_dashboard", "view_beneficiaries", "view_coverage",
            "view_cases", "edit_cases", "view_referrals",
            "view_programmes", "edit_programmes",
            "view_finance", "edit_finance", "view_reports",
        },
    },
    "coverage_officer": {
        "name": "Coverage coordination officer",
        "description": "Runs simulated coverage checks and manages enrolment support and referrals.",
        "permissions": {
            "view_dashboard", "view_beneficiaries", "view_coverage", "run_coverage_check",
            "view_cases", "edit_cases", "view_referrals", "edit_referrals",
            "view_programmes", "view_reports",
        },
    },
    "management": {
        "name": "Management (view-only)",
        "description": "Reviews dashboards, reports and activity. Cannot change any record.",
        "permissions": {
            "view_dashboard", "view_beneficiaries", "view_coverage", "view_cases",
            "view_referrals", "view_programmes", "view_finance", "view_reports",
            "view_activity_log",
        },
    },
}


def role_has(role_key, permission):
    """Return True if the role is allowed to do `permission`."""
    role = ROLES.get(role_key)
    return bool(role) and permission in role["permissions"]
