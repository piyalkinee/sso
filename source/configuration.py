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
    "log_level": os.getenv("LOG_LEVEL", "DEBUG"),
    "debug": os.getenv("DEBUG", "True") == "True",
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
        "google_client_id": os.getenv(
            "OAUTH2_GOOGLE_CLIENT_ID",
            "app.apps.googleusercontent.com"
        ),
        "apple_bundle_id": os.getenv(
            "OAUTH2_APPLE_BUNDLE_ID", 
            "com.app.app"
        )
    }
}

global conf


def set_config(config: dict) -> None:
    global conf
    conf = config


set_config(_base_config)
