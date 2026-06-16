import pytest
from unittest.mock import patch, MagicMock


def test_process_email_saves_to_db(tmp_path):
    eml_content = """From: john@example.com
To: support@example.com
Subject: VPN not working
Message-ID: <test-ingest-001@example.com>

I cannot connect to VPN since this morning. Please help.
"""
    eml_path = tmp_path / 'test.eml'
    eml_path.write_text(eml_content)

    mock_db = MagicMock()
    mock_email_record = MagicMock()
    mock_email_record.id = 1
    mock_email_record.subject = 'VPN not working'
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    with patch('backend.app.pipeline.stage1_ingest.SessionLocal', return_value=mock_db),          patch('backend.app.pipeline.stage1_ingest.RawEmail', return_value=mock_email_record):
        from backend.app.pipeline.stage1_ingest import process_email
        result = process_email(str(eml_path))

    assert mock_db.add.call_count >= 1
    mock_db.commit.assert_called_once()


def test_process_email_missing_file():
    with patch('backend.app.pipeline.stage1_ingest.SessionLocal'):
        from backend.app.pipeline.stage1_ingest import process_email
        with pytest.raises(Exception):
            process_email('/nonexistent/path/fake.eml')


def test_process_email_extracts_subject(tmp_path):
    eml_content = """From: alice@example.com
To: support@example.com
Subject: Cannot access SharePoint
Message-ID: <test-ingest-002@example.com>

SharePoint is down for our whole team.
"""
    eml_path = tmp_path / 'test2.eml'
    eml_path.write_text(eml_content)

    mock_db = MagicMock()
    mock_record = MagicMock()
    mock_record.subject = 'Cannot access SharePoint'

    with patch('backend.app.pipeline.stage1_ingest.SessionLocal', return_value=mock_db),          patch('backend.app.pipeline.stage1_ingest.RawEmail', return_value=mock_record):
        from backend.app.pipeline.stage1_ingest import process_email
        result = process_email(str(eml_path))

    assert result.subject == 'Cannot access SharePoint'
