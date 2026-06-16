import pytest
from backend.app.interfaces.vector_store import VectorMatch
from backend.app.interfaces.ticketing import TicketPayload, CreatedTicket
from backend.app.interfaces.directory import UserRecord
from backend.app.interfaces.mail_source import IncomingEmail


def test_vector_match_creation():
    match = VectorMatch(ticket_id='INC001', similarity=0.92, metadata={'application': 'HR Portal'})
    assert match.ticket_id == 'INC001'
    assert match.similarity == 0.92
    assert match.metadata['application'] == 'HR Portal'


def test_ticket_payload_creation():
    payload = TicketPayload(
        summary='Cannot login to HR Portal',
        description='User gets AUTH-401 error',
        caller='john@example.com',
        priority='P3',
        category='Application Access',
        application='HR Portal',
        business_unit='Finance',
        thread_id='thread-001',
        dedup_status='NONE',
    )
    assert payload.summary == 'Cannot login to HR Portal'
    assert payload.priority == 'P3'


def test_created_ticket_creation():
    ticket = CreatedTicket(
        ticket_id='sys-001',
        ticket_number='INC0010001',
        url='http://localhost:8001/incident/sys-001',
    )
    assert ticket.ticket_number == 'INC0010001'


def test_user_record_creation():
    user = UserRecord(
        upn='john@example.com',
        display_name='John Smith',
        department='Finance',
        manager='jane@example.com',
    )
    assert user.display_name == 'John Smith'
    assert user.location is None


def test_incoming_email_creation():
    email = IncomingEmail(
        file_path='mailboxes/inbox_1/new/test.eml',
        mailbox='inbox_1',
        raw_bytes=b'raw email content',
    )
    assert email.mailbox == 'inbox_1'
    assert email.raw_bytes == b'raw email content'
