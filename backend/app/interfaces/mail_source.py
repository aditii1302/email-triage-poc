from typing import Protocol, Iterator
from dataclasses import dataclass


@dataclass
class IncomingEmail:
    file_path: str
    mailbox: str
    raw_bytes: bytes


class MailSource(Protocol):
    def watch(self) -> Iterator[IncomingEmail]: ...
    def mark_processed(self, email: IncomingEmail, destination: str) -> None: ...
