import base64
import hashlib
import hmac
import json
import os
import time


TOKEN_TTL_SECONDS = int(os.environ.get("AUTH_TOKEN_TTL_SECONDS", "7200"))
TOKEN_SECRET = os.environ.get("AUTH_TOKEN_SECRET", os.environ.get("WEB_PASSWORD", "hf123456"))


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + pad).encode("utf-8"))


def issue_token(subject: str) -> tuple[str, int]:
    now = int(time.time())
    exp = now + TOKEN_TTL_SECONDS
    payload = {"sub": subject, "iat": now, "exp": exp}
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(TOKEN_SECRET.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    token = f"{payload_b64}.{_b64url_encode(signature)}"
    return token, exp


def verify_token(token: str) -> dict:
    if not token or "." not in token:
        raise ValueError("invalid token")
    payload_b64, signature_b64 = token.split(".", 1)
    expected_sig = hmac.new(TOKEN_SECRET.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    actual_sig = _b64url_decode(signature_b64)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("invalid signature")
    payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("token expired")
    return payload
