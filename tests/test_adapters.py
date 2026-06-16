import pytest
from unittest.mock import patch, MagicMock
from backend.app.adapters.mock_directory import MockDirectoryClient
from backend.app.adapters.hosted_llm import HostedLLMClient


def test_mock_directory_lookup_success():
    client = MockDirectoryClient(base_url='http://localhost:8003')
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        'upn': 'john@example.com',
        'display_name': 'John Smith',
        'department': 'Finance',
        'manager': 'jane@example.com',
    }
    with patch('requests.get', return_value=mock_resp):
        result = client.lookup_by_email('john@example.com')
    assert result is not None
    assert result.display_name == 'John Smith'
    assert result.department == 'Finance'


def test_mock_directory_lookup_not_found():
    client = MockDirectoryClient(base_url='http://localhost:8003')
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    with patch('requests.get', return_value=mock_resp):
        result = client.lookup_by_email('unknown@example.com')
    assert result is None


def test_mock_directory_lookup_connection_error():
    client = MockDirectoryClient(base_url='http://localhost:8003')
    with patch('requests.get', side_effect=Exception('connection refused')):
        result = client.lookup_by_email('john@example.com')
    assert result is None


def test_hosted_llm_classify_intent_raises():
    client = HostedLLMClient()
    with pytest.raises(NotImplementedError):
        client.classify_intent('test email', ['support@example.com'])


def test_hosted_llm_extract_raises():
    client = HostedLLMClient()
    with pytest.raises(NotImplementedError):
        client.extract('test email', [])


def test_hosted_llm_describe_image_raises():
    client = HostedLLMClient()
    with pytest.raises(NotImplementedError):
        client.describe_image(b'fake image bytes')
