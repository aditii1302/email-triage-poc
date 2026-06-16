import pytest
from backend.app.config import settings


def test_config_loads():
    assert settings.LLM_PROVIDER in ('ollama', 'hosted')


def test_config_ollama_url():
    assert settings.OLLAMA_BASE_URL.startswith('http')


def test_config_database_url():
    assert 'sqlite' in settings.DATABASE_URL


def test_config_itsm_urls():
    assert settings.ITSM_A_BASE_URL.startswith('http')
    assert settings.ITSM_B_BASE_URL.startswith('http')


def test_config_directory_url():
    assert settings.DIRECTORY_BASE_URL.startswith('http')
