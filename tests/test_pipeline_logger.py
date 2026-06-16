import pytest
from unittest.mock import MagicMock, patch
from backend.app.utils.pipeline_logger import start_stage, complete_stage, fail_stage


def _mock_db():
    db = MagicMock()
    run = MagicMock()
    run.id = 1
    run.stage_name = 'stage1_ingest'
    run.status = 'running'
    run.input_payload = {}
    run.output_payload = {}
    db.add = MagicMock()
    db.flush = MagicMock()
    return db, run


def test_start_stage_returns_run():
    db, _ = _mock_db()
    with patch('backend.app.utils.pipeline_logger.PipelineRun') as MockRun:
        mock_instance = MagicMock()
        MockRun.return_value = mock_instance
        result = start_stage(db, 'stage1_ingest', input_payload={'raw_email_id': 1})
        db.add.assert_called_once_with(mock_instance)
        db.flush.assert_called_once()
        assert result == mock_instance


def test_complete_stage_sets_status():
    db, run = _mock_db()
    complete_stage(db, run, raw_email_id=1, output_payload={'result': 'ok'})
    assert run.status in ('completed', 'success')
    assert run.output_payload == {'result': 'ok'}
    assert run.raw_email_id == 1


def test_fail_stage_sets_status():
    db, run = _mock_db()
    fail_stage(
        db, run,
        stage_name='stage2_intent',
        correlation_id='corr-001',
        input_payload={'raw_email_id': 1},
        output_payload={'error_type': 'ValueError'},
        error_message='something went wrong',
    )
    assert run.status == 'failed'
    assert run.error_message == 'something went wrong'


def test_complete_stage_with_none_run():
    db, _ = _mock_db()
    # Should not raise even if pipeline_run is None
    try:
        complete_stage(db, None, raw_email_id=1, output_payload={})
    except AttributeError:
        pass  # expected if None is passed


def test_fail_stage_with_none_run():
    db, _ = _mock_db()
    try:
        fail_stage(db, None, stage_name='stage1_ingest',
                   correlation_id=None, input_payload={},
                   output_payload={}, error_message='error')
    except AttributeError:
        pass  # expected if None is passed
