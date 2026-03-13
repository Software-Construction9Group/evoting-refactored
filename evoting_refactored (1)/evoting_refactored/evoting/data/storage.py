"""
Data storage layer — holds all application state and handles
JSON persistence. This is the single source of truth for all data.
"""

import datetime
import json
import os

from config import DATA_FILE, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_FULL_NAME, DEFAULT_ADMIN_EMAIL
from models.admin import Admin
from models.candidate import Candidate
from models.voter import Voter
from models.station import VotingStation
from models.poll import Poll, Position
from models.vote import Vote
from services.auth_service import hash_password


class Store:
    """Central data store for the entire application."""

    def __init__(self):
        self.candidates: dict[int, Candidate] = {}
        self.candidate_id_counter: int = 1

        self.voting_stations: dict[int, VotingStation] = {}
        self.station_id_counter: int = 1

        self.polls: dict[int, Poll] = {}
        self.poll_id_counter: int = 1

        self.positions: dict[int, Position] = {}
        self.position_id_counter: int = 1

        self.voters: dict[int, Voter] = {}
        self.voter_id_counter: int = 1

        self.admins: dict[int, Admin] = {}
        self.admin_id_counter: int = 1

        self.votes: list[Vote] = []
        self.audit_log: list[dict] = []

        self._seed_default_admin()

    def _seed_default_admin(self):
        """Create the default super admin account on first run."""
        self.admins[1] = Admin(
            id=1,
            username=DEFAULT_ADMIN_USERNAME,
            password=hash_password(DEFAULT_ADMIN_PASSWORD),
            full_name=DEFAULT_ADMIN_FULL_NAME,
            email=DEFAULT_ADMIN_EMAIL,
            role="super_admin",
            created_at=str(datetime.datetime.now()),
            is_active=True,
        )
        self.admin_id_counter = 2

    def save(self):
        """Serialize all state to JSON and write to disk."""
        data = {
            "candidates": {k: v.to_dict() for k, v in self.candidates.items()},
            "candidate_id_counter": self.candidate_id_counter,
            "voting_stations": {k: v.to_dict() for k, v in self.voting_stations.items()},
            "station_id_counter": self.station_id_counter,
            "polls": {k: v.to_dict() for k, v in self.polls.items()},
            "poll_id_counter": self.poll_id_counter,
            "positions": {k: v.to_dict() for k, v in self.positions.items()},
            "position_id_counter": self.position_id_counter,
            "voters": {k: v.to_dict() for k, v in self.voters.items()},
            "voter_id_counter": self.voter_id_counter,
            "admins": {k: v.to_dict() for k, v in self.admins.items()},
            "admin_id_counter": self.admin_id_counter,
            "votes": [v.to_dict() for v in self.votes],
            "audit_log": self.audit_log,
        }
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"  Error saving data: {e}")

    def load(self):
        """Load and deserialize state from JSON file if it exists."""
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)

            self.candidates = {
                int(k): Candidate.from_dict(v)
                for k, v in data.get("candidates", {}).items()
            }
            self.candidate_id_counter = data.get("candidate_id_counter", 1)

            self.voting_stations = {
                int(k): VotingStation.from_dict(v)
                for k, v in data.get("voting_stations", {}).items()
            }
            self.station_id_counter = data.get("station_id_counter", 1)

            self.polls = {
                int(k): Poll.from_dict(v)
                for k, v in data.get("polls", {}).items()
            }
            self.poll_id_counter = data.get("poll_id_counter", 1)

            self.positions = {
                int(k): Position.from_dict(v)
                for k, v in data.get("positions", {}).items()
            }
            self.position_id_counter = data.get("position_id_counter", 1)

            self.voters = {
                int(k): Voter.from_dict(v)
                for k, v in data.get("voters", {}).items()
            }
            self.voter_id_counter = data.get("voter_id_counter", 1)

            self.admins = {
                int(k): Admin.from_dict(v)
                for k, v in data.get("admins", {}).items()
            }
            self.admin_id_counter = data.get("admin_id_counter", 1)

            self.votes = [Vote.from_dict(v) for v in data.get("votes", [])]
            self.audit_log = data.get("audit_log", [])

        except Exception as e:
            print(f"  Error loading data: {e}")


# Singleton store instance used across the application
store = Store()
