import os
import pathlib
from dotenv import load_dotenv

pr = pathlib.Path(__file__).parent.resolve()

if os.path.exists("/etc/sso/sso.conf"):
    fn = "/etc/sso/sso.conf"
elif os.path.exists(f"{pr}/../.sso.conf"):
    fn = f"{pr}/../.sso.conf"
else:
    fn = None

if fn:
    load_dotenv(dotenv_path=fn)

_base_config = {
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "debug": os.getenv("DEBUG", "False") == "True",
    "workers": int(os.getenv("WORKERS", 1)),
    "api": {
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": os.getenv("API_PORT", "9897"),
        "ssl": os.getenv("SSL", "True") == "True"
    },
    "http": {
        "path_prefix": os.getenv("HTTP_PATH_PREFIX", "/auth")
    },
    "postgres": {
        "host": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "user": os.getenv("POSTGRES_USER", "user"),
        "password": os.getenv("POSTGRES_PASSWORD", "password"),
        "database": os.getenv("POSTGRES_DATABASE_SSO", "database")
    },
    "access_security": {
        "secret_key": os.getenv("SECRET_KEY", "secret"),
        "algorithm": os.getenv("SSO_ALGORITHM", "HS256"),
        "access_token_ttl": 1020,  # 1020 minutes
        "refresh_token_ttl": 31556926  # 365 days
    },
    "oauth2": {
        "google_client_id": [
            cid.strip()
            for cid in os.getenv("OAUTH2_GOOGLE_CLIENT_ID", "app.apps.googleusercontent.com").split(",")
            if cid.strip()
        ],
        "apple_bundle_id": os.getenv(
            "OAUTH2_APPLE_BUNDLE_ID",
            "com.app.app"
        )
    },
    "verification": {
        "code_length": int(os.getenv("VERIFICATION_CODE_LENGTH", "6")),
        "code_ttl": int(os.getenv("VERIFICATION_CODE_TTL", "300")),
        "max_attempts": int(os.getenv("VERIFICATION_MAX_ATTEMPTS", "5")),
        "dev_fixed_code": os.getenv("DEV_FIXED_OTP_CODE", ""),
    },
    "sms": {
        "provider": os.getenv("SMS_PROVIDER", "mock"),
    },
    "twilio": {
        "account_sid": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "auth_token": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "from_phone": os.getenv("TWILIO_FROM_PHONE", ""),
        "messaging_service_sid": os.getenv("TWILIO_MESSAGING_SERVICE_SID", ""),
    },
    "whatsapp": {
        "api_url": os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v17.0"),
        "phone_number_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        "api_token": os.getenv("WHATSAPP_API_TOKEN", ""),
    },
    "telegram": {
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
    },
}

global conf


def set_config(config: dict) -> None:
    global conf
    conf = config


set_config(_base_config)
