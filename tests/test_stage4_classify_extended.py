import pytest
from unittest.mock import patch, MagicMock
from backend.app.pipeline.stage4_classify import (
    _load_sop_rules,
    _load_settings,
    _load_app_catalogue,
    _apply_sop_rules,
    run_classification,
)


def test_load_settings():
    settings = _load_settings()
    assert 'dedup' in settings
    assert 'priority_default' in settings


def test_apply_sop_rules_finance_app():
    rules = _load_sop_rules()
    result = _apply_sop_rules(rules, 'Finance System', 'cannot access finance portal', '')
    assert result == 'Financial Systems'


def test_apply_sop_rules_install_keyword():
    rules = _load_sop_rules()
    result = _apply_sop_rules(rules, '', 'need to install new version of software', '')
    assert result == 'Software Installation'


def test_apply_sop_rules_case_insensitive():
    rules = _load_sop_rules()
    result = _apply_sop_rules(rules, 'hr portal', 'cannot log in', '')
    assert result == 'Application Access'


def test_catalogue_alias_resolution():
    catalogue = _load_app_catalogue()
    assert catalogue.get('hrp') == 'HR Portal'
    assert catalogue.get('finsys') == 'Finance System'
    assert catalogue.get('vpn') == 'VPN Client'


def test_run_classification_uses_stated_category():
    mock_db = MagicMock()
    mock_email = MagicMock()
    mock_email.id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = mock_email

    extraction = {
        'problem_statement': 'User cannot login',
        'impacted_application': 'HR Portal',
        'impacted_business_unit': 'Finance',
        'stated_category': 'Hardware Issue',
        'extraction_confidence': 0.9,
    }

    with patch('backend.app.pipeline.stage4_classify.SessionLocal', return_value=mock_db),          patch('backend.app.pipeline.stage4_classify.start_stage', return_value=MagicMock()),          patch('backend.app.pipeline.stage4_classify.complete_stage'),          patch('backend.app.pipeline.stage4_classify._load_sop_rules', return_value=[]),          patch('backend.app.pipeline.stage4_classify._load_settings', return_value={'priority_default': 'P3'}),          patch('backend.app.pipeline.stage4_classify._load_app_catalogue', return_value={}):
        result = run_classification(1, extraction)

    assert result['category'] == 'Hardware Issue'
    assert result['stated_category_used'] is True


def test_run_classification_priority_default():
    mock_db = MagicMock()
    mock_email = MagicMock()
    mock_email.id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = mock_email

    extraction = {
        'problem_statement': 'system is slow',
        'impacted_application': '',
        'impacted_business_unit': '',
        'stated_category': None,
        'extraction_confidence': 0.7,
    }

    with patch('backend.app.pipeline.stage4_classify.SessionLocal', return_value=mock_db),          patch('backend.app.pipeline.stage4_classify.start_stage', return_value=MagicMock()),          patch('backend.app.pipeline.stage4_classify.complete_stage'),          patch('backend.app.pipeline.stage4_classify._load_sop_rules') as mock_rules,          patch('backend.app.pipeline.stage4_classify._load_settings', return_value={'priority_default': 'P3'}),          patch('backend.app.pipeline.stage4_classify._load_app_catalogue', return_value={}):
        mock_rules.return_value = [{'default': True, 'category': 'General Request'}]
        result = run_classification(1, extraction)

    assert result['priority'] == 'P3'
