from typing import Protocol
from dataclasses import dataclass


@dataclass
class UserRecord:
    upn: str
    display_name: str
    department: str | None
    manager: str | None
    location: str | None = None


class DirectoryClient(Protocol):
    def lookup_by_email(self, email: str) -> UserRecord | None: ...
