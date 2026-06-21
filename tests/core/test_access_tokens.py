import pytest
from unittest.mock import patch

from source.core.access_tokens import generate_token, decode_token, generate_salt
from source.exceptions.auth import InvalidCredentialsError


@pytest.fixture(autouse=True)
def mock_config():
    config = {
        'access_security': {
            'secret_key': 'test-secret-key',
            'algorithm': 'HS256',
        }
    }
    with patch('source.core.access_tokens.conf', config):
        yield


class TestGenerateToken:
    def test_returns_string(self):
        token = generate_token(data={"id": 1}, type="access", ttl=10)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_decodable(self):
        token = generate_token(data={"id": 42}, type="access", ttl=10)
        payload = decode_token(token)
        assert payload["type"] == "access"
        assert payload["sub"] == "42"

    def test_refresh_token_decodable(self):
        token = generate_token(data={"id": 7}, type="refresh", ttl=10)
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_sub_from_id(self):
        token = generate_token(data={"id": 99}, type="access", ttl=10)
        payload = decode_token(token)
        assert payload["sub"] == "99"

    def test_sub_from_sub_field(self):
        token = generate_token(data={"sub": "123"}, type="access", ttl=10)
        payload = decode_token(token)
        assert payload["sub"] == "123"

    def test_roles_from_groups(self):
        data = {"id": 1, "groups": [{"name": "admin"}, {"name": "driver"}]}
        token = generate_token(data=data, type="access", ttl=10)
        payload = decode_token(token)
        assert "admin" in payload["roles"]
        assert "driver" in payload["roles"]

    def test_explicit_roles_override_groups(self):
        data = {"id": 1, "roles": ["passenger"], "groups": [{"name": "admin"}]}
        token = generate_token(data=data, type="access", ttl=10)
        payload = decode_token(token)
        assert payload["roles"] == ["passenger"]

    def test_each_token_has_unique_salt(self):
        t1 = generate_token(data={"id": 1}, type="access", ttl=10)
        t2 = generate_token(data={"id": 1}, type="access", ttl=10)
        assert t1 != t2

    def test_exp_and_iat_present(self):
        token = generate_token(data={"id": 1}, type="access", ttl=60)
        payload = decode_token(token)
        assert "exp" in payload
        assert "iat" in payload
        assert payload["exp"] > payload["iat"]


class TestDecodeToken:
    def test_invalid_token_raises(self):
        with pytest.raises(InvalidCredentialsError):
            decode_token("not.a.valid.token")

    def test_tampered_token_raises(self):
        token = generate_token(data={"id": 1}, type="access", ttl=10)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(InvalidCredentialsError):
            decode_token(tampered)

    def test_wrong_secret_raises(self):
        token = generate_token(data={"id": 1}, type="access", ttl=10)
        other_config = {
            'access_security': {
                'secret_key': 'wrong-secret',
                'algorithm': 'HS256',
            }
        }
        with patch('source.core.access_tokens.conf', other_config):
            with pytest.raises(InvalidCredentialsError):
                decode_token(token)


class TestGenerateSalt:
    def test_returns_string(self):
        assert isinstance(generate_salt(), str)

    def test_not_literal_salt(self):
        assert generate_salt() != "salt"

    def test_unique_each_call(self):
        assert generate_salt() != generate_salt()

    def test_min_length(self):
        assert len(generate_salt()) >= 32
