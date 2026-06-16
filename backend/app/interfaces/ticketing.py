from typing import Protocol
from dataclasses import dataclass


@dataclass
class TicketPayload:
    summary: str
    description: str
    caller: str
    priority: str
    category: str
    application: str
    business_unit: str
    thread_id: str
    dedup_status: str


@dataclass
class CreatedTicket:
    ticket_id: str
    ticket_number: str
    url: str


class TicketingClient(Protocol):
    def create(self, payload: TicketPayload) -> CreatedTicket: ...
    def get(self, ticket_id: str) -> dict: ...
    def update(self, ticket_id: str, fields: dict) -> None: ...
    def close_as_duplicate(self, ticket_id: str, parent_id: str) -> None: ...
