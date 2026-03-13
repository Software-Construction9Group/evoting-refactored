"""
Poll and Position service — business logic for creating, updating,
opening/closing polls and managing positions. No UI output.
"""

import datetime

from config import MIN_CANDIDATE_AGE
from models.poll import Poll, PollPosition, Position
from services.audit_service import log_action


class PositionService:
    def __init__(self, store):
        self.store = store

    def create(self, data: dict, created_by: str) -> Position:
        if not data["title"]:
            raise ValueError("Title cannot be empty.")
        if data["level"].lower() not in ["national", "regional", "local"]:
            raise ValueError("Invalid level. Choose: National, Regional, or Local.")
        if data["max_winners"] <= 0:
            raise ValueError("Must have at least 1 winner seat.")

        position = Position(
            id=self.store.position_id_counter,
            title=data["title"],
            description=data.get("description", ""),
            level=data["level"].capitalize(),
            max_winners=data["max_winners"],
            min_candidate_age=data.get("min_candidate_age", MIN_CANDIDATE_AGE),
            is_active=True,
            created_at=str(datetime.datetime.now()),
            created_by=created_by,
        )
        self.store.positions[position.id] = position
        self.store.position_id_counter += 1
        log_action(self.store, "CREATE_POSITION", created_by, f"Created position: {position.title} (ID: {position.id})")
        self.store.save()
        return position

    def update(self, position_id: int, updates: dict, updated_by: str) -> Position:
        position = self.store.positions.get(position_id)
        if not position:
            raise ValueError("Position not found.")
        for field, value in updates.items():
            if value:
                setattr(position, field, value)
        log_action(self.store, "UPDATE_POSITION", updated_by, f"Updated position: {position.title}")
        self.store.save()
        return position

    def deactivate(self, position_id: int, deactivated_by: str):
        position = self.store.positions.get(position_id)
        if not position:
            raise ValueError("Position not found.")
        for poll in self.store.polls.values():
            for pp in poll.positions:
                if pp.position_id == position_id and poll.status == "open":
                    raise ValueError(f"Cannot delete — in active poll: {poll.title}")
        position.is_active = False
        log_action(self.store, "DELETE_POSITION", deactivated_by, f"Deactivated position: {position.title}")
        self.store.save()


class PollService:
    def __init__(self, store):
        self.store = store

    def create(self, data: dict, created_by: str) -> Poll:
        if not data["title"]:
            raise ValueError("Title cannot be empty.")
        try:
            sd = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d")
            ed = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")
        if ed <= sd:
            raise ValueError("End date must be after start date.")

        poll_positions = []
        for pid in data["position_ids"]:
            pos = self.store.positions.get(pid)
            if not pos or not pos.is_active:
                continue
            poll_positions.append(PollPosition(
                position_id=pid,
                position_title=pos.title,
                candidate_ids=[],
                max_winners=pos.max_winners,
            ))
        if not poll_positions:
            raise ValueError("No valid positions selected.")

        poll = Poll(
            id=self.store.poll_id_counter,
            title=data["title"],
            description=data.get("description", ""),
            election_type=data["election_type"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            positions=poll_positions,
            station_ids=data["station_ids"],
            status="draft",
            total_votes_cast=0,
            created_at=str(datetime.datetime.now()),
            created_by=created_by,
        )
        self.store.polls[poll.id] = poll
        self.store.poll_id_counter += 1
        log_action(self.store, "CREATE_POLL", created_by, f"Created poll: {poll.title} (ID: {poll.id})")
        self.store.save()
        return poll

    def update(self, poll_id: int, updates: dict, updated_by: str) -> Poll:
        poll = self.store.polls.get(poll_id)
        if not poll:
            raise ValueError("Poll not found.")
        if poll.status == "open":
            raise ValueError("Cannot update an open poll. Close it first.")
        if poll.status == "closed" and poll.total_votes_cast > 0:
            raise ValueError("Cannot update a poll with recorded votes.")
        for field, value in updates.items():
            if value:
                setattr(poll, field, value)
        log_action(self.store, "UPDATE_POLL", updated_by, f"Updated poll: {poll.title}")
        self.store.save()
        return poll

    def delete(self, poll_id: int, deleted_by: str):
        poll = self.store.polls.get(poll_id)
        if not poll:
            raise ValueError("Poll not found.")
        if poll.status == "open":
            raise ValueError("Cannot delete an open poll. Close it first.")
        title = poll.title
        del self.store.polls[poll_id]
        self.store.votes = [v for v in self.store.votes if v.poll_id != poll_id]
        log_action(self.store, "DELETE_POLL", deleted_by, f"Deleted poll: {title}")
        self.store.save()

    def open(self, poll_id: int, opened_by: str) -> Poll:
        poll = self.store.polls.get(poll_id)
        if not poll:
            raise ValueError("Poll not found.")
        if not any(pos.candidate_ids for pos in poll.positions):
            raise ValueError("Cannot open — no candidates assigned.")
        poll.status = "open"
        log_action(self.store, "OPEN_POLL", opened_by, f"Opened poll: {poll.title}")
        self.store.save()
        return poll

    def close(self, poll_id: int, closed_by: str) -> Poll:
        poll = self.store.polls.get(poll_id)
        if not poll:
            raise ValueError("Poll not found.")
        poll.status = "closed"
        log_action(self.store, "CLOSE_POLL", closed_by, f"Closed poll: {poll.title}")
        self.store.save()
        return poll

    def reopen(self, poll_id: int, reopened_by: str) -> Poll:
        poll = self.store.polls.get(poll_id)
        if not poll:
            raise ValueError("Poll not found.")
        poll.status = "open"
        log_action(self.store, "REOPEN_POLL", reopened_by, f"Reopened poll: {poll.title}")
        self.store.save()
        return poll

    def assign_candidates(self, poll_id: int, position_index: int, candidate_ids: list, assigned_by: str):
        poll = self.store.polls.get(poll_id)
        if not poll:
            raise ValueError("Poll not found.")
        if poll.status == "open":
            raise ValueError("Cannot modify candidates of an open poll.")
        poll.positions[position_index].candidate_ids = candidate_ids
        log_action(self.store, "ASSIGN_CANDIDATES", assigned_by, f"Updated candidates for poll: {poll.title}")
        self.store.save()
