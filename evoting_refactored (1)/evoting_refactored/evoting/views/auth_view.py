"""
Auth view — login screen and voter self-registration screen.
Handles only user input/output. Delegates logic to services.
"""

from ui.colors import (
    RESET, BOLD, DIM, BRIGHT_YELLOW, BRIGHT_BLUE,
    THEME_LOGIN, THEME_ADMIN, THEME_VOTER,
)
from ui.components import header, menu_item, error, success, warning, info, subheader
from ui.prompts import clear_screen, pause, prompt, masked_input


class AuthView:
    def __init__(self, store, session, voter_svc):
        self.store = store
        self.session = session
        self.voter_svc = voter_svc

    def show_login_menu(self) -> bool:
        """
        Display the main login menu. Returns True when a user successfully
        logs in, False otherwise (so the main loop retries).
        """
        clear_screen()
        header("E-VOTING SYSTEM", THEME_LOGIN)
        print()
        menu_item(1, "Login as Admin", THEME_LOGIN)
        menu_item(2, "Login as Voter", THEME_LOGIN)
        menu_item(3, "Register as Voter", THEME_LOGIN)
        menu_item(4, "Exit", THEME_LOGIN)
        print()
        choice = prompt("Enter choice: ")

        if choice == "1":
            return self._admin_login()
        elif choice == "2":
            return self._voter_login()
        elif choice == "3":
            self._register_voter()
            return False
        elif choice == "4":
            print()
            info("Goodbye!")
            self.store.save()
            exit()
        else:
            error("Invalid choice.")
            pause()
            return False

    def _admin_login(self) -> bool:
        clear_screen()
        header("ADMIN LOGIN", THEME_ADMIN)
        print()
        username = prompt("Username: ")
        password = masked_input("Password: ").strip()
        ok, msg, _ = self.session.login_admin(username, password, self.store.admins)
        if ok:
            from services.audit_service import log_action
            log_action(self.store, "LOGIN", username, "Admin login successful")
            print()
            success(msg)
            pause()
            return True
        else:
            from services.audit_service import log_action
            log_action(self.store, "LOGIN_FAILED", username, msg)
            error(msg)
            pause()
            return False

    def _voter_login(self) -> bool:
        clear_screen()
        header("VOTER LOGIN", THEME_VOTER)
        print()
        voter_card = prompt("Voter Card Number: ")
        password = masked_input("Password: ").strip()
        ok, msg, _ = self.session.login_voter(voter_card, password, self.store.voters)
        if ok:
            from services.audit_service import log_action
            log_action(self.store, "LOGIN", voter_card, "Voter login successful")
            print()
            success(msg)
            pause()
            return True
        else:
            from services.audit_service import log_action
            log_action(self.store, "LOGIN_FAILED", voter_card, msg)
            error(msg)
            pause()
            return False

    def _register_voter(self):
        clear_screen()
        header("VOTER REGISTRATION", THEME_VOTER)
        print()
        full_name = prompt("Full Name: ")
        national_id = prompt("National ID Number: ")
        dob_str = prompt("Date of Birth (YYYY-MM-DD): ")
        gender = prompt("Gender (M/F/Other): ").upper()
        address = prompt("Residential Address: ")
        phone = prompt("Phone Number: ")
        email = prompt("Email Address: ")
        password = masked_input("Create Password: ").strip()
        confirm_password = masked_input("Confirm Password: ").strip()

        if not self.store.voting_stations:
            error("No voting stations available. Contact admin.")
            pause()
            return

        subheader("Available Voting Stations", THEME_VOTER)
        for s in self.store.voting_stations.values():
            if s.is_active:
                print(f"    {BRIGHT_BLUE}{s.id}.{RESET} {s.name} {DIM}- {s.location}{RESET}")

        try:
            station_choice = int(prompt("\nSelect your voting station ID: "))
        except ValueError:
            error("Invalid input.")
            pause()
            return

        try:
            voter = self.voter_svc.register(
                data={
                    "full_name": full_name, "national_id": national_id,
                    "date_of_birth": dob_str, "gender": gender,
                    "address": address, "phone": phone, "email": email,
                    "password": password, "confirm_password": confirm_password,
                    "station_id": station_choice,
                }
            )
            print()
            success("Registration successful!")
            print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{voter.voter_card_number}{RESET}")
            warning("IMPORTANT: Save this number! You need it to login.")
            info("Your registration is pending admin verification.")
        except ValueError as e:
            error(str(e))
        pause()
