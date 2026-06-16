import os
import pytest
from backend.app.parsing.eml_parser import parse_eml


def test_parse_eml_basic(tmp_path):
    eml_content = """From: john@example.com
To: support@example.com
Subject: Cannot login to HR Portal
Message-ID: <test-001@example.com>

Hi team,

I cannot log into the HR Portal. Getting AUTH-401 error.

Regards,
John
"""
    eml_path = str(tmp_path / 'test.eml')
    with open(eml_path, 'w') as f:
        f.write(eml_content)

    result = parse_eml(eml_path)
    assert result['subject'] == 'Cannot login to HR Portal'
    assert result['sender'] == 'john@example.com'
    assert result['message_id'] == '<test-001@example.com>'
    assert 'AUTH-401' in result['body']


def test_parse_eml_extracts_conversation_id(tmp_path):
    eml_content = """From: john@example.com
To: support@example.com
Subject: Re: HR Portal issue
Message-ID: <test-002@example.com>
In-Reply-To: <original-001@example.com>

Following up on this issue.
"""
    eml_path = str(tmp_path / 'reply.eml')
    with open(eml_path, 'w') as f:
        f.write(eml_content)

    result = parse_eml(eml_path)
    assert result['conversation_id'] == '<original-001@example.com>'


def test_parse_eml_no_message_id(tmp_path):
    eml_content = """From: john@example.com
To: support@example.com
Subject: Test email

Body text here.
"""
    eml_path = str(tmp_path / 'noid.eml')
    with open(eml_path, 'w') as f:
        f.write(eml_content)

    result = parse_eml(eml_path)
    assert result['subject'] == 'Test email'
    assert result['conversation_id'] is not None
