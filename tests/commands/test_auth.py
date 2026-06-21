import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from source.commands.auth import (
    verify_google_token,
    verify_apple_token,
    refresh_access_token,
)
from source.exceptions.auth import InvalidCredentialsError


BASE_CONF = {
    'oauth2': {
        'google_client_id': ['test-client-id.apps.googleusercontent.com'],
        'apple_bundle_id': 'com.test.app',
    },
    'access_security': {
        'secret_key': 'test-secret',
        'algorithm': 'HS256',
        'access_token_ttl': 60,
        'refresh_token_ttl': 525960,
    },
}


# ── Google token verification ──────────────────────────────────────────────

class TestVerifyGoogleToken:
    async def test_valid_token_returns_email(self):
        with patch('source.commands.auth.id_token') as mock_id_token, \
             patch('source.commands.auth.conf', BASE_CONF):
            mock_id_token.verify_oauth2_token.return_value = {'email': 'user@example.com'}
            email = await verify_google_token("valid-token")
            assert email == 'user@example.com'

    async def test_missing_email_raises(self):
        with patch('source.commands.auth.id_token') as mock_id_token, \
             patch('source.commands.auth.conf', BASE_CONF):
            mock_id_token.verify_oauth2_token.return_value = {}
            with pytest.raises(InvalidCredentialsError):
                await verify_google_token("valid-token")

    async def test_google_lib_exception_raises(self):
        with patch('source.commands.auth.id_token') as mock_id_token, \
             patch('source.commands.auth.conf', BASE_CONF):
            mock_id_token.verify_oauth2_token.side_effect = ValueError("bad token")
            with pytest.raises(InvalidCredentialsError):
                await verify_google_token("bad-token")


# ── Apple token verification ───────────────────────────────────────────────

APPLE_JWKS = {
    "keys": [{"kid": "key1", "kty": "RSA", "n": "x", "e": "AQAB"}]
}

APPLE_PAYLOAD = {
    "email": "apple@example.com",
    "iss": "https://appleid.apple.com",
    "aud": "com.test.app",
}


class TestVerifyAppleToken:
    async def test_valid_token_returns_email(self):
        mock_response = MagicMock()
        mock_response.json.return_value = APPLE_JWKS

        with patch('source.commands.auth.httpx.AsyncClient') as mock_client, \
             patch('source.commands.auth.jwt') as mock_jwt, \
             patch('source.commands.auth.conf', BASE_CONF):
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value.get = AsyncMock(return_value=mock_response)
            mock_jwt.get_unverified_header.return_value = {"kid": "key1", "alg": "RS256"}
            mock_jwt.decode.return_value = APPLE_PAYLOAD

            email = await verify_apple_token("valid-apple-token")
            assert email == "apple@example.com"

    async def test_unknown_kid_raises(self):
        mock_response = MagicMock()
        mock_response.json.return_value = APPLE_JWKS

        with patch('source.commands.auth.httpx.AsyncClient') as mock_client, \
             patch('source.commands.auth.jwt') as mock_jwt, \
             patch('source.commands.auth.conf', BASE_CONF):
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value.get = AsyncMock(return_value=mock_response)
            mock_jwt.get_unverified_header.return_value = {"kid": "unknown-kid", "alg": "RS256"}

            with pytest.raises(InvalidCredentialsError):
                await verify_apple_token("token-with-bad-kid")

    async def test_missing_email_raises(self):
        mock_response = MagicMock()
        mock_response.json.return_value = APPLE_JWKS

        with patch('source.commands.auth.httpx.AsyncClient') as mock_client, \
             patch('source.commands.auth.jwt') as mock_jwt, \
             patch('source.commands.auth.conf', BASE_CONF):
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value.get = AsyncMock(return_value=mock_response)
            mock_jwt.get_unverified_header.return_value = {"kid": "key1", "alg": "RS256"}
            mock_jwt.decode.return_value = {"iss": "https://appleid.apple.com"}

            with pytest.raises(InvalidCredentialsError):
                await verify_apple_token("token-without-email")

    async def test_jwks_fetch_error_raises(self):
        with patch('source.commands.auth.httpx.AsyncClient') as mock_client, \
             patch('source.commands.auth.conf', BASE_CONF):
            mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value.get = AsyncMock(side_effect=Exception("network error"))

            with pytest.raises(InvalidCredentialsError):
                await verify_apple_token("any-token")


# ── refresh_access_token ───────────────────────────────────────────────────

class TestRefreshAccessToken:
    async def test_valid_refresh_token_returns_new_tokens(self):
        from source.core.access_tokens import generate_token

        with patch('source.commands.auth.conf', BASE_CONF), \
             patch('source.core.access_tokens.conf', BASE_CONF):
            refresh_token = generate_token(
                data={"id": 1, "project_id": None},
                type="refresh",
                ttl=525960,
            )

        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.model_dump.return_value = {
            "id": 1, "sub": "1", "groups": [], "roles": [],
            "info": {}, "oauth": {}, "created_at": None, "updated_at": None,
        }

        with patch('source.commands.auth.conf', BASE_CONF), \
             patch('source.core.access_tokens.conf', BASE_CONF), \
             patch('source.commands.auth.qusers.get_data_for_token', AsyncMock(return_value=mock_user)), \
             patch('source.commands.auth.qprojects.get_user_project_names', AsyncMock(return_value=[])), \
             patch('source.commands.auth.qtokens.create', AsyncMock()):
            result = await refresh_access_token(database=mock_db, refresh_token=refresh_token)

        assert result.tokens.access
        assert result.tokens.refresh

    async def test_access_token_as_refresh_raises(self):
        from source.core.access_tokens import generate_token

        with patch('source.commands.auth.conf', BASE_CONF), \
             patch('source.core.access_tokens.conf', BASE_CONF):
            access_token = generate_token(data={"id": 1}, type="access", ttl=60)

        mock_db = AsyncMock()
        with patch('source.commands.auth.conf', BASE_CONF), \
             patch('source.core.access_tokens.conf', BASE_CONF):
            with pytest.raises(InvalidCredentialsError):
                await refresh_access_token(database=mock_db, refresh_token=access_token)

    async def test_invalid_token_raises(self):
        mock_db = AsyncMock()
        with patch('source.commands.auth.conf', BASE_CONF), \
             patch('source.core.access_tokens.conf', BASE_CONF):
            with pytest.raises(InvalidCredentialsError):
                await refresh_access_token(database=mock_db, refresh_token="garbage")
