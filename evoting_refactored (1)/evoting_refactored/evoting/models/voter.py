"""
Voter model — represents a registered voter's data and identity.
No business logic; only data structure and serialization.
"""


class Voter:
    def __init__(
        self, id, full_name, national_id, date_of_birth, age, gender,
        address, phone, email, password, voter_card_number, station_id,
        is_verified, is_active, has_voted_in, registered_at, role="voter",
    ):
        self.id = id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password
        self.voter_card_number = voter_card_number
        self.station_id = station_id
        self.is_verified = is_verified
        self.is_active = is_active
        self.has_voted_in = has_voted_in if has_voted_in is not None else []
        self.registered_at = registered_at
        self.role = role

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
