"""
Vote model — represents a single ballot entry for one position.
No business logic; only data structure and serialization.
"""


class Vote:
    def __init__(
        self, vote_id, poll_id, position_id, candidate_id,
        voter_id, station_id, timestamp, abstained,
    ):
        self.vote_id = vote_id
        self.poll_id = poll_id
        self.position_id = position_id
        self.candidate_id = candidate_id
        self.voter_id = voter_id
        self.station_id = station_id
        self.timestamp = timestamp
        self.abstained = abstained

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
