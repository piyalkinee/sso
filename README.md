# SSO Service

Authentication microservice supporting Google/Apple OAuth2 and phone OTP (SMS/WhatsApp/Telegram). Issues JWT access + refresh tokens.

## Features

- **OAuth2** — Google and Apple Sign-In
- **Phone OTP** — SMS (Twilio), WhatsApp, Telegram
- **JWT** — access token (17h) + refresh token (365d)
- **Multi-project** — user can be linked to multiple projects
- **PostgreSQL** + Alembic migrations

## Quick Start

```bash
cp .env.example .sso.conf
# edit .sso.conf — set SECRET_KEY, DB credentials, OAuth2 IDs

docker build -t sso .
docker run --env-file .sso.conf -p 9897:9897 sso
```

Swagger UI: `http://localhost:9897/auth/docs`

## Configuration

Copy `.env.example` to `.sso.conf` (or `/etc/sso/sso.conf`) and fill in the values.

| Variable | Description |
|---|---|
| `SECRET_KEY` | JWT signing secret — use a long random string |
| `DEBUG` | `False` in production. When `True`, OTP codes appear in logs and API responses |
| `POSTGRES_*` | PostgreSQL connection |
| `OAUTH2_GOOGLE_CLIENT_ID` | Google Client ID(s), comma-separated for multiple apps |
| `OAUTH2_APPLE_BUNDLE_ID` | Apple app Bundle ID |
| `SMS_PROVIDER` | `mock` / `twilio` / `whatsapp` / `telegram` |

## API

All endpoints are prefixed with `HTTP_PATH_PREFIX` (default `/auth`).

### OAuth2

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/v1/oauth2/login` | Login with Google or Apple token |
| `POST` | `/auth/v1/oauth2/link` | Link OAuth2 provider to existing account |
| `POST` | `/auth/v1/oauth2/refresh` | Refresh access token |

### Phone OTP

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/v1/phone/check` | Check if phone number is registered |
| `POST` | `/auth/v1/phone/send-code` | Send OTP code |
| `POST` | `/auth/v1/phone/verify` | Verify OTP and get tokens |

### Base

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/v1/` | Login with email/password |

## Development

```bash
pip install -e .
cp .env.example .sso.conf
alembic upgrade head
python -m source
```

For local dev set `SMS_PROVIDER=mock` — codes will appear in logs.  
Set `DEV_FIXED_OTP_CODE=123456` + `DEBUG=True` for a fixed OTP during testing.
