import requests
from backend.app.interfaces.ticketing import CreatedTicket, TicketPayload


class ItsmAClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def create(self, payload: TicketPayload) -> CreatedTicket:
        description = (
            f'{payload.description}\n\n'
            f'Impacted Application: {payload.application}\n'
            f'Business Unit: {payload.business_unit}\n'
            f'Source Thread ID: {payload.thread_id}\n'
            f'AI Duplicate Check: {payload.dedup_status}'
        )
        resp = requests.post(
            f'{self.base_url}/api/now/table/incident',
            json={
                'short_description': payload.summary[:200],
                'description': description,
                'caller_id': payload.caller,
                'state': 'new',
                'urgency': '3',
                'impact': '3',
                'assignment_group': payload.category,
            },
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()['result']
        return CreatedTicket(
            ticket_id=result['sys_id'],
            ticket_number=result['number'],
            url=f'{self.base_url}/incident/{result["sys_id"]}',
        )

    def get(self, ticket_id: str) -> dict:
        resp = requests.get(
            f'{self.base_url}/api/now/table/incident/{ticket_id}',
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()['result']

    def update(self, ticket_id: str, fields: dict) -> None:
        requests.patch(
            f'{self.base_url}/api/now/table/incident/{ticket_id}',
            json=fields,
            timeout=10,
        ).raise_for_status()

    def close_as_duplicate(self, ticket_id: str, parent_id: str) -> None:
        self.update(ticket_id, {
            'state': 'resolved',
            'close_notes': f'Duplicate of {parent_id}',
            'resolution_code': 'duplicate',
        })
