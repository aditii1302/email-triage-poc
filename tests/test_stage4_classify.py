import pytest
from unittest.mock import patch, MagicMock
from backend.app.pipeline.stage4_classify import (
    _load_sop_rules,
    _load_app_catalogue,
    _apply_sop_rules,
)


def test_load_sop_rules():
    rules = _load_sop_rules()
    assert isinstance(rules, list)
    assert len(rules) > 0


def test_load_app_catalogue():
    catalogue = _load_app_catalogue()
    assert isinstance(catalogue, dict)
    assert 'hr portal' in catalogue
    assert catalogue['hr portal'] == 'HR Portal'


def test_apply_sop_rules_application_match():
    rules = _load_sop_rules()
    result = _apply_sop_rules(rules, 'HR Portal', 'user cannot log in', '')
    assert result == 'Application Access'


def test_apply_sop_rules_keyword_match():
    rules = _load_sop_rules()
    result = _apply_sop_rules(rules, '', 'password reset required for user', '')
    assert result == 'Identity & Access'


def test_apply_sop_rules_performance_keyword():
    rules = _load_sop_rules()
    result = _apply_sop_rules(rules, '', 'system is very slow and timing out', '')
    assert result == 'Performance'


def test_apply_sop_rules_default():
    rules = _load_sop_rules()
    result = _apply_sop_rules(rules, '', 'general enquiry about something', '')
    assert result == 'General Request'


def test_apply_sop_rules_error_keyword():
    rules = _load_sop_rules()
    result = _apply_sop_rules(rules, '', 'application crashed with exception', '')
    assert result == 'Application Error'
