"""
Admin account service — handles creating and deactivating admin accounts.
No UI output.
"""

import datetime

from config import MIN_PASSWORD_LENGTH, ADMIN_ROLES
from models.admin import Admin
from services.auth_service import hash_password
from services.audit_service import log_action


class AdminService:
    def __init__(self, store):
        self.store = store

    def create(self, data: dict, created_by: str) -> Admin:
        if not data["username"]:
            raise ValueError("Username cannot be empty.")
        for a in self.store.admins.values():
            if a.username == data["username"]:
                raise ValueError("Username already exists.")
        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        if data["role"] not in ADMIN_ROLES.values():
            raise ValueError("Invalid role.")

        admin = Admin(
            id=self.store.admin_id_counter,
            username=data["username"],
            password=hash_password(data["password"]),
            full_name=data["full_name"],
            email=data["email"],
            role=data["role"],
            created_at=str(datetime.datetime.now()),
            is_active=True,
        )
        self.store.admins[admin.id] = admin
        self.store.admin_id_counter += 1
        log_action(self.store, "CREATE_ADMIN", created_by, f"Created admin: {admin.username} (Role: {admin.role})")
        self.store.save()
        return admin

    def deactivate(self, admin_id: int, current_admin_id: int, deactivated_by: str):
        admin = self.store.admins.get(admin_id)
        if not admin:
            raise ValueError("Admin not found.")
        if admin_id == current_admin_id:
            raise ValueError("Cannot deactivate your own account.")
        admin.is_active = False
        log_action(self.store, "DEACTIVATE_ADMIN", deactivated_by, f"Deactivated admin: {admin.username}")
        self.store.save()
