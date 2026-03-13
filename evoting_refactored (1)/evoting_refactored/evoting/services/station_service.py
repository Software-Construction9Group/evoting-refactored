"""
Station service — business logic for voting station CRUD.
No UI output.
"""

import datetime

from models.station import VotingStation
from services.audit_service import log_action


class StationService:
    def __init__(self, store):
        self.store = store

    def create(self, data: dict, created_by: str) -> VotingStation:
        if not data["name"]:
            raise ValueError("Station name cannot be empty.")
        if not data["location"]:
            raise ValueError("Location cannot be empty.")
        if data["capacity"] <= 0:
            raise ValueError("Capacity must be positive.")

        station = VotingStation(
            id=self.store.station_id_counter,
            name=data["name"],
            location=data["location"],
            region=data["region"],
            capacity=data["capacity"],
            registered_voters=0,
            supervisor=data.get("supervisor", ""),
            contact=data.get("contact", ""),
            opening_time=data.get("opening_time", ""),
            closing_time=data.get("closing_time", ""),
            is_active=True,
            created_at=str(datetime.datetime.now()),
            created_by=created_by,
        )
        self.store.voting_stations[station.id] = station
        self.store.station_id_counter += 1
        log_action(self.store, "CREATE_STATION", created_by, f"Created station: {station.name} (ID: {station.id})")
        self.store.save()
        return station

    def update(self, station_id: int, updates: dict, updated_by: str) -> VotingStation:
        station = self.store.voting_stations.get(station_id)
        if not station:
            raise ValueError("Station not found.")
        for field, value in updates.items():
            if value:
                setattr(station, field, value)
        log_action(self.store, "UPDATE_STATION", updated_by, f"Updated station: {station.name} (ID: {station_id})")
        self.store.save()
        return station

    def deactivate(self, station_id: int, deactivated_by: str):
        station = self.store.voting_stations.get(station_id)
        if not station:
            raise ValueError("Station not found.")
        station.is_active = False
        log_action(self.store, "DELETE_STATION", deactivated_by, f"Deactivated station: {station.name}")
        self.store.save()

    def voter_count(self, station_id: int) -> int:
        return sum(1 for v in self.store.voters.values() if v.station_id == station_id)
