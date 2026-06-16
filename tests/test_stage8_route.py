import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_run_routing_processed():
    mock_db = MagicMock()
    mock_email = MagicMock()
    mock_email.id = 1
    mock_email.file_path = None
    mock_db.query.return_value.filter.return_value.first.return_value = mock_email

    with patch('backend.app.pipeline.stage8_route.SessionLocal', return_value=mock_db),          patch('backend.app.pipeline.stage8_route.start_stage', return_value=MagicMock()),          patch('backend.app.pipeline.stage8_route.complete_stage'):
        from backend.app.pipeline.stage8_route import run_routing
        result = run_routing(1, is_actionable=True, dedup_status='NONE')

    assert result['destination'] == 'processed'
    assert result['new_path'] is None


def test_run_routing_no_action():
    mock_db = MagicMock()
    mock_email = MagicMock()
    mock_email.id = 1
    mock_email.file_path = None
    mock_db.query.return_value.filter.return_value.first.return_value = mock_email

    with patch('backend.app.pipeline.stage8_route.SessionLocal', return_value=mock_db),          patch('backend.app.pipeline.stage8_route.start_stage', return_value=MagicMock()),          patch('backend.app.pipeline.stage8_route.complete_stage'):
        from backend.app.pipeline.stage8_route import run_routing
        result = run_routing(1, is_actionable=False, dedup_status='NONE')

    assert result['destination'] == 'no_action'


def test_run_routing_review():
    mock_db = MagicMock()
    mock_email = MagicMock()
    mock_email.id = 1
    mock_email.file_path = None
    mock_db.query.return_value.filter.return_value.first.return_value = mock_email

    with patch('backend.app.pipeline.stage8_route.SessionLocal', return_value=mock_db),          patch('backend.app.pipeline.stage8_route.start_stage', return_value=MagicMock()),          patch('backend.app.pipeline.stage8_route.complete_stage'):
        from backend.app.pipeline.stage8_route import run_routing
        result = run_routing(1, is_actionable=True, dedup_status='POSSIBLE-DUPLICATE-REVIEW')

    assert result['destination'] == 'review'


def test_run_routing_email_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with patch('backend.app.pipeline.stage8_route.SessionLocal', return_value=mock_db),          patch('backend.app.pipeline.stage8_route.start_stage', return_value=MagicMock()),          patch('backend.app.pipeline.stage8_route.fail_stage'):
        from backend.app.pipeline.stage8_route import run_routing
        with pytest.raises(ValueError, match='not found'):
            run_routing(99, is_actionable=True, dedup_status='NONE')


def test_run_routing_moves_file(tmp_path):
    src = tmp_path / 'inbox_1' / 'new'
    src.mkdir(parents=True)
    eml = src / 'test.eml'
    eml.write_text('fake email')

    mock_db = MagicMock()
    mock_email = MagicMock()
    mock_email.id = 1
    mock_email.file_path = str(eml)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_email

    with patch('backend.app.pipeline.stage8_route.SessionLocal', return_value=mock_db),          patch('backend.app.pipeline.stage8_route.start_stage', return_value=MagicMock()),          patch('backend.app.pipeline.stage8_route.complete_stage'):
        from backend.app.pipeline.stage8_route import run_routing
        result = run_routing(1, is_actionable=True, dedup_status='NONE')

    assert result['destination'] == 'processed'
    assert result['new_path'] is not None
    assert not eml.exists()
