import os


DEFAULT_WEB_PASSWORD = "hf123456"


def get_web_password() -> str:
    return os.environ.get("WEB_PASSWORD", DEFAULT_WEB_PASSWORD)


def get_token_secret() -> str:
    return os.environ.get("AUTH_TOKEN_SECRET", "")


def validate_security_config() -> None:
    web_password = get_web_password()
    token_secret = get_token_secret()
    if web_password == DEFAULT_WEB_PASSWORD:
        raise RuntimeError("WEB_PASSWORD must be set and must not use the default value")
    if len(token_secret) < 32:
        raise RuntimeError("AUTH_TOKEN_SECRET must be set and at least 32 characters long")

