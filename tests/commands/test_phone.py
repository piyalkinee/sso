import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from source.commands.phone import verify_phone_code, send_phone_code, check_phone
from source.exceptions.auth import InvalidCredentialsError
from source.schemas.phone import PhoneCheckInput, PhoneSendCodeInput, PhoneVerifyCodeInput


BASE_CONF = {
    'debug': False,
    'sms': {'provider': 'mock'},
    'verification': {
        'code_length': 6,
        'code_ttl': 300,
        'max_attempts': 5,
        'dev_fixed_code': '',
    },
    'access_security': {
        'secret_key': 'test-secret',
        'algorithm': 'HS256',
        'access_token_ttl': 60,
        'refresh_token_ttl': 525960,
    },
}


def _make_code_record(code="123456", attempts=0, expired=False, used=False):
    return {
        "id": 1,
        "code": code,
        "attempts": attempts,
        "expires_at": datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=-1 if expired else 300),
        "used_at": datetime.utcnow() if used else None,
    }


def _make_user():
    user = MagicMock()
    user.model_dump.return_value = {
        "id": 42, "sub": "42", "groups": [], "roles": [],
        "info": {}, "oauth": {}, "created_at": None, "updated_at": None,
    }
    return user


# ── check_phone ────────────────────────────────────────────────────────────

class TestCheckPhone:
    async def test_existing_phone_returns_true(self):
        db = AsyncMock()
        with patch('source.commands.phone.qphone.get_user_id_by_phone', AsyncMock(return_value=7)):
            result = await check_phone(db, PhoneCheckInput(phone="+77001234567"))
        assert result.exists is True

    async def test_unknown_phone_returns_false(self):
        db = AsyncMock()
        with patch('source.commands.phone.qphone.get_user_id_by_phone', AsyncMock(return_value=None)):
            result = await check_phone(db, PhoneCheckInput(phone="+77001234567"))
        assert result.exists is False


# ── send_phone_code ────────────────────────────────────────────────────────

class TestSendPhoneCode:
    async def test_mock_provider_always_succeeds(self):
        db = AsyncMock()
        mock_provider = AsyncMock()
        mock_provider.send_code = AsyncMock(return_value=True)

        with patch('source.commands.phone.conf', BASE_CONF), \
             patch('source.commands.phone.qphone.create_verification_code', AsyncMock(return_value="123456")), \
             patch('source.commands.phone.PhoneProviderFactory.get_provider', return_value=mock_provider):
            result = await send_phone_code(db, PhoneSendCodeInput(phone="+77001234567", provider="sms"))

        assert result.success is True

    async def test_allowlisted_phone_exposes_fixed_code(self):
        db = AsyncMock()
        debug_conf = {
            **BASE_CONF,
            'debug': True,
            'verification': {
                **BASE_CONF['verification'],
                'dev_fixed_code': '654321',
                'dev_fixed_phones': {'+77001234567'},
            },
        }

        with patch('source.commands.phone.conf', debug_conf), \
             patch('source.commands.phone.qphone.create_verification_code', AsyncMock(return_value="654321")):
            result = await send_phone_code(db, PhoneSendCodeInput(phone="+77001234567", provider="sms"))

        assert result.debug_code == "654321"

    async def test_no_debug_code_in_prod(self):
        db = AsyncMock()
        prod_conf = {**BASE_CONF, 'debug': False, 'sms': {'provider': 'twilio'}}
        mock_provider = AsyncMock()
        mock_provider.send_code = AsyncMock(return_value=True)

        with patch('source.commands.phone.conf', prod_conf), \
             patch('source.commands.phone.qphone.create_verification_code', AsyncMock(return_value="654321")), \
             patch('source.commands.phone.PhoneProviderFactory.get_provider', return_value=mock_provider):
            result = await send_phone_code(db, PhoneSendCodeInput(phone="+77001234567", provider="sms"))

        assert result.debug_code is None


# ── verify_phone_code ──────────────────────────────────────────────────────

class TestVerifyPhoneCode:
    async def test_correct_code_returns_tokens(self):
        db = AsyncMock()
        record = _make_code_record(code="123456")
        user = _make_user()

        with patch('source.commands.phone.conf', BASE_CONF), \
             patch('source.core.access_tokens.conf', BASE_CONF), \
             patch('source.commands.phone.qphone.get_latest_verification_code', AsyncMock(return_value=record)), \
             patch('source.commands.phone.qphone.increment_attempts', AsyncMock()), \
             patch('source.commands.phone.qphone.mark_code_as_used', AsyncMock()), \
             patch('source.commands.phone.qphone.get_user_id_by_phone', AsyncMock(return_value=42)), \
             patch('source.commands.phone.qusers.get_data_for_token', AsyncMock(return_value=user)), \
             patch('source.commands.phone.qtokens.create', AsyncMock()):
            result = await verify_phone_code(
                db, PhoneVerifyCodeInput(phone="+77001234567", code="123456")
            )

        assert result.tokens.access
        assert result.tokens.refresh

    async def test_wrong_code_raises(self):
        db = AsyncMock()
        record = _make_code_record(code="123456")

        with patch('source.commands.phone.conf', BASE_CONF), \
             patch('source.commands.phone.qphone.get_latest_verification_code', AsyncMock(return_value=record)), \
             patch('source.commands.phone.qphone.increment_attempts', AsyncMock()):
            with pytest.raises(InvalidCredentialsError):
                await verify_phone_code(
                    db, PhoneVerifyCodeInput(phone="+77001234567", code="999999")
                )

    async def test_expired_code_raises(self):
        db = AsyncMock()
        record = _make_code_record(expired=True)

        with patch('source.commands.phone.conf', BASE_CONF), \
             patch('source.commands.phone.qphone.get_latest_verification_code', AsyncMock(return_value=record)):
            with pytest.raises(InvalidCredentialsError):
                await verify_phone_code(
                    db, PhoneVerifyCodeInput(phone="+77001234567", code="123456")
                )

    async def test_max_attempts_exceeded_raises(self):
        db = AsyncMock()
        record = _make_code_record(code="123456", attempts=5)

        with patch('source.commands.phone.conf', BASE_CONF), \
             patch('source.commands.phone.qphone.get_latest_verification_code', AsyncMock(return_value=record)), \
             patch('source.commands.phone.qphone.increment_attempts', AsyncMock()):
            with pytest.raises(InvalidCredentialsError):
                await verify_phone_code(
                    db, PhoneVerifyCodeInput(phone="+77001234567", code="123456")
                )

    async def test_new_user_created_is_new_true(self):
        db = AsyncMock()
        record = _make_code_record(code="123456")
        user = _make_user()

        with patch('source.commands.phone.conf', BASE_CONF), \
             patch('source.core.access_tokens.conf', BASE_CONF), \
             patch('source.commands.phone.qphone.get_latest_verification_code', AsyncMock(return_value=record)), \
             patch('source.commands.phone.qphone.increment_attempts', AsyncMock()), \
             patch('source.commands.phone.qphone.mark_code_as_used', AsyncMock()), \
             patch('source.commands.phone.qphone.get_user_id_by_phone', AsyncMock(return_value=None)), \
             patch('source.commands.phone.qphone.create_user_by_phone', AsyncMock(return_value=42)), \
             patch('source.commands.phone.qusers.get_data_for_token', AsyncMock(return_value=user)), \
             patch('source.commands.phone.qtokens.create', AsyncMock()):
            result = await verify_phone_code(
                db, PhoneVerifyCodeInput(phone="+77001234567", code="123456")
            )

        assert result.is_new is True

    async def test_fixed_code_works_for_allowlisted_phone(self):
        db = AsyncMock()
        debug_conf = {
            **BASE_CONF,
            'debug': True,
            'verification': {
                **BASE_CONF['verification'],
                'dev_fixed_code': '000000',
                'dev_fixed_phones': {'+77001234567'},
            },
        }
        user = _make_user()

        with patch('source.commands.phone.conf', debug_conf), \
             patch('source.core.access_tokens.conf', debug_conf), \
             patch('source.commands.phone.qphone.get_latest_verification_code', AsyncMock(return_value=None)), \
             patch('source.commands.phone.qphone.get_user_id_by_phone', AsyncMock(return_value=42)), \
             patch('source.commands.phone.qusers.get_data_for_token', AsyncMock(return_value=user)), \
             patch('source.commands.phone.qtokens.create', AsyncMock()):
            result = await verify_phone_code(
                db, PhoneVerifyCodeInput(phone="+77001234567", code="000000")
            )

        assert result.tokens.access

    async def test_fixed_code_ignored_in_prod(self):
        db = AsyncMock()
        prod_conf = {**BASE_CONF, 'debug': False, 'verification': {**BASE_CONF['verification'], 'dev_fixed_code': '000000'}}

        with patch('source.commands.phone.conf', prod_conf), \
             patch('source.commands.phone.qphone.get_latest_verification_code', AsyncMock(return_value=None)):
            with pytest.raises(InvalidCredentialsError):
                await verify_phone_code(
                    db, PhoneVerifyCodeInput(phone="+77001234567", code="000000")
                )
