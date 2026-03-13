"""
Results service — computes vote tallies, turnout statistics,
station-wise breakdowns, and demographic summaries. No UI output.
"""


class ResultsService:
    def __init__(self, store):
        self.store = store

    def tally_position(self, poll_id: int, position_id: int) -> dict:
        """
        Count votes for a single position in a poll.
        Returns { candidate_id: count, '_abstain': count, '_total': count }.
        """
        tally = {}
        abstain_count = 0
        total = 0

        for vote in self.store.votes:
            if vote.poll_id == poll_id and vote.position_id == position_id:
                total += 1
                if vote.abstained:
                    abstain_count += 1
                else:
                    tally[vote.candidate_id] = tally.get(vote.candidate_id, 0) + 1

        return {"counts": tally, "abstain": abstain_count, "total": total}

    def poll_turnout(self, poll_id: int) -> dict:
        """Return turnout info: eligible voter count, votes cast, percentage."""
        poll = self.store.polls.get(poll_id)
        if not poll:
            return {"eligible": 0, "voted": 0, "percentage": 0.0}

        eligible = sum(
            1 for v in self.store.voters.values()
            if v.is_verified and v.is_active and v.station_id in poll.station_ids
        )
        voted = poll.total_votes_cast
        percentage = (voted / eligible * 100) if eligible > 0 else 0.0
        return {"eligible": eligible, "voted": voted, "percentage": percentage}

    def station_turnout(self, poll_id: int, station_id: int) -> dict:
        """Return turnout for a specific station within a poll."""
        station_votes = [
            v for v in self.store.votes
            if v.poll_id == poll_id and v.station_id == station_id
        ]
        voters_who_voted = len(set(v.voter_id for v in station_votes))
        registered_at_station = sum(
            1 for v in self.store.voters.values()
            if v.station_id == station_id and v.is_verified and v.is_active
        )
        percentage = (voters_who_voted / registered_at_station * 100) if registered_at_station > 0 else 0.0
        return {
            "registered": registered_at_station,
            "voted": voters_who_voted,
            "percentage": percentage,
            "votes": station_votes,
        }

    def system_overview(self) -> dict:
        """Return high-level counts for the statistics dashboard."""
        s = self.store
        return {
            "total_candidates": len(s.candidates),
            "active_candidates": sum(1 for c in s.candidates.values() if c.is_active),
            "total_voters": len(s.voters),
            "verified_voters": sum(1 for v in s.voters.values() if v.is_verified),
            "active_voters": sum(1 for v in s.voters.values() if v.is_active),
            "total_stations": len(s.voting_stations),
            "active_stations": sum(1 for st in s.voting_stations.values() if st.is_active),
            "total_polls": len(s.polls),
            "open_polls": sum(1 for p in s.polls.values() if p.status == "open"),
            "closed_polls": sum(1 for p in s.polls.values() if p.status == "closed"),
            "draft_polls": sum(1 for p in s.polls.values() if p.status == "draft"),
            "total_votes": len(s.votes),
        }

    def voter_demographics(self) -> dict:
        """Return gender counts and age group distribution."""
        gender_counts = {}
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}

        for v in self.store.voters.values():
            g = v.gender or "?"
            gender_counts[g] = gender_counts.get(g, 0) + 1
            age = v.age or 0
            if age <= 25:       age_groups["18-25"] += 1
            elif age <= 35:     age_groups["26-35"] += 1
            elif age <= 45:     age_groups["36-45"] += 1
            elif age <= 55:     age_groups["46-55"] += 1
            elif age <= 65:     age_groups["56-65"] += 1
            else:               age_groups["65+"] += 1

        return {"gender": gender_counts, "age_groups": age_groups}

    def station_load(self) -> list:
        """Return load info for every station."""
        result = []
        for sid, station in self.store.voting_stations.items():
            vc = sum(1 for v in self.store.voters.values() if v.station_id == sid)
            load_pct = (vc / station.capacity * 100) if station.capacity > 0 else 0
            result.append({
                "station": station,
                "voter_count": vc,
                "load_pct": load_pct,
                "overloaded": load_pct > 100,
            })
        return result

    def party_distribution(self) -> dict:
        counts = {}
        for c in self.store.candidates.values():
            if c.is_active:
                counts[c.party] = counts.get(c.party, 0) + 1
        return counts

    def education_distribution(self) -> dict:
        counts = {}
        for c in self.store.candidates.values():
            if c.is_active:
                counts[c.education] = counts.get(c.education, 0) + 1
        return counts
