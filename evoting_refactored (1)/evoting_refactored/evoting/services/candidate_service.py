"""
Candidate service — business logic for candidate CRUD and eligibility validation.
No UI output; raises ValueError or returns results to callers.
"""

import datetime

from config import MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, REQUIRED_EDUCATION_LEVELS
from models.candidate import Candidate
from services.audit_service import log_action


def calculate_age(dob_str: str) -> int:
    dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
    return (datetime.datetime.now() - dob).days // 365


class CandidateService:
    def __init__(self, store):
        self.store = store

    def validate_eligibility(self, national_id: str, dob_str: str, criminal_record: str):
        """Validate all eligibility rules. Raises ValueError on failure."""
        for c in self.store.candidates.values():
            if c.national_id == national_id:
                raise ValueError("A candidate with this National ID already exists.")

        age = calculate_age(dob_str)
        if age < MIN_CANDIDATE_AGE:
            raise ValueError(f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}")
        if age > MAX_CANDIDATE_AGE:
            raise ValueError(f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}")
        if criminal_record.lower() == "yes":
            raise ValueError("Candidates with criminal records are not eligible.")
        return age

    def create(self, data: dict, created_by: str) -> Candidate:
        """Create and store a new candidate. Returns the created Candidate."""
        age = self.validate_eligibility(data["national_id"], data["date_of_birth"], data["criminal_record"])

        candidate = Candidate(
            id=self.store.candidate_id_counter,
            full_name=data["full_name"],
            national_id=data["national_id"],
            date_of_birth=data["date_of_birth"],
            age=age,
            gender=data["gender"],
            education=data["education"],
            party=data["party"],
            manifesto=data["manifesto"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            has_criminal_record=False,
            years_experience=data.get("years_experience", 0),
            is_active=True,
            is_approved=True,
            created_at=str(datetime.datetime.now()),
            created_by=created_by,
        )
        self.store.candidates[candidate.id] = candidate
        self.store.candidate_id_counter += 1
        log_action(self.store, "CREATE_CANDIDATE", created_by, f"Created candidate: {candidate.full_name} (ID: {candidate.id})")
        self.store.save()
        return candidate

    def update(self, candidate_id: int, updates: dict, updated_by: str) -> Candidate:
        """Apply non-empty updates to a candidate. Returns updated Candidate."""
        candidate = self.store.candidates.get(candidate_id)
        if not candidate:
            raise ValueError("Candidate not found.")

        for field, value in updates.items():
            if value:
                setattr(candidate, field, value)

        log_action(self.store, "UPDATE_CANDIDATE", updated_by, f"Updated candidate: {candidate.full_name} (ID: {candidate_id})")
        self.store.save()
        return candidate

    def deactivate(self, candidate_id: int, deleted_by: str):
        """Soft-delete a candidate by deactivating them."""
        candidate = self.store.candidates.get(candidate_id)
        if not candidate:
            raise ValueError("Candidate not found.")

        for poll in self.store.polls.values():
            if poll.status == "open":
                for pos in poll.positions:
                    if candidate_id in pos.candidate_ids:
                        raise ValueError(f"Cannot delete — candidate is in active poll: {poll.title}")

        candidate.is_active = False
        log_action(self.store, "DELETE_CANDIDATE", deleted_by, f"Deactivated candidate: {candidate.full_name} (ID: {candidate_id})")
        self.store.save()

    def search(self, field: str, term) -> list:
        """Search candidates by field. Returns a list of matching Candidates."""
        results = []
        for c in self.store.candidates.values():
            if field == "name" and term.lower() in c.full_name.lower():
                results.append(c)
            elif field == "party" and term.lower() in c.party.lower():
                results.append(c)
            elif field == "education" and c.education == term:
                results.append(c)
            elif field == "age_range":
                min_age, max_age = term
                if min_age <= c.age <= max_age:
                    results.append(c)
        return results
