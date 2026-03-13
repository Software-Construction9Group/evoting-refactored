"""
Voter view — all voter-facing menus and screens.
Handles only user input and output. Delegates all logic to services.
"""

from ui.colors import (
    RESET, BOLD, DIM, ITALIC, GRAY,
    GREEN, RED, YELLOW, BLACK,
    BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_CYAN, BRIGHT_BLUE,
    BG_GREEN, THEME_VOTER, THEME_VOTER_ACCENT,
)
from ui.components import (
    header, subheader, menu_item, error, success, warning, info, status_badge,
)
from ui.prompts import clear_screen, pause, prompt, masked_input


class VoterView:
    def __init__(self, store, session, services):
        self.store = store
        self.session = session
        self.vote_svc = services["vote"]
        self.voter_svc = services["voter"]
        self.results_svc = services["results"]

    def run(self):
        while True:
            clear_screen()
            header("VOTER DASHBOARD", THEME_VOTER)
            voter = self.session.current_user
            station_name = self.store.voting_stations.get(voter.station_id, None)
            station_label = station_name.name if station_name else "Unknown"
            print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{voter.full_name}{RESET}")
            print(f"  {DIM}    Card: {voter.voter_card_number}  │  Station: {station_label}{RESET}")
            print()
            menu_item(1, "View Open Polls", THEME_VOTER)
            menu_item(2, "Cast Vote", THEME_VOTER)
            menu_item(3, "View My Voting History", THEME_VOTER)
            menu_item(4, "View Results (Closed Polls)", THEME_VOTER)
            menu_item(5, "View My Profile", THEME_VOTER)
            menu_item(6, "Change Password", THEME_VOTER)
            menu_item(7, "Logout", THEME_VOTER)
            print()
            choice = prompt("Enter choice: ")

            if choice == "1":
                self.view_open_polls()
            elif choice == "2":
                self.cast_vote()
            elif choice == "3":
                self.view_voting_history()
            elif choice == "4":
                self.view_closed_results()
            elif choice == "5":
                self.view_profile()
            elif choice == "6":
                self.change_password()
            elif choice == "7":
                from services.audit_service import log_action
                log_action(self.store, "LOGOUT", voter.voter_card_number, "Voter logged out")
                self.store.save()
                break
            else:
                error("Invalid choice.")
                pause()

    def view_open_polls(self):
        clear_screen()
        header("OPEN POLLS", THEME_VOTER)
        voter = self.session.current_user
        open_polls = {pid: p for pid, p in self.store.polls.items() if p.status == "open"}
        if not open_polls:
            print()
            info("No open polls at this time.")
            pause()
            return
        for pid, poll in open_polls.items():
            already_voted = pid in voter.has_voted_in
            vs = f" {GREEN}[VOTED]{RESET}" if already_voted else f" {YELLOW}[NOT YET VOTED]{RESET}"
            print(f"\n  {BOLD}{THEME_VOTER}Poll #{poll.id}: {poll.title}{RESET}{vs}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  {DIM}│  Period:{RESET} {poll.start_date} to {poll.end_date}")
            for pos in poll.positions:
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {BOLD}{pos.position_title}{RESET}")
                for cid in pos.candidate_ids:
                    if cid in self.store.candidates:
                        c = self.store.candidates[cid]
                        print(f"      {DIM}•{RESET} {c.full_name} {DIM}({c.party}) │ Age: {c.age} │ Edu: {c.education}{RESET}")
        pause()

    def cast_vote(self):
        clear_screen()
        header("CAST YOUR VOTE", THEME_VOTER)
        voter = self.session.current_user
        available_polls = self.vote_svc.get_available_polls(voter)
        if not available_polls:
            print()
            info("No available polls to vote in.")
            pause()
            return

        subheader("Available Polls", THEME_VOTER_ACCENT)
        for poll in available_polls.values():
            print(f"  {THEME_VOTER}{poll.id}.{RESET} {poll.title} {DIM}({poll.election_type}){RESET}")

        try:
            pid = int(prompt("\nSelect Poll ID to vote: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in available_polls:
            error("Invalid poll selection.")
            pause()
            return

        poll = self.store.polls[pid]
        print()
        header(f"Voting: {poll.title}", THEME_VOTER)
        info("Please select ONE candidate for each position.\n")

        selections = []
        for pos in poll.positions:
            subheader(pos.position_title, THEME_VOTER_ACCENT)
            if not pos.candidate_ids:
                info("No candidates for this position.")
                continue

            for idx, cid in enumerate(pos.candidate_ids, 1):
                if cid in self.store.candidates:
                    c = self.store.candidates[cid]
                    print(f"    {THEME_VOTER}{BOLD}{idx}.{RESET} {c.full_name} {DIM}({c.party}){RESET}")
                    print(f"       {DIM}Age: {c.age} │ Edu: {c.education} │ Exp: {c.years_experience} yrs{RESET}")
                    if c.manifesto:
                        print(f"       {ITALIC}{DIM}{c.manifesto[:80]}...{RESET}")
            print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain / Skip{RESET}")

            try:
                vote_choice = int(prompt(f"\nYour choice for {pos.position_title}: "))
            except ValueError:
                warning("Invalid input. Skipping.")
                vote_choice = 0

            if vote_choice == 0 or not (1 <= vote_choice <= len(pos.candidate_ids)):
                if vote_choice != 0:
                    warning("Invalid choice. Marking as abstain.")
                selections.append({
                    "position_id": pos.position_id,
                    "position_title": pos.position_title,
                    "candidate_id": None,
                    "abstained": True,
                })
            else:
                selected_cid = pos.candidate_ids[vote_choice - 1]
                selections.append({
                    "position_id": pos.position_id,
                    "position_title": pos.position_title,
                    "candidate_id": selected_cid,
                    "candidate_name": self.store.candidates[selected_cid].full_name,
                    "abstained": False,
                })

        subheader("VOTE SUMMARY", BRIGHT_CYAN)
        for sel in selections:
            if sel["abstained"]:
                print(f"  {sel['position_title']}: {GRAY}ABSTAINED{RESET}")
            else:
                print(f"  {sel['position_title']}: {BRIGHT_GREEN}{BOLD}{sel['candidate_name']}{RESET}")
        print()

        if prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
            info("Vote cancelled.")
            pause()
            return

        try:
            vote_hash = self.vote_svc.cast_ballot(voter, pid, selections)
            print()
            success("Your vote has been recorded successfully!")
            print(f"  {DIM}Vote Reference:{RESET} {BRIGHT_YELLOW}{vote_hash}{RESET}")
            print(f"  {BRIGHT_CYAN}Thank you for participating in the democratic process!{RESET}")
        except ValueError as e:
            error(str(e))
        pause()

    def view_voting_history(self):
        clear_screen()
        header("MY VOTING HISTORY", THEME_VOTER)
        voter = self.session.current_user
        voted_polls = voter.has_voted_in
        if not voted_polls:
            print()
            info("You have not voted in any polls yet.")
            pause()
            return
        print(f"\n  {DIM}You have voted in {len(voted_polls)} poll(s):{RESET}\n")
        for pid in voted_polls:
            if pid not in self.store.polls:
                continue
            poll = self.store.polls[pid]
            sc = GREEN if poll.status == "open" else RED
            print(f"  {BOLD}{THEME_VOTER}Poll #{pid}: {poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  {DIM}│  Status:{RESET} {sc}{poll.status.upper()}{RESET}")
            my_votes = self.vote_svc.get_voter_votes(voter.id, pid)
            for vr in my_votes:
                pos_title = next(
                    (pos.position_title for pos in poll.positions if pos.position_id == vr.position_id),
                    "Unknown",
                )
                if vr.abstained:
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {GRAY}ABSTAINED{RESET}")
                else:
                    cand = self.store.candidates.get(vr.candidate_id)
                    name = cand.full_name if cand else "Unknown"
                    print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos_title}: {BRIGHT_GREEN}{name}{RESET}")
            print()
        pause()

    def view_closed_results(self):
        clear_screen()
        header("ELECTION RESULTS", THEME_VOTER)
        closed_polls = {pid: p for pid, p in self.store.polls.items() if p.status == "closed"}
        if not closed_polls:
            print()
            info("No closed polls with results.")
            pause()
            return
        for pid, poll in closed_polls.items():
            print(f"\n  {BOLD}{THEME_VOTER}{poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  {DIM}│  Votes:{RESET} {poll.total_votes_cast}")
            for pos in poll.positions:
                subheader(pos.position_title, THEME_VOTER_ACCENT)
                tally = self.results_svc.tally_position(pid, pos.position_id)
                vote_counts = tally["counts"]
                abstain_count = tally["abstain"]
                total = tally["total"]
                for rank, (cid, count) in enumerate(
                    sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1
                ):
                    cand = self.store.candidates.get(cid)
                    name = cand.full_name if cand else "?"
                    party = cand.party if cand else "?"
                    pct = (count / total * 100) if total > 0 else 0
                    bar = f"{THEME_VOTER}{'█' * int(pct / 2)}{GRAY}{'░' * (50 - int(pct / 2))}{RESET}"
                    winner = f" {BG_GREEN}{BLACK}{BOLD} WINNER {RESET}" if rank <= pos.max_winners else ""
                    print(f"    {BOLD}{rank}. {name}{RESET} {DIM}({party}){RESET}")
                    print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
                if abstain_count > 0:
                    pct = (abstain_count / total * 100) if total > 0 else 0
                    print(f"    {GRAY}Abstained: {abstain_count} ({pct:.1f}%){RESET}")
        pause()

    def view_profile(self):
        clear_screen()
        header("MY PROFILE", THEME_VOTER)
        v = self.session.current_user
        station = self.store.voting_stations.get(v.station_id)
        station_label = station.name if station else "Unknown"
        print()
        fields = [
            ("Name", v.full_name),
            ("National ID", v.national_id),
            ("Voter Card", f"{BRIGHT_YELLOW}{v.voter_card_number}{RESET}"),
            ("Date of Birth", v.date_of_birth),
            ("Age", v.age),
            ("Gender", v.gender),
            ("Address", v.address),
            ("Phone", v.phone),
            ("Email", v.email),
            ("Station", station_label),
            ("Verified", status_badge("Yes", True) if v.is_verified else status_badge("No", False)),
            ("Registered", v.registered_at),
            ("Polls Voted", len(v.has_voted_in)),
        ]
        for label, value in fields:
            print(f"  {THEME_VOTER}{label + ':':<16}{RESET} {value}")
        pause()

    def change_password(self):
        clear_screen()
        header("CHANGE PASSWORD", THEME_VOTER)
        voter = self.session.current_user
        print()
        old_pass = masked_input("Current Password: ").strip()
        new_pass = masked_input("New Password: ").strip()
        confirm_pass = masked_input("Confirm New Password: ").strip()
        try:
            self.voter_svc.change_password(voter.id, old_pass, new_pass, confirm_pass)
            # Keep session in sync
            self.session.current_user.password = self.store.voters[voter.id].password
            print()
            success("Password changed successfully!")
        except ValueError as e:
            error(str(e))
        pause()
