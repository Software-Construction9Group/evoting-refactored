"""
Poll and Position models — represent elections and the positions within them.
No business logic; only data structure and serialization.
"""


class PollPosition:
    """A position (e.g. President) within a specific poll."""

    def __init__(self, position_id, position_title, candidate_ids, max_winners):
        self.position_id = position_id
        self.position_title = position_title
        self.candidate_ids = candidate_ids if candidate_ids is not None else []
        self.max_winners = max_winners

    def to_dict(self):
        return {
            "position_id": self.position_id,
            "position_title": self.position_title,
            "candidate_ids": self.candidate_ids,
            "max_winners": self.max_winners,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            position_id=data["position_id"],
            position_title=data["position_title"],
            candidate_ids=data.get("candidate_ids", []),
            max_winners=data["max_winners"],
        )


class Poll:
    """An election poll containing one or more positions."""

    def __init__(
        self, id, title, description, election_type, start_date, end_date,
        positions, station_ids, status, total_votes_cast, created_at, created_by,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.election_type = election_type
        self.start_date = start_date
        self.end_date = end_date
        self.positions = positions  # list of PollPosition objects
        self.station_ids = station_ids if station_ids is not None else []
        self.status = status
        self.total_votes_cast = total_votes_cast
        self.created_at = created_at
        self.created_by = created_by

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "election_type": self.election_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "positions": [p.to_dict() for p in self.positions],
            "station_ids": self.station_ids,
            "status": self.status,
            "total_votes_cast": self.total_votes_cast,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data):
        positions = [PollPosition.from_dict(p) for p in data.get("positions", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            election_type=data["election_type"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            positions=positions,
            station_ids=data.get("station_ids", []),
            status=data["status"],
            total_votes_cast=data.get("total_votes_cast", 0),
            created_at=data["created_at"],
            created_by=data["created_by"],
        )


class Position:
    """A reusable electoral position definition (e.g. President, Governor)."""

    def __init__(
        self, id, title, description, level, max_winners,
        min_candidate_age, is_active, created_at, created_by,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.level = level
        self.max_winners = max_winners
        self.min_candidate_age = min_candidate_age
        self.is_active = is_active
        self.created_at = created_at
        self.created_by = created_by

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
