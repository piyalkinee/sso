import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from source.core.verification_code import (
    generate_verification_code,
    get_code_expiration_time,
    format_phone_number,
)


@pytest.fixture(autouse=True)
def mock_config():
    config = {
        'verification': {
            'code_length': 6,
            'code_ttl': 300,
        }
    }
    with patch('source.core.verification_code.conf', config):
        yield


class TestGenerateVerificationCode:
    def test_returns_string(self):
        assert isinstance(generate_verification_code(), str)

    def test_correct_length(self):
        assert len(generate_verification_code()) == 6

    def test_digits_only(self):
        code = generate_verification_code()
        assert code.isdigit()

    def test_unique_each_call(self):
        codes = {generate_verification_code() for _ in range(20)}
        assert len(codes) > 1

    def test_custom_length(self):
        config = {'verification': {'code_length': 4, 'code_ttl': 300}}
        with patch('source.core.verification_code.conf', config):
            assert len(generate_verification_code()) == 4


class TestGetCodeExpirationTime:
    def test_returns_datetime(self):
        assert isinstance(get_code_expiration_time(), datetime)

    def test_in_future(self):
        assert get_code_expiration_time() > datetime.now(timezone.utc).replace(tzinfo=None)

    def test_ttl_applied(self):
        before = datetime.now(timezone.utc).replace(tzinfo=None)
        exp = get_code_expiration_time()
        after = datetime.now(timezone.utc).replace(tzinfo=None)
        delta = (exp - before).total_seconds()
        assert 299 <= delta <= 301


class TestFormatPhoneNumber:
    def test_plus_format(self):
        assert format_phone_number("+77001234567") == "+77001234567"

    def test_strips_spaces_and_dashes(self):
        assert format_phone_number("+7 700 123-45-67") == "+77001234567"

    def test_8_prefix_converted_to_7(self):
        assert format_phone_number("87001234567") == "+77001234567"

    def test_adds_plus(self):
        assert format_phone_number("77001234567").startswith("+")

    def test_strips_parens(self):
        assert format_phone_number("+7(700)1234567") == "+77001234567"

    def test_international_format(self):
        assert format_phone_number("+1234567890") == "+1234567890"
