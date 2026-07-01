from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Optional

from fastapi import Header, HTTPException

from database_sql import session_scope
from sql_models import AdminUser, utc_now


TOKEN_TTL_SECONDS = 12 * 60 * 60


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260000)
    return "pbkdf2_sha256$260000${}${}".format(
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, rounds_text, salt_text, digest_text = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(rounds_text),
        )
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def create_token(user: AdminUser) -> str:
    now = int(time.time())
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "iat": now,
        "exp": now + TOKEN_TTL_SECONDS,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_text = base64.urlsafe_b64encode(payload_bytes).decode("ascii").rstrip("=")
    signature = _sign(payload_text)
    return f"{payload_text}.{signature}"


def decode_token(token: str) -> dict:
    try:
        payload_text, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid admin token") from exc
    if not hmac.compare_digest(_sign(payload_text), signature):
        raise HTTPException(status_code=401, detail="Invalid admin token")
    padded = payload_text + "=" * (-len(payload_text) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="Admin token expired")
    return payload


def get_current_admin(authorization: Optional[str] = Header(default=None)) -> AdminUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing admin token")
    payload = decode_token(authorization.split(" ", 1)[1].strip())
    with session_scope() as session:
        user = session.get(AdminUser, payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Admin user is inactive")
        return user


def touch_login(user_id: str) -> None:
    with session_scope() as session:
        user = session.get(AdminUser, user_id)
        if user:
            user.last_login_at = utc_now()


def _sign(payload_text: str) -> str:
    secret = os.getenv("ADMIN_AUTH_SECRET") or os.getenv("DATA_EXPORT_TOKEN") or "dev-admin-secret-change-me"
    digest = hmac.new(secret.encode("utf-8"), payload_text.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
