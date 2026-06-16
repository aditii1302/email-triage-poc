import requests
from backend.app.interfaces.ticketing import CreatedTicket, TicketPayload


class ItsmBClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def create(self, payload: TicketPayload) -> CreatedTicket:
        resp = requests.post(
            f'{self.base_url}/rest/api/2/issue',
            json={
                'fields': {
                    'summary': payload.summary[:200],
                    'description': payload.description,
                    'reporter': payload.caller,
                    'status': 'Open',
                    'priority': payload.priority,
                    'issuetype': 'Incident',
                }
            },
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        return CreatedTicket(
            ticket_id=str(result.get('id', '')),
            ticket_number=result.get('key', ''),
            url=f'{self.base_url}/browse/{result.get("key", "")}',
        )

    def get(self, ticket_id: str) -> dict:
        resp = requests.get(
            f'{self.base_url}/rest/api/2/issue/{ticket_id}',
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def update(self, ticket_id: str, fields: dict) -> None:
        requests.put(
            f'{self.base_url}/rest/api/2/issue/{ticket_id}',
            json={'fields': fields},
            timeout=10,
        ).raise_for_status()

    def close_as_duplicate(self, ticket_id: str, parent_id: str) -> None:
        requests.post(
            f'{self.base_url}/rest/api/2/issue/{ticket_id}/comment',
            json={'body': f'Closed as duplicate of {parent_id}'},
            timeout=10,
        )
        self.update(ticket_id, {'status': 'Closed'})
