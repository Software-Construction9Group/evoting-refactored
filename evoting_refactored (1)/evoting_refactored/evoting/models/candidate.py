"""
Candidate model — represents a candidate's data and identity.
No business logic; only data structure and serialization.
"""

import datetime


class Candidate:
    def __init__(
        self, id, full_name, national_id, date_of_birth, age, gender,
        education, party, manifesto, address, phone, email,
        has_criminal_record, years_experience, is_active, is_approved,
        created_at, created_by,
    ):
        self.id = id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.education = education
        self.party = party
        self.manifesto = manifesto
        self.address = address
        self.phone = phone
        self.email = email
        self.has_criminal_record = has_criminal_record
        self.years_experience = years_experience
        self.is_active = is_active
        self.is_approved = is_approved
        self.created_at = created_at
        self.created_by = created_by

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
