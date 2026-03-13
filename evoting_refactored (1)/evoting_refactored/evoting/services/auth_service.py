"""
Authentication service — handles password hashing, login validation,
and the current user session. No UI output; returns results to callers.
"""

import hashlib


def hash_password(password: str) -> str:
    """Return the SHA-256 hex digest of a plaintext password."""
    return hashlib.sha256(password.encode()).hexdigest()


class AuthService:
    """Manages the current user session and login verification."""

    def __init__(self):
        self.current_user = None
        self.current_role: str | None = None

    def login_admin(self, username: str, password: str, admins: dict):
        """
        Attempt admin login. Returns (success, message, admin_object).
        """
        hashed = hash_password(password)
        for admin in admins.values():
            if admin.username == username and admin.password == hashed:
                if not admin.is_active:
                    return False, "Account deactivated", None
                self.current_user = admin
                self.current_role = "admin"
                return True, f"Welcome, {admin.full_name}!", admin
        return False, "Invalid credentials", None

    def login_voter(self, voter_card: str, password: str, voters: dict):
        """
        Attempt voter login. Returns (success, message, voter_object).
        """
        hashed = hash_password(password)
        for voter in voters.values():
            if voter.voter_card_number == voter_card and voter.password == hashed:
                if not voter.is_active:
                    return False, "Voter account deactivated", None
                if not voter.is_verified:
                    return False, "Registration not yet verified. Contact an admin.", None
                self.current_user = voter
                self.current_role = "voter"
                return True, f"Welcome, {voter.full_name}!", voter
        return False, "Invalid voter card number or password", None

    def logout(self):
        self.current_user = None
        self.current_role = None

    def is_super_admin(self) -> bool:
        return (
            self.current_user is not None
            and self.current_role == "admin"
            and self.current_user.role == "super_admin"
        )


# Singleton session used across the application
session = AuthService()
