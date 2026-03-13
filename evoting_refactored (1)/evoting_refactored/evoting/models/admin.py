"""
Admin model — represents an administrative user account.
No business logic; only data structure and serialization.
"""


class Admin:
    def __init__(
        self, id, username, password, full_name, email,
        role, created_at, is_active,
    ):
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role
        self.created_at = created_at
        self.is_active = is_active

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
