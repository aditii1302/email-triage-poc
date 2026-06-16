import pytest
from unittest.mock import patch, MagicMock
from backend.app.adapters.itsm_a_client import ItsmAClient
from backend.app.adapters.itsm_b_client import ItsmBClient
from backend.app.interfaces.ticketing import TicketPayload


SAMPLE_PAYLOAD = TicketPayload(
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


def test_itsm_a_create_ticket():
    client = ItsmAClient(base_url='http://localhost:8001')
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        'result': {
            'sys_id': 'abc-123',
            'number': 'INC0010001',
        }
    }
    with patch('requests.post', return_value=mock_resp):
        result = client.create(SAMPLE_PAYLOAD)
    assert result.ticket_number == 'INC0010001'
    assert result.ticket_id == 'abc-123'


def test_itsm_a_get_ticket():
    client = ItsmAClient(base_url='http://localhost:8001')
    mock_resp = MagicMock()
    mock_resp.json.return_value = {'result': {'sys_id': 'abc-123', 'state': 'new'}}
    with patch('requests.get', return_value=mock_resp):
        result = client.get('abc-123')
    assert result['state'] == 'new'


def test_itsm_a_update_ticket():
    client = ItsmAClient(base_url='http://localhost:8001')
    mock_resp = MagicMock()
    with patch('requests.patch', return_value=mock_resp):
        client.update('abc-123', {'state': 'resolved'})
    mock_resp.raise_for_status.assert_called_once()


def test_itsm_b_create_ticket():
    client = ItsmBClient(base_url='http://localhost:8002')
    mock_resp = MagicMock()
    mock_resp.json.return_value = {'id': '1', 'key': 'SUP-101'}
    with patch('requests.post', return_value=mock_resp):
        result = client.create(SAMPLE_PAYLOAD)
    assert result.ticket_number == 'SUP-101'


def test_itsm_b_get_ticket():
    client = ItsmBClient(base_url='http://localhost:8002')
    mock_resp = MagicMock()
    mock_resp.json.return_value = {'key': 'SUP-101', 'status': 'Open'}
    with patch('requests.get', return_value=mock_resp):
        result = client.get('SUP-101')
    assert result['status'] == 'Open'


def test_itsm_b_close_as_duplicate():
    client = ItsmBClient(base_url='http://localhost:8002')
    mock_resp = MagicMock()
    with patch('requests.post', return_value=mock_resp),          patch('requests.put', return_value=mock_resp):
        client.close_as_duplicate('SUP-102', 'SUP-101')
    mock_resp.raise_for_status.assert_called()
