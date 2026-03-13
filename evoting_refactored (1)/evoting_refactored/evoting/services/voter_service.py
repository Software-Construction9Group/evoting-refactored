"""
Voter service — business logic for voter registration, verification,
deactivation, and search. No UI output.
"""

import datetime
import random
import string

from config import MIN_VOTER_AGE, MIN_PASSWORD_LENGTH
from models.voter import Voter
from services.auth_service import hash_password
from services.audit_service import log_action


def generate_voter_card_number() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


class VoterService:
    def __init__(self, store):
        self.store = store

    def register(self, data: dict) -> Voter:
        """Validate and register a new voter. Returns created Voter."""
        if not data["full_name"]:
            raise ValueError("Name cannot be empty.")
        if not data["national_id"]:
            raise ValueError("National ID cannot be empty.")

        for v in self.store.voters.values():
            if v.national_id == data["national_id"]:
                raise ValueError("A voter with this National ID already exists.")

        try:
            dob = datetime.datetime.strptime(data["date_of_birth"], "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        age = (datetime.datetime.now() - dob).days // 365
        if age < MIN_VOTER_AGE:
            raise ValueError(f"You must be at least {MIN_VOTER_AGE} years old to register.")

        if data["gender"] not in ["M", "F", "OTHER"]:
            raise ValueError("Invalid gender selection.")

        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")

        if data["password"] != data["confirm_password"]:
            raise ValueError("Passwords do not match.")

        station_id = data["station_id"]
        station = self.store.voting_stations.get(station_id)
        if not station or not station.is_active:
            raise ValueError("Invalid station selection.")

        voter_card = generate_voter_card_number()
        voter = Voter(
            id=self.store.voter_id_counter,
            full_name=data["full_name"],
            national_id=data["national_id"],
            date_of_birth=data["date_of_birth"],
            age=age,
            gender=data["gender"],
            address=data.get("address", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            password=hash_password(data["password"]),
            voter_card_number=voter_card,
            station_id=station_id,
            is_verified=False,
            is_active=True,
            has_voted_in=[],
            registered_at=str(datetime.datetime.now()),
            role="voter",
        )
        self.store.voters[voter.id] = voter
        self.store.voter_id_counter += 1
        log_action(self.store, "REGISTER", voter.full_name, f"New voter registered with card: {voter_card}")
        self.store.save()
        return voter

    def verify(self, voter_id: int, verified_by: str):
        voter = self.store.voters.get(voter_id)
        if not voter:
            raise ValueError("Voter not found.")
        if voter.is_verified:
            raise ValueError("Voter is already verified.")
        voter.is_verified = True
        log_action(self.store, "VERIFY_VOTER", verified_by, f"Verified voter: {voter.full_name}")
        self.store.save()

    def verify_all_pending(self, verified_by: str) -> int:
        count = 0
        for voter in self.store.voters.values():
            if not voter.is_verified:
                voter.is_verified = True
                count += 1
        log_action(self.store, "VERIFY_ALL_VOTERS", verified_by, f"Verified {count} voters")
        self.store.save()
        return count

    def deactivate(self, voter_id: int, deactivated_by: str):
        voter = self.store.voters.get(voter_id)
        if not voter:
            raise ValueError("Voter not found.")
        if not voter.is_active:
            raise ValueError("Voter is already deactivated.")
        voter.is_active = False
        log_action(self.store, "DEACTIVATE_VOTER", deactivated_by, f"Deactivated voter: {voter.full_name}")
        self.store.save()

    def change_password(self, voter_id: int, old_password: str, new_password: str, confirm_password: str):
        voter = self.store.voters.get(voter_id)
        if not voter:
            raise ValueError("Voter not found.")
        if hash_password(old_password) != voter.password:
            raise ValueError("Incorrect current password.")
        if len(new_password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        if new_password != confirm_password:
            raise ValueError("Passwords do not match.")
        voter.password = hash_password(new_password)
        log_action(self.store, "CHANGE_PASSWORD", voter.voter_card_number, "Password changed")
        self.store.save()

    def search(self, field: str, term) -> list:
        results = []
        for v in self.store.voters.values():
            if field == "name" and term.lower() in v.full_name.lower():
                results.append(v)
            elif field == "card" and term == v.voter_card_number:
                results.append(v)
            elif field == "national_id" and term == v.national_id:
                results.append(v)
            elif field == "station" and v.station_id == term:
                results.append(v)
        return results
