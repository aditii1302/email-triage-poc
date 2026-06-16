import pytest
from unittest.mock import patch, MagicMock
from backend.app.pipeline.sync_worker import _sync_once, _get_itsm_a_incidents, _get_itsm_b_issues


def test_get_itsm_a_incidents_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {'result': [{'number': 'INC001', 'state': 'new'}]}
    with patch('requests.get', return_value=mock_resp):
        result = _get_itsm_a_incidents()
    assert len(result) == 1
    assert result[0]['number'] == 'INC001'


def test_get_itsm_a_incidents_connection_error():
    with patch('requests.get', side_effect=Exception('connection refused')):
        result = _get_itsm_a_incidents()
    assert result == []


def test_get_itsm_b_issues_success():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {'issues': [{'key': 'SUP-101', 'status': 'Open'}]}
    with patch('requests.post', return_value=mock_resp):
        result = _get_itsm_b_issues()
    assert len(result) == 1
    assert result[0]['key'] == 'SUP-101'


def test_get_itsm_b_issues_connection_error():
    with patch('requests.post', side_effect=Exception('connection refused')):
        result = _get_itsm_b_issues()
    assert result == []


def test_sync_once_no_incidents():
    with patch('backend.app.pipeline.sync_worker._get_itsm_a_incidents', return_value=[]),          patch('backend.app.pipeline.sync_worker._get_itsm_b_issues', return_value=[]):
        _sync_once()  # should not raise


def test_sync_once_state_change_pushes_to_itsm_b():
    from backend.app.pipeline import sync_worker
    sync_worker._last_known = {'INC001': {'state': 'new', 'urgency': '3', 'b_status': 'Open'}}

    incidents = [{'number': 'INC001', 'state': 'resolved', 'urgency': '3', 'sys_id': 'sys-001'}]
    issues = [{'key': 'SUP-101', 'status': 'Open'}]

    mock_resp = MagicMock()
    with patch('backend.app.pipeline.sync_worker._get_itsm_a_incidents', return_value=incidents),          patch('backend.app.pipeline.sync_worker._get_itsm_b_issues', return_value=issues),          patch('requests.put', return_value=mock_resp):
        _sync_once()

    mock_resp.raise_for_status.assert_called()


def test_sync_once_updates_last_known():
    from backend.app.pipeline import sync_worker
    sync_worker._last_known = {}

    incidents = [{'number': 'INC002', 'state': 'new', 'urgency': '3', 'sys_id': 'sys-002'}]
    issues = [{'key': 'SUP-102', 'status': 'Open'}]

    with patch('backend.app.pipeline.sync_worker._get_itsm_a_incidents', return_value=incidents),          patch('backend.app.pipeline.sync_worker._get_itsm_b_issues', return_value=issues):
        _sync_once()

    assert 'INC002' in sync_worker._last_known
    assert sync_worker._last_known['INC002']['state'] == 'new'
