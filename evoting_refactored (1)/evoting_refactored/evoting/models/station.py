"""
VotingStation model — represents a physical voting station.
No business logic; only data structure and serialization.
"""


class VotingStation:
    def __init__(
        self, id, name, location, region, capacity, registered_voters,
        supervisor, contact, opening_time, closing_time,
        is_active, created_at, created_by,
    ):
        self.id = id
        self.name = name
        self.location = location
        self.region = region
        self.capacity = capacity
        self.registered_voters = registered_voters
        self.supervisor = supervisor
        self.contact = contact
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.is_active = is_active
        self.created_at = created_at
        self.created_by = created_by

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
