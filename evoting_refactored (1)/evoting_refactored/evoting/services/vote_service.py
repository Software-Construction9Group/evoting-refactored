"""
Vote service — handles ballot casting with duplicate prevention.
No UI output.
"""

import datetime
import hashlib

from models.vote import Vote
from services.audit_service import log_action


class VoteService:
    def __init__(self, store):
        self.store = store

    def get_available_polls(self, voter) -> dict:
        """Return polls the voter can still vote in."""
        available = {}
        for pid, poll in self.store.polls.items():
            if (
                poll.status == "open"
                and pid not in voter.has_voted_in
                and voter.station_id in poll.station_ids
            ):
                available[pid] = poll
        return available

    def cast_ballot(self, voter, poll_id: int, selections: list):
        """
        Record a voter's ballot selections.

        selections: list of dicts with keys:
            position_id, position_title, candidate_id (or None), abstained
        """
        poll = self.store.polls.get(poll_id)
        if not poll or poll.status != "open":
            raise ValueError("This poll is not open for voting.")
        if poll_id in voter.has_voted_in:
            raise ValueError("You have already voted in this poll.")

        timestamp = str(datetime.datetime.now())
        vote_hash = hashlib.sha256(
            f"{voter.id}{poll_id}{timestamp}".encode()
        ).hexdigest()[:16]

        for sel in selections:
            self.store.votes.append(Vote(
                vote_id=vote_hash + str(sel["position_id"]),
                poll_id=poll_id,
                position_id=sel["position_id"],
                candidate_id=sel.get("candidate_id"),
                voter_id=voter.id,
                station_id=voter.station_id,
                timestamp=timestamp,
                abstained=sel.get("abstained", False),
            ))

        voter.has_voted_in.append(poll_id)
        # Sync the change back to the store
        self.store.voters[voter.id].has_voted_in.append(poll_id)
        poll.total_votes_cast += 1

        log_action(
            self.store,
            "CAST_VOTE",
            voter.voter_card_number,
            f"Voted in poll: {poll.title} (Hash: {vote_hash})",
        )
        self.store.save()
        return vote_hash

    def get_voter_votes(self, voter_id: int, poll_id: int) -> list:
        return [v for v in self.store.votes if v.voter_id == voter_id and v.poll_id == poll_id]
