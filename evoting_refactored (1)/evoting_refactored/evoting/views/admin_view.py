"""
Admin view — all admin-facing menus and screens.
Handles only user input and output. Delegates all logic to services.
"""

from config import REQUIRED_EDUCATION_LEVELS, ADMIN_ROLES, ADMIN_ROLE_LABELS, POSITION_LEVELS
from ui.colors import (
    RESET, BOLD, DIM, ITALIC, GRAY,
    GREEN, RED, YELLOW, BLACK,
    BRIGHT_YELLOW, BRIGHT_GREEN, BRIGHT_WHITE,
    BG_GREEN, THEME_ADMIN, THEME_ADMIN_ACCENT,
)
from ui.components import (
    header, subheader, table_header, table_divider,
    menu_item, error, success, warning, info, status_badge,
)
from ui.prompts import clear_screen, pause, prompt, masked_input


class AdminView:
    def __init__(self, store, session, services):
        self.store = store
        self.session = session
        self.candidate_svc = services["candidate"]
        self.station_svc = services["station"]
        self.position_svc = services["position"]
        self.poll_svc = services["poll"]
        self.voter_svc = services["voter"]
        self.admin_svc = services["admin"]
        self.results_svc = services["results"]

    # ──────────────────────────────────────────────
    # Dashboard
    # ──────────────────────────────────────────────
    def run(self):
        while True:
            clear_screen()
            header("ADMIN DASHBOARD", THEME_ADMIN)
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{self.session.current_user.full_name}{RESET}"
                  f"  {DIM}│  Role: {self.session.current_user.role}{RESET}")

            subheader("Candidate Management", THEME_ADMIN_ACCENT)
            menu_item(1, "Create Candidate", THEME_ADMIN)
            menu_item(2, "View All Candidates", THEME_ADMIN)
            menu_item(3, "Update Candidate", THEME_ADMIN)
            menu_item(4, "Delete Candidate", THEME_ADMIN)
            menu_item(5, "Search Candidates", THEME_ADMIN)

            subheader("Voting Station Management", THEME_ADMIN_ACCENT)
            menu_item(6, "Create Voting Station", THEME_ADMIN)
            menu_item(7, "View All Stations", THEME_ADMIN)
            menu_item(8, "Update Station", THEME_ADMIN)
            menu_item(9, "Delete Station", THEME_ADMIN)

            subheader("Polls & Positions", THEME_ADMIN_ACCENT)
            menu_item(10, "Create Position", THEME_ADMIN)
            menu_item(11, "View Positions", THEME_ADMIN)
            menu_item(12, "Update Position", THEME_ADMIN)
            menu_item(13, "Delete Position", THEME_ADMIN)
            menu_item(14, "Create Poll", THEME_ADMIN)
            menu_item(15, "View All Polls", THEME_ADMIN)
            menu_item(16, "Update Poll", THEME_ADMIN)
            menu_item(17, "Delete Poll", THEME_ADMIN)
            menu_item(18, "Open/Close Poll", THEME_ADMIN)
            menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)

            subheader("Voter Management", THEME_ADMIN_ACCENT)
            menu_item(20, "View All Voters", THEME_ADMIN)
            menu_item(21, "Verify Voter", THEME_ADMIN)
            menu_item(22, "Deactivate Voter", THEME_ADMIN)
            menu_item(23, "Search Voters", THEME_ADMIN)

            subheader("Admin Management", THEME_ADMIN_ACCENT)
            menu_item(24, "Create Admin Account", THEME_ADMIN)
            menu_item(25, "View Admins", THEME_ADMIN)
            menu_item(26, "Deactivate Admin", THEME_ADMIN)

            subheader("Results & Reports", THEME_ADMIN_ACCENT)
            menu_item(27, "View Poll Results", THEME_ADMIN)
            menu_item(28, "View Detailed Statistics", THEME_ADMIN)
            menu_item(29, "View Audit Log", THEME_ADMIN)
            menu_item(30, "Station-wise Results", THEME_ADMIN)

            subheader("System", THEME_ADMIN_ACCENT)
            menu_item(31, "Save Data", THEME_ADMIN)
            menu_item(32, "Logout", THEME_ADMIN)
            print()
            choice = prompt("Enter choice: ")

            actions = {
                "1": self.create_candidate, "2": self.view_all_candidates,
                "3": self.update_candidate, "4": self.delete_candidate,
                "5": self.search_candidates, "6": self.create_station,
                "7": self.view_all_stations, "8": self.update_station,
                "9": self.delete_station, "10": self.create_position,
                "11": self.view_positions, "12": self.update_position,
                "13": self.delete_position, "14": self.create_poll,
                "15": self.view_all_polls, "16": self.update_poll,
                "17": self.delete_poll, "18": self.open_close_poll,
                "19": self.assign_candidates_to_poll, "20": self.view_all_voters,
                "21": self.verify_voter, "22": self.deactivate_voter,
                "23": self.search_voters, "24": self.create_admin,
                "25": self.view_admins, "26": self.deactivate_admin,
                "27": self.view_poll_results, "28": self.view_detailed_statistics,
                "29": self.view_audit_log, "30": self.station_wise_results,
            }

            if choice in actions:
                actions[choice]()
            elif choice == "31":
                self.store.save()
                pause()
            elif choice == "32":
                from services.audit_service import log_action
                log_action(self.store, "LOGOUT", self.session.current_user.username, "Admin logged out")
                self.store.save()
                break
            else:
                error("Invalid choice.")
                pause()

    # ──────────────────────────────────────────────
    # Candidate screens
    # ──────────────────────────────────────────────
    def create_candidate(self):
        clear_screen()
        header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()
        full_name = prompt("Full Name: ")
        if not full_name:
            error("Name cannot be empty.")
            pause()
            return
        national_id = prompt("National ID: ")
        if not national_id:
            error("National ID cannot be empty.")
            pause()
            return
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        gender = prompt("Gender (M/F/Other): ").upper()

        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        try:
            edu_choice = int(prompt("Select education level: "))
            if edu_choice < 1 or edu_choice > len(REQUIRED_EDUCATION_LEVELS):
                error("Invalid choice.")
                pause()
                return
            education = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        except ValueError:
            error("Invalid input.")
            pause()
            return

        party = prompt("Political Party/Affiliation: ")
        manifesto = prompt("Brief Manifesto/Bio: ")
        address = prompt("Address: ")
        phone = prompt("Phone: ")
        email = prompt("Email: ")
        criminal_record = prompt("Has Criminal Record? (yes/no): ")
        years_exp_str = prompt("Years of Public Service/Political Experience: ")
        try:
            years_experience = int(years_exp_str)
        except ValueError:
            years_experience = 0

        try:
            candidate = self.candidate_svc.create(
                data={
                    "full_name": full_name, "national_id": national_id,
                    "date_of_birth": dob_str, "gender": gender,
                    "education": education, "party": party,
                    "manifesto": manifesto, "address": address,
                    "phone": phone, "email": email,
                    "criminal_record": criminal_record,
                    "years_experience": years_experience,
                },
                created_by=self.session.current_user.username,
            )
            print()
            success(f"Candidate '{candidate.full_name}' created successfully! ID: {candidate.id}")
        except ValueError as e:
            error(str(e))
        pause()

    def view_all_candidates(self):
        clear_screen()
        header("ALL CANDIDATES", THEME_ADMIN)
        if not self.store.candidates:
            print()
            info("No candidates found.")
            pause()
            return
        print()
        table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", THEME_ADMIN)
        table_divider(85, THEME_ADMIN)
        for c in self.store.candidates.values():
            badge = status_badge("Active", True) if c.is_active else status_badge("Inactive", False)
            print(f"  {c.id:<5} {c.full_name:<25} {c.party:<20} {c.age:<5} {c.education:<20} {badge}")
        print(f"\n  {DIM}Total Candidates: {len(self.store.candidates)}{RESET}")
        pause()

    def update_candidate(self):
        clear_screen()
        header("UPDATE CANDIDATE", THEME_ADMIN)
        if not self.store.candidates:
            print()
            info("No candidates found.")
            pause()
            return
        print()
        for c in self.store.candidates.values():
            print(f"  {THEME_ADMIN}{c.id}.{RESET} {c.full_name} {DIM}({c.party}){RESET}")
        try:
            cid = int(prompt("\nEnter Candidate ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        c = self.store.candidates.get(cid)
        if not c:
            error("Candidate not found.")
            pause()
            return
        print(f"\n  {BOLD}Updating: {c.full_name}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {
            "full_name": prompt(f"Full Name [{c.full_name}]: "),
            "party": prompt(f"Party [{c.party}]: "),
            "manifesto": prompt(f"Manifesto [{c.manifesto[:50]}...]: "),
            "phone": prompt(f"Phone [{c.phone}]: "),
            "email": prompt(f"Email [{c.email}]: "),
            "address": prompt(f"Address [{c.address}]: "),
        }
        exp_input = prompt(f"Years Experience [{c.years_experience}]: ")
        if exp_input:
            try:
                updates["years_experience"] = int(exp_input)
            except ValueError:
                warning("Invalid number, keeping old value.")
        try:
            self.candidate_svc.update(cid, updates, self.session.current_user.username)
            print()
            success(f"Candidate '{self.store.candidates[cid].full_name}' updated successfully!")
        except ValueError as e:
            error(str(e))
        pause()

    def delete_candidate(self):
        clear_screen()
        header("DELETE CANDIDATE", THEME_ADMIN)
        if not self.store.candidates:
            print()
            info("No candidates found.")
            pause()
            return
        print()
        for c in self.store.candidates.values():
            badge = status_badge("Active", True) if c.is_active else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{c.id}.{RESET} {c.full_name} {DIM}({c.party}){RESET} {badge}")
        try:
            cid = int(prompt("\nEnter Candidate ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        candidate = self.store.candidates.get(cid)
        if not candidate:
            error("Candidate not found.")
            pause()
            return
        if prompt(f"Are you sure you want to delete '{candidate.full_name}'? (yes/no): ").lower() == "yes":
            try:
                self.candidate_svc.deactivate(cid, self.session.current_user.username)
                print()
                success(f"Candidate '{candidate.full_name}' has been deactivated.")
            except ValueError as e:
                error(str(e))
        else:
            info("Deletion cancelled.")
        pause()

    def search_candidates(self):
        clear_screen()
        header("SEARCH CANDIDATES", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Party", THEME_ADMIN)
        menu_item(3, "Education Level", THEME_ADMIN)
        menu_item(4, "Age Range", THEME_ADMIN)
        choice = prompt("\nChoice: ")

        try:
            if choice == "1":
                term = prompt("Enter name to search: ")
                results = self.candidate_svc.search("name", term)
            elif choice == "2":
                term = prompt("Enter party name: ")
                results = self.candidate_svc.search("party", term)
            elif choice == "3":
                subheader("Education Levels", THEME_ADMIN_ACCENT)
                for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
                    print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
                edu_choice = int(prompt("Select: "))
                edu = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
                results = self.candidate_svc.search("education", edu)
            elif choice == "4":
                min_age = int(prompt("Min age: "))
                max_age = int(prompt("Max age: "))
                results = self.candidate_svc.search("age_range", (min_age, max_age))
            else:
                error("Invalid choice.")
                pause()
                return
        except (ValueError, IndexError):
            error("Invalid input.")
            pause()
            return

        if not results:
            print()
            info("No candidates found matching your criteria.")
        else:
            print(f"\n  {BOLD}Found {len(results)} candidate(s):{RESET}")
            table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}", THEME_ADMIN)
            table_divider(75, THEME_ADMIN)
            for c in results:
                print(f"  {c.id:<5} {c.full_name:<25} {c.party:<20} {c.age:<5} {c.education:<20}")
        pause()

    # ──────────────────────────────────────────────
    # Station screens
    # ──────────────────────────────────────────────
    def create_station(self):
        clear_screen()
        header("CREATE VOTING STATION", THEME_ADMIN)
        print()
        name = prompt("Station Name: ")
        location = prompt("Location/Address: ")
        region = prompt("Region/District: ")
        try:
            capacity = int(prompt("Voter Capacity: "))
        except ValueError:
            error("Invalid capacity.")
            pause()
            return
        supervisor = prompt("Station Supervisor Name: ")
        contact = prompt("Contact Phone: ")
        opening_time = prompt("Opening Time (e.g. 08:00): ")
        closing_time = prompt("Closing Time (e.g. 17:00): ")
        try:
            station = self.station_svc.create(
                data={
                    "name": name, "location": location, "region": region,
                    "capacity": capacity, "supervisor": supervisor,
                    "contact": contact, "opening_time": opening_time,
                    "closing_time": closing_time,
                },
                created_by=self.session.current_user.username,
            )
            print()
            success(f"Voting Station '{station.name}' created! ID: {station.id}")
        except ValueError as e:
            error(str(e))
        pause()

    def view_all_stations(self):
        clear_screen()
        header("ALL VOTING STATIONS", THEME_ADMIN)
        if not self.store.voting_stations:
            print()
            info("No voting stations found.")
            pause()
            return
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}",
            THEME_ADMIN,
        )
        table_divider(96, THEME_ADMIN)
        for s in self.store.voting_stations.values():
            reg_count = self.station_svc.voter_count(s.id)
            badge = status_badge("Active", True) if s.is_active else status_badge("Inactive", False)
            print(f"  {s.id:<5} {s.name:<25} {s.location:<25} {s.region:<15} {s.capacity:<8} {reg_count:<8} {badge}")
        print(f"\n  {DIM}Total Stations: {len(self.store.voting_stations)}{RESET}")
        pause()

    def update_station(self):
        clear_screen()
        header("UPDATE VOTING STATION", THEME_ADMIN)
        if not self.store.voting_stations:
            print()
            info("No stations found.")
            pause()
            return
        print()
        for s in self.store.voting_stations.values():
            print(f"  {THEME_ADMIN}{s.id}.{RESET} {s.name} {DIM}- {s.location}{RESET}")
        try:
            sid = int(prompt("\nEnter Station ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        s = self.store.voting_stations.get(sid)
        if not s:
            error("Station not found.")
            pause()
            return
        print(f"\n  {BOLD}Updating: {s.name}{RESET}")
        info("Press Enter to keep current value\n")
        cap_input = prompt(f"Capacity [{s.capacity}]: ")
        capacity = None
        if cap_input:
            try:
                capacity = int(cap_input)
            except ValueError:
                warning("Invalid number, keeping old value.")
        updates = {
            "name": prompt(f"Name [{s.name}]: "),
            "location": prompt(f"Location [{s.location}]: "),
            "region": prompt(f"Region [{s.region}]: "),
            "supervisor": prompt(f"Supervisor [{s.supervisor}]: "),
            "contact": prompt(f"Contact [{s.contact}]: "),
        }
        if capacity:
            updates["capacity"] = capacity
        try:
            self.station_svc.update(sid, updates, self.session.current_user.username)
            print()
            success(f"Station '{self.store.voting_stations[sid].name}' updated successfully!")
        except ValueError as e:
            error(str(e))
        pause()

    def delete_station(self):
        clear_screen()
        header("DELETE VOTING STATION", THEME_ADMIN)
        if not self.store.voting_stations:
            print()
            info("No stations found.")
            pause()
            return
        print()
        for s in self.store.voting_stations.values():
            badge = status_badge("Active", True) if s.is_active else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{s.id}.{RESET} {s.name} {DIM}({s.location}){RESET} {badge}")
        try:
            sid = int(prompt("\nEnter Station ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if sid not in self.store.voting_stations:
            error("Station not found.")
            pause()
            return
        voter_count = self.station_svc.voter_count(sid)
        if voter_count > 0:
            warning(f"{voter_count} voters are registered at this station.")
            if prompt("Proceed with deactivation? (yes/no): ").lower() != "yes":
                info("Cancelled.")
                pause()
                return
        if prompt(f"Confirm deactivation of '{self.store.voting_stations[sid].name}'? (yes/no): ").lower() == "yes":
            try:
                self.station_svc.deactivate(sid, self.session.current_user.username)
                print()
                success(f"Station '{self.store.voting_stations[sid].name}' deactivated.")
            except ValueError as e:
                error(str(e))
        else:
            info("Cancelled.")
        pause()

    # ──────────────────────────────────────────────
    # Position screens
    # ──────────────────────────────────────────────
    def create_position(self):
        clear_screen()
        header("CREATE POSITION", THEME_ADMIN)
        print()
        title = prompt("Position Title (e.g. President, Governor, Senator): ")
        if not title:
            error("Title cannot be empty.")
            pause()
            return
        description = prompt("Description: ")
        level = prompt("Level (National/Regional/Local): ")
        try:
            max_winners = int(prompt("Number of winners/seats: "))
        except ValueError:
            error("Invalid number.")
            pause()
            return
        min_age_str = prompt(f"Minimum candidate age [25]: ")
        min_age = int(min_age_str) if min_age_str.isdigit() else 25
        try:
            position = self.position_svc.create(
                data={
                    "title": title, "description": description,
                    "level": level, "max_winners": max_winners,
                    "min_candidate_age": min_age,
                },
                created_by=self.session.current_user.username,
            )
            print()
            success(f"Position '{position.title}' created! ID: {position.id}")
        except ValueError as e:
            error(str(e))
        pause()

    def view_positions(self):
        clear_screen()
        header("ALL POSITIONS", THEME_ADMIN)
        if not self.store.positions:
            print()
            info("No positions found.")
            pause()
            return
        print()
        table_header(
            f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}",
            THEME_ADMIN,
        )
        table_divider(70, THEME_ADMIN)
        for p in self.store.positions.values():
            badge = status_badge("Active", True) if p.is_active else status_badge("Inactive", False)
            print(f"  {p.id:<5} {p.title:<25} {p.level:<12} {p.max_winners:<8} {p.min_candidate_age:<10} {badge}")
        print(f"\n  {DIM}Total Positions: {len(self.store.positions)}{RESET}")
        pause()

    def update_position(self):
        clear_screen()
        header("UPDATE POSITION", THEME_ADMIN)
        if not self.store.positions:
            print()
            info("No positions found.")
            pause()
            return
        print()
        for p in self.store.positions.values():
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.level}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        p = self.store.positions.get(pid)
        if not p:
            error("Position not found.")
            pause()
            return
        print(f"\n  {BOLD}Updating: {p.title}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {
            "title": prompt(f"Title [{p.title}]: "),
            "description": prompt(f"Description [{p.description[:50]}]: "),
        }
        new_level = prompt(f"Level [{p.level}]: ")
        if new_level and new_level.lower() in POSITION_LEVELS:
            updates["level"] = new_level.capitalize()
        seats_str = prompt(f"Seats [{p.max_winners}]: ")
        if seats_str:
            try:
                updates["max_winners"] = int(seats_str)
            except ValueError:
                warning("Keeping old value.")
        try:
            self.position_svc.update(pid, updates, self.session.current_user.username)
            print()
            success("Position updated!")
        except ValueError as e:
            error(str(e))
        pause()

    def delete_position(self):
        clear_screen()
        header("DELETE POSITION", THEME_ADMIN)
        if not self.store.positions:
            print()
            info("No positions found.")
            pause()
            return
        print()
        for p in self.store.positions.values():
            print(f"  {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.level}){RESET}")
        try:
            pid = int(prompt("\nEnter Position ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in self.store.positions:
            error("Position not found.")
            pause()
            return
        if prompt(f"Confirm deactivation of '{self.store.positions[pid].title}'? (yes/no): ").lower() == "yes":
            try:
                self.position_svc.deactivate(pid, self.session.current_user.username)
                print()
                success("Position deactivated.")
            except ValueError as e:
                error(str(e))
        pause()

    # ──────────────────────────────────────────────
    # Poll screens
    # ──────────────────────────────────────────────
    def create_poll(self):
        clear_screen()
        header("CREATE POLL / ELECTION", THEME_ADMIN)
        print()
        title = prompt("Poll/Election Title: ")
        if not title:
            error("Title cannot be empty.")
            pause()
            return
        description = prompt("Description: ")
        election_type = prompt("Election Type (General/Primary/By-election/Referendum): ")
        start_date = prompt("Start Date (YYYY-MM-DD): ")
        end_date = prompt("End Date (YYYY-MM-DD): ")

        active_positions = {pid: p for pid, p in self.store.positions.items() if p.is_active}
        if not active_positions:
            error("No active positions. Create positions first.")
            pause()
            return

        subheader("Available Positions", THEME_ADMIN_ACCENT)
        for p in active_positions.values():
            print(f"    {THEME_ADMIN}{p.id}.{RESET} {p.title} {DIM}({p.level}) - {p.max_winners} seat(s){RESET}")
        try:
            selected_ids = [int(x.strip()) for x in prompt("\nEnter Position IDs (comma-separated): ").split(",")]
        except ValueError:
            error("Invalid input.")
            pause()
            return

        active_stations = {sid: s for sid, s in self.store.voting_stations.items() if s.is_active}
        if not active_stations:
            error("No active voting stations.")
            pause()
            return

        subheader("Available Voting Stations", THEME_ADMIN_ACCENT)
        for s in active_stations.values():
            print(f"    {THEME_ADMIN}{s.id}.{RESET} {s.name} {DIM}({s.location}){RESET}")

        if prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            selected_station_ids = list(active_stations.keys())
        else:
            try:
                selected_station_ids = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",")]
            except ValueError:
                error("Invalid input.")
                pause()
                return

        try:
            poll = self.poll_svc.create(
                data={
                    "title": title, "description": description,
                    "election_type": election_type, "start_date": start_date,
                    "end_date": end_date, "position_ids": selected_ids,
                    "station_ids": selected_station_ids,
                },
                created_by=self.session.current_user.username,
            )
            print()
            success(f"Poll '{poll.title}' created! ID: {poll.id}")
            warning("Status: DRAFT — Assign candidates and then open the poll.")
        except ValueError as e:
            error(str(e))
        pause()

    def view_all_polls(self):
        clear_screen()
        header("ALL POLLS / ELECTIONS", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        for poll in self.store.polls.values():
            sc = GREEN if poll.status == "open" else (YELLOW if poll.status == "draft" else RED)
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{poll.id}: {poll.title}{RESET}")
            print(f"  {DIM}Type:{RESET} {poll.election_type}  {DIM}│  Status:{RESET} {sc}{BOLD}{poll.status.upper()}{RESET}")
            print(f"  {DIM}Period:{RESET} {poll.start_date} to {poll.end_date}  {DIM}│  Votes:{RESET} {poll.total_votes_cast}")
            for pos in poll.positions:
                cand_names = [
                    self.store.candidates[cid].full_name
                    for cid in pos.candidate_ids
                    if cid in self.store.candidates
                ]
                cand_display = ", ".join(cand_names) if cand_names else f"{DIM}None assigned{RESET}"
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos.position_title}: {cand_display}")
        print(f"\n  {DIM}Total Polls: {len(self.store.polls)}{RESET}")
        pause()

    def update_poll(self):
        clear_screen()
        header("UPDATE POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        print()
        for poll in self.store.polls.values():
            sc = GREEN if poll.status == "open" else (YELLOW if poll.status == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} {sc}({poll.status}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID to update: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        poll = self.store.polls.get(pid)
        if not poll:
            error("Poll not found.")
            pause()
            return
        print(f"\n  {BOLD}Updating: {poll.title}{RESET}")
        info("Press Enter to keep current value\n")
        updates = {
            "title": prompt(f"Title [{poll.title}]: "),
            "description": prompt(f"Description [{poll.description[:50]}]: "),
            "election_type": prompt(f"Election Type [{poll.election_type}]: "),
            "start_date": prompt(f"Start Date [{poll.start_date}]: "),
            "end_date": prompt(f"End Date [{poll.end_date}]: "),
        }
        try:
            self.poll_svc.update(pid, updates, self.session.current_user.username)
            print()
            success("Poll updated!")
        except ValueError as e:
            error(str(e))
        pause()

    def delete_poll(self):
        clear_screen()
        header("DELETE POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        print()
        for poll in self.store.polls.values():
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} {DIM}({poll.status}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID to delete: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if pid not in self.store.polls:
            error("Poll not found.")
            pause()
            return
        if self.store.polls[pid].total_votes_cast > 0:
            warning(f"This poll has {self.store.polls[pid].total_votes_cast} votes recorded.")
        if prompt(f"Confirm deletion of '{self.store.polls[pid].title}'? (yes/no): ").lower() == "yes":
            try:
                title = self.store.polls[pid].title
                self.poll_svc.delete(pid, self.session.current_user.username)
                print()
                success(f"Poll '{title}' deleted.")
            except ValueError as e:
                error(str(e))
        pause()

    def open_close_poll(self):
        clear_screen()
        header("OPEN / CLOSE POLL", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        print()
        for poll in self.store.polls.values():
            sc = GREEN if poll.status == "open" else (YELLOW if poll.status == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title}  {sc}{BOLD}{poll.status.upper()}{RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        poll = self.store.polls.get(pid)
        if not poll:
            error("Poll not found.")
            pause()
            return
        user = self.session.current_user.username
        try:
            if poll.status == "draft":
                if prompt(f"Open poll '{poll.title}'? Voting will begin. (yes/no): ").lower() == "yes":
                    self.poll_svc.open(pid, user)
                    print()
                    success(f"Poll '{poll.title}' is now OPEN for voting!")
            elif poll.status == "open":
                if prompt(f"Close poll '{poll.title}'? No more votes accepted. (yes/no): ").lower() == "yes":
                    self.poll_svc.close(pid, user)
                    print()
                    success(f"Poll '{poll.title}' is now CLOSED.")
            elif poll.status == "closed":
                info("This poll is already closed.")
                if prompt("Reopen it? (yes/no): ").lower() == "yes":
                    self.poll_svc.reopen(pid, user)
                    print()
                    success("Poll reopened!")
        except ValueError as e:
            error(str(e))
        pause()

    def assign_candidates_to_poll(self):
        clear_screen()
        header("ASSIGN CANDIDATES TO POLL", THEME_ADMIN)
        if not self.store.polls or not self.store.candidates:
            print()
            info("No polls or candidates found.")
            pause()
            return
        print()
        for poll in self.store.polls.values():
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} {DIM}({poll.status}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        poll = self.store.polls.get(pid)
        if not poll:
            error("Poll not found.")
            pause()
            return
        if poll.status == "open":
            error("Cannot modify candidates of an open poll.")
            pause()
            return

        for i, pos in enumerate(poll.positions):
            subheader(f"Position: {pos.position_title}", THEME_ADMIN_ACCENT)
            current_names = [
                f"{cid}: {self.store.candidates[cid].full_name}"
                for cid in pos.candidate_ids
                if cid in self.store.candidates
            ]
            if current_names:
                print(f"  {DIM}Current:{RESET} {', '.join(current_names)}")
            else:
                info("No candidates assigned yet.")

            pos_data = self.store.positions.get(pos.position_id, None)
            min_age = pos_data.min_candidate_age if pos_data else 25
            eligible = {
                cid: c for cid, c in self.store.candidates.items()
                if c.is_active and c.is_approved and c.age >= min_age
            }

            if not eligible:
                info("No eligible candidates found.")
                continue

            subheader("Available Candidates", THEME_ADMIN)
            for c in eligible.values():
                marker = f" {GREEN}[ASSIGNED]{RESET}" if c.id in pos.candidate_ids else ""
                print(f"    {THEME_ADMIN}{c.id}.{RESET} {c.full_name} {DIM}({c.party}) - Age: {c.age}, Edu: {c.education}{RESET}{marker}")

            if prompt(f"\nModify candidates for {pos.position_title}? (yes/no): ").lower() == "yes":
                try:
                    new_ids = [int(x.strip()) for x in prompt("Enter Candidate IDs (comma-separated): ").split(",")]
                    valid_ids = [nid for nid in new_ids if nid in eligible]
                    for nid in new_ids:
                        if nid not in eligible:
                            warning(f"Candidate {nid} not eligible. Skipping.")
                    self.poll_svc.assign_candidates(pid, i, valid_ids, self.session.current_user.username)
                    success(f"{len(valid_ids)} candidate(s) assigned.")
                except ValueError:
                    error("Invalid input. Skipping this position.")
        pause()

    # ──────────────────────────────────────────────
    # Voter management screens
    # ──────────────────────────────────────────────
    def view_all_voters(self):
        clear_screen()
        header("ALL REGISTERED VOTERS", THEME_ADMIN)
        if not self.store.voters:
            print()
            info("No voters registered.")
            pause()
            return
        print()
        table_header(
            f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}",
            THEME_ADMIN,
        )
        table_divider(70, THEME_ADMIN)
        for v in self.store.voters.values():
            verified = status_badge("Yes", True) if v.is_verified else status_badge("No", False)
            active = status_badge("Yes", True) if v.is_active else status_badge("No", False)
            print(f"  {v.id:<5} {v.full_name:<25} {v.voter_card_number:<15} {v.station_id:<6} {verified:<19} {active}")
        verified_count = sum(1 for v in self.store.voters.values() if v.is_verified)
        unverified_count = len(self.store.voters) - verified_count
        print(f"\n  {DIM}Total: {len(self.store.voters)}  │  Verified: {verified_count}  │  Unverified: {unverified_count}{RESET}")
        pause()

    def verify_voter(self):
        clear_screen()
        header("VERIFY VOTER", THEME_ADMIN)
        unverified = {vid: v for vid, v in self.store.voters.items() if not v.is_verified}
        if not unverified:
            print()
            info("No unverified voters.")
            pause()
            return
        subheader("Unverified Voters", THEME_ADMIN_ACCENT)
        for v in unverified.values():
            print(f"  {THEME_ADMIN}{v.id}.{RESET} {v.full_name} {DIM}│ NID: {v.national_id} │ Card: {v.voter_card_number}{RESET}")
        print()
        menu_item(1, "Verify a single voter", THEME_ADMIN)
        menu_item(2, "Verify all pending voters", THEME_ADMIN)
        choice = prompt("\nChoice: ")
        if choice == "1":
            try:
                vid = int(prompt("Enter Voter ID: "))
            except ValueError:
                error("Invalid input.")
                pause()
                return
            try:
                self.voter_svc.verify(vid, self.session.current_user.username)
                print()
                success(f"Voter '{self.store.voters[vid].full_name}' verified!")
            except ValueError as e:
                error(str(e))
        elif choice == "2":
            count = self.voter_svc.verify_all_pending(self.session.current_user.username)
            print()
            success(f"{count} voters verified!")
        pause()

    def deactivate_voter(self):
        clear_screen()
        header("DEACTIVATE VOTER", THEME_ADMIN)
        if not self.store.voters:
            print()
            info("No voters found.")
            pause()
            return
        print()
        try:
            vid = int(prompt("Enter Voter ID to deactivate: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        voter = self.store.voters.get(vid)
        if not voter:
            error("Voter not found.")
            pause()
            return
        if prompt(f"Deactivate '{voter.full_name}'? (yes/no): ").lower() == "yes":
            try:
                self.voter_svc.deactivate(vid, self.session.current_user.username)
                print()
                success("Voter deactivated.")
            except ValueError as e:
                error(str(e))
        pause()

    def search_voters(self):
        clear_screen()
        header("SEARCH VOTERS", THEME_ADMIN)
        subheader("Search by", THEME_ADMIN_ACCENT)
        menu_item(1, "Name", THEME_ADMIN)
        menu_item(2, "Voter Card Number", THEME_ADMIN)
        menu_item(3, "National ID", THEME_ADMIN)
        menu_item(4, "Station", THEME_ADMIN)
        choice = prompt("\nChoice: ")
        try:
            if choice == "1":
                results = self.voter_svc.search("name", prompt("Name: "))
            elif choice == "2":
                results = self.voter_svc.search("card", prompt("Card Number: "))
            elif choice == "3":
                results = self.voter_svc.search("national_id", prompt("National ID: "))
            elif choice == "4":
                sid = int(prompt("Station ID: "))
                results = self.voter_svc.search("station", sid)
            else:
                error("Invalid choice.")
                pause()
                return
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if not results:
            print()
            info("No voters found.")
        else:
            print(f"\n  {BOLD}Found {len(results)} voter(s):{RESET}")
            for v in results:
                verified = status_badge("Verified", True) if v.is_verified else status_badge("Unverified", False)
                print(
                    f"  {THEME_ADMIN}ID:{RESET} {v.id}  {DIM}│{RESET}  {v.full_name}"
                    f"  {DIM}│  Card:{RESET} {v.voter_card_number}  {DIM}│{RESET}  {verified}"
                )
        pause()

    # ──────────────────────────────────────────────
    # Admin management screens
    # ──────────────────────────────────────────────
    def create_admin(self):
        clear_screen()
        header("CREATE ADMIN ACCOUNT", THEME_ADMIN)
        if not self.session.is_super_admin():
            print()
            error("Only super admins can create admin accounts.")
            pause()
            return
        print()
        username = prompt("Username: ")
        full_name = prompt("Full Name: ")
        email = prompt("Email: ")
        password = masked_input("Password: ").strip()
        subheader("Available Roles", THEME_ADMIN_ACCENT)
        for key, role in ADMIN_ROLES.items():
            label = ADMIN_ROLE_LABELS.get(role, "")
            menu_item(int(key), f"{role} {DIM}─ {label}{RESET}", THEME_ADMIN)
        role_choice = prompt("\nSelect role (1-4): ")
        role = ADMIN_ROLES.get(role_choice)
        if not role:
            error("Invalid role.")
            pause()
            return
        try:
            admin = self.admin_svc.create(
                data={"username": username, "full_name": full_name, "email": email, "password": password, "role": role},
                created_by=self.session.current_user.username,
            )
            print()
            success(f"Admin '{admin.username}' created with role: {admin.role}")
        except ValueError as e:
            error(str(e))
        pause()

    def view_admins(self):
        clear_screen()
        header("ALL ADMIN ACCOUNTS", THEME_ADMIN)
        print()
        table_header(f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}", THEME_ADMIN)
        table_divider(78, THEME_ADMIN)
        for a in self.store.admins.values():
            active = status_badge("Yes", True) if a.is_active else status_badge("No", False)
            print(f"  {a.id:<5} {a.username:<20} {a.full_name:<25} {a.role:<20} {active}")
        print(f"\n  {DIM}Total Admins: {len(self.store.admins)}{RESET}")
        pause()

    def deactivate_admin(self):
        clear_screen()
        header("DEACTIVATE ADMIN", THEME_ADMIN)
        if not self.session.is_super_admin():
            print()
            error("Only super admins can deactivate admins.")
            pause()
            return
        print()
        for a in self.store.admins.values():
            badge = status_badge("Active", True) if a.is_active else status_badge("Inactive", False)
            print(f"  {THEME_ADMIN}{a.id}.{RESET} {a.username} {DIM}({a.role}){RESET} {badge}")
        try:
            aid = int(prompt("\nEnter Admin ID to deactivate: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        if prompt(f"Deactivate '{self.store.admins.get(aid, {}).username if aid in self.store.admins else '?'}'? (yes/no): ").lower() == "yes":
            try:
                self.admin_svc.deactivate(aid, self.session.current_user.id, self.session.current_user.username)
                print()
                success("Admin deactivated.")
            except ValueError as e:
                error(str(e))
        pause()

    # ──────────────────────────────────────────────
    # Results & reports screens
    # ──────────────────────────────────────────────
    def view_poll_results(self):
        clear_screen()
        header("POLL RESULTS", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        print()
        for poll in self.store.polls.values():
            sc = GREEN if poll.status == "open" else (YELLOW if poll.status == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} {sc}({poll.status}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        poll = self.store.polls.get(pid)
        if not poll:
            error("Poll not found.")
            pause()
            return

        print()
        header(f"RESULTS: {poll.title}", THEME_ADMIN)
        sc = GREEN if poll.status == "open" else RED
        print(f"  {DIM}Status:{RESET} {sc}{BOLD}{poll.status.upper()}{RESET}  {DIM}│  Votes:{RESET} {BOLD}{poll.total_votes_cast}{RESET}")

        turnout = self.results_svc.poll_turnout(pid)
        tc = GREEN if turnout["percentage"] > 50 else (YELLOW if turnout["percentage"] > 25 else RED)
        print(f"  {DIM}Eligible:{RESET} {turnout['eligible']}  {DIM}│  Turnout:{RESET} {tc}{BOLD}{turnout['percentage']:.1f}%{RESET}")

        for pos in poll.positions:
            subheader(f"{pos.position_title} (Seats: {pos.max_winners})", THEME_ADMIN_ACCENT)
            tally = self.results_svc.tally_position(pid, pos.position_id)
            self._render_tally(tally, pos.max_winners, THEME_ADMIN)
        pause()

    def _render_tally(self, tally: dict, max_winners: int, bar_color):
        vote_counts = tally["counts"]
        abstain_count = tally["abstain"]
        total = tally["total"]
        if not vote_counts:
            info("    No votes recorded for this position.")
            return
        for rank, (cid, count) in enumerate(
            sorted(vote_counts.items(), key=lambda x: x[1], reverse=True), 1
        ):
            cand = self.store.candidates.get(cid, None)
            name = cand.full_name if cand else "?"
            party = cand.party if cand else "?"
            pct = (count / total * 100) if total > 0 else 0
            bl = int(pct / 2)
            bar = f"{bar_color}{'█' * bl}{GRAY}{'░' * (50 - bl)}{RESET}"
            winner = f" {BG_GREEN}{BLACK}{BOLD} ★ WINNER {RESET}" if rank <= max_winners else ""
            print(f"    {BOLD}{rank}. {name}{RESET} {DIM}({party}){RESET}")
            print(f"       {bar} {BOLD}{count}{RESET} ({pct:.1f}%){winner}")
        if abstain_count > 0:
            pct = (abstain_count / total * 100) if total > 0 else 0
            print(f"    {GRAY}Abstained: {abstain_count} ({pct:.1f}%){RESET}")

    def view_detailed_statistics(self):
        clear_screen()
        header("DETAILED STATISTICS", THEME_ADMIN)
        overview = self.results_svc.system_overview()

        subheader("SYSTEM OVERVIEW", THEME_ADMIN_ACCENT)
        print(f"  {THEME_ADMIN}Candidates:{RESET}  {overview['total_candidates']} {DIM}(Active: {overview['active_candidates']}){RESET}")
        print(f"  {THEME_ADMIN}Voters:{RESET}      {overview['total_voters']} {DIM}(Verified: {overview['verified_voters']}, Active: {overview['active_voters']}){RESET}")
        print(f"  {THEME_ADMIN}Stations:{RESET}    {overview['total_stations']} {DIM}(Active: {overview['active_stations']}){RESET}")
        print(f"  {THEME_ADMIN}Polls:{RESET}       {overview['total_polls']} "
              f"{DIM}({GREEN}Open: {overview['open_polls']}{RESET}{DIM}, {RED}Closed: {overview['closed_polls']}{RESET}{DIM}, {YELLOW}Draft: {overview['draft_polls']}{RESET}{DIM}){RESET}")
        print(f"  {THEME_ADMIN}Total Votes:{RESET} {overview['total_votes']}")

        demo = self.results_svc.voter_demographics()
        subheader("VOTER DEMOGRAPHICS", THEME_ADMIN_ACCENT)
        tv = overview["total_voters"]
        for g, count in demo["gender"].items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {g}: {count} ({pct:.1f}%)")
        print(f"  {BOLD}Age Distribution:{RESET}")
        for group, count in demo["age_groups"].items():
            pct = (count / tv * 100) if tv > 0 else 0
            print(f"    {group:>5}: {count:>3} ({pct:>5.1f}%) {THEME_ADMIN}{'█' * int(pct / 2)}{RESET}")

        subheader("STATION LOAD", THEME_ADMIN_ACCENT)
        for item in self.results_svc.station_load():
            s = item["station"]
            lp = item["load_pct"]
            lc = RED if lp > 100 else (YELLOW if lp > 75 else GREEN)
            st = f"{RED}{BOLD}OVERLOADED{RESET}" if item["overloaded"] else f"{GREEN}OK{RESET}"
            print(f"    {s.name}: {item['voter_count']}/{s.capacity} {lc}({lp:.0f}%){RESET} {st}")

        subheader("CANDIDATE PARTY DISTRIBUTION", THEME_ADMIN_ACCENT)
        for party, count in sorted(self.results_svc.party_distribution().items(), key=lambda x: x[1], reverse=True):
            print(f"    {party}: {BOLD}{count}{RESET} candidate(s)")

        subheader("CANDIDATE EDUCATION LEVELS", THEME_ADMIN_ACCENT)
        for edu, count in self.results_svc.education_distribution().items():
            print(f"    {edu}: {BOLD}{count}{RESET}")
        pause()

    def station_wise_results(self):
        clear_screen()
        header("STATION-WISE RESULTS", THEME_ADMIN)
        if not self.store.polls:
            print()
            info("No polls found.")
            pause()
            return
        print()
        for poll in self.store.polls.values():
            sc = GREEN if poll.status == "open" else (YELLOW if poll.status == "draft" else RED)
            print(f"  {THEME_ADMIN}{poll.id}.{RESET} {poll.title} {sc}({poll.status}){RESET}")
        try:
            pid = int(prompt("\nEnter Poll ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return
        poll = self.store.polls.get(pid)
        if not poll:
            error("Poll not found.")
            pause()
            return
        print()
        header(f"STATION RESULTS: {poll.title}", THEME_ADMIN)
        for sid in poll.station_ids:
            if sid not in self.store.voting_stations:
                continue
            station = self.store.voting_stations[sid]
            subheader(f"{station.name}  ({station.location})", BRIGHT_WHITE)
            st_data = self.results_svc.station_turnout(pid, sid)
            tc = GREEN if st_data["percentage"] > 50 else (YELLOW if st_data["percentage"] > 25 else RED)
            print(
                f"  {DIM}Registered:{RESET} {st_data['registered']}  "
                f"{DIM}│  Voted:{RESET} {st_data['voted']}  "
                f"{DIM}│  Turnout:{RESET} {tc}{BOLD}{st_data['percentage']:.1f}%{RESET}"
            )
            for pos in poll.positions:
                print(f"    {THEME_ADMIN_ACCENT}▸ {pos.position_title}:{RESET}")
                pos_votes = [v for v in st_data["votes"] if v.position_id == pos.position_id]
                vc = {}
                ac = 0
                for v in pos_votes:
                    if v.abstained:
                        ac += 1
                    else:
                        vc[v.candidate_id] = vc.get(v.candidate_id, 0) + 1
                total = sum(vc.values()) + ac
                for cid, count in sorted(vc.items(), key=lambda x: x[1], reverse=True):
                    cand = self.store.candidates.get(cid)
                    name = cand.full_name if cand else "?"
                    party = cand.party if cand else "?"
                    pct = (count / total * 100) if total > 0 else 0
                    print(f"      {name} {DIM}({party}){RESET}: {BOLD}{count}{RESET} ({pct:.1f}%)")
                if ac > 0:
                    pct = (ac / total * 100) if total > 0 else 0
                    print(f"      {GRAY}Abstained: {ac} ({pct:.1f}%){RESET}")
        pause()

    def view_audit_log(self):
        clear_screen()
        header("AUDIT LOG", THEME_ADMIN)
        if not self.store.audit_log:
            print()
            info("No audit records.")
            pause()
            return
        print(f"\n  {DIM}Total Records: {len(self.store.audit_log)}{RESET}")
        subheader("Filter", THEME_ADMIN_ACCENT)
        menu_item(1, "Last 20 entries", THEME_ADMIN)
        menu_item(2, "All entries", THEME_ADMIN)
        menu_item(3, "Filter by action type", THEME_ADMIN)
        menu_item(4, "Filter by user", THEME_ADMIN)
        choice = prompt("\nChoice: ")
        entries = self.store.audit_log

        if choice == "1":
            entries = self.store.audit_log[-20:]
        elif choice == "3":
            action_types = list(set(e["action"] for e in self.store.audit_log))
            for i, at in enumerate(action_types, 1):
                print(f"    {THEME_ADMIN}{i}.{RESET} {at}")
            try:
                at_choice = int(prompt("Select action type: "))
                entries = [e for e in self.store.audit_log if e["action"] == action_types[at_choice - 1]]
            except (ValueError, IndexError):
                error("Invalid choice.")
                pause()
                return
        elif choice == "4":
            uf = prompt("Enter username/card number: ")
            entries = [e for e in self.store.audit_log if uf.lower() in e["user"].lower()]

        print()
        table_header(f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}", THEME_ADMIN)
        table_divider(100, THEME_ADMIN)
        for entry in entries:
            ac = (
                GREEN if "CREATE" in entry["action"] or entry["action"] == "LOGIN"
                else RED if "DELETE" in entry["action"] or "DEACTIVATE" in entry["action"]
                else YELLOW if "UPDATE" in entry["action"]
                else RESET
            )
            print(
                f"  {DIM}{entry['timestamp'][:19]}{RESET}  "
                f"{ac}{entry['action']:<25}{RESET} "
                f"{entry['user']:<20} "
                f"{DIM}{entry['details'][:50]}{RESET}"
            )
        pause()
