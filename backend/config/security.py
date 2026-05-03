import base64
import hashlib
import hmac
import json
import os
import secrets
import string
from dataclasses import dataclass
from pathlib import Path


PASSWORD_LENGTH = 14
PASSWORD_ALPHABET = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
PASSWORD_RECORD_PATH = Path("/app/data/security/web_password.json")
PBKDF2_ITERATIONS = 200_000
PBKDF2_SALT_BYTES = 16


@dataclass
class PasswordInitResult:
    created: bool
    generated_password: str | None = None


def get_token_secret() -> str:
    return os.environ.get("AUTH_TOKEN_SECRET", "")


def validate_security_config() -> None:
    token_secret = get_token_secret()
    if len(token_secret) < 32:
        raise RuntimeError("AUTH_TOKEN_SECRET must be set and at least 32 characters long")


def _resolve_record_path(data_dir: Path | None = None) -> Path:
    if data_dir is None:
        return PASSWORD_RECORD_PATH
    return data_dir / "security" / "web_password.json"


def _hash_password(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return base64.b64encode(digest).decode("ascii")


def _generate_password() -> str:
    while True:
        password = "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(PASSWORD_LENGTH))
        has_lower = any(ch.islower() for ch in password)
        has_upper = any(ch.isupper() for ch in password)
        has_digit = any(ch.isdigit() for ch in password)
        has_special = any(ch in "!@#$%^&*()-_=+" for ch in password)
        if has_lower and has_upper and has_digit and has_special:
            return password


def _write_password(password: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    salt = secrets.token_bytes(PBKDF2_SALT_BYTES)
    record = {
        "hash": _hash_password(password, salt),
        "salt": base64.b64encode(salt).decode("ascii"),
        "iterations": PBKDF2_ITERATIONS,
    }
    path.write_text(json.dumps(record), encoding="utf-8")


def _read_password_record(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_web_password_initialized(data_dir: Path | None = None) -> PasswordInitResult:
    path = _resolve_record_path(data_dir)
    if path.exists():
        return PasswordInitResult(created=False, generated_password=None)
    password = _generate_password()
    _write_password(password, path)
    return PasswordInitResult(created=True, generated_password=password)


def verify_web_password(password: str, data_dir: Path | None = None) -> bool:
    if not password:
        return False
    path = _resolve_record_path(data_dir)
    if not path.exists():
        return False
    record = _read_password_record(path)
    salt = base64.b64decode(record["salt"].encode("ascii"))
    expected_hash = record["hash"]
    iterations = int(record.get("iterations", PBKDF2_ITERATIONS))
    actual_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    actual_hash = base64.b64encode(actual_digest).decode("ascii")
    return hmac.compare_digest(expected_hash, actual_hash)


def reset_web_password(data_dir: Path | None = None) -> str:
    path = _resolve_record_path(data_dir)
    password = _generate_password()
    _write_password(password, path)
    return password
