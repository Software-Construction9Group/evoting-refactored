"""
main.py — Application entry point.

Wires together the data store, services, and views,
then starts the main application loop.
"""

import time

from ui.colors import THEME_LOGIN, RESET
from ui.prompts import clear_screen
from data.storage import store
from services.auth_service import session
from services.candidate_service import CandidateService
from services.voter_service import VoterService
from services.station_service import StationService
from services.poll_service import PollService, PositionService
from services.vote_service import VoteService
from services.admin_service import AdminService
from services.results_service import ResultsService
from views.auth_view import AuthView
from views.admin_view import AdminView
from views.voter_view import VoterView


def build_services(store):
    """Instantiate all services, injecting the shared store."""
    return {
        "candidate": CandidateService(store),
        "voter": VoterService(store),
        "station": StationService(store),
        "position": PositionService(store),
        "poll": PollService(store),
        "vote": VoteService(store),
        "admin": AdminService(store),
        "results": ResultsService(store),
    }


def main():
    print(f"\n  {THEME_LOGIN}Loading E-Voting System...{RESET}")
    store.load()
    time.sleep(1)

    services = build_services(store)
    auth_view = AuthView(store, session, services["voter"])
    admin_view = AdminView(store, session, services)
    voter_view = VoterView(store, session, services)

    while True:
        clear_screen()
        logged_in = auth_view.show_login_menu()

        if logged_in:
            if session.current_role == "admin":
                admin_view.run()
            elif session.current_role == "voter":
                voter_view.run()
            session.logout()


if __name__ == "__main__":
    main()
