"""
Application-wide constants and configuration.
"""

MIN_CANDIDATE_AGE = 25
MAX_CANDIDATE_AGE = 75
MIN_VOTER_AGE = 18
MIN_PASSWORD_LENGTH = 6

REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Doctorate",
]

ADMIN_ROLES = {
    "1": "super_admin",
    "2": "election_officer",
    "3": "station_manager",
    "4": "auditor",
}

ADMIN_ROLE_LABELS = {
    "super_admin": "Full access",
    "election_officer": "Manage polls and candidates",
    "station_manager": "Manage stations and verify voters",
    "auditor": "Read-only access",
}

ELECTION_TYPES = ["General", "Primary", "By-election", "Referendum"]
POSITION_LEVELS = ["national", "regional", "local"]
DATA_FILE = "evoting_data.json"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_FULL_NAME = "System Administrator"
DEFAULT_ADMIN_EMAIL = "admin@evote.com"
