from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, Header, Request

from src.auth.repository import AuthRepository
from src.core.config import get_settings
from src.processing.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
)

ROLE_ADMIN = "admin"
ROLE_REVIEWER = "reviewer"
ROLE_UPLOADER = "uploader"


@dataclass(frozen=True)
class AuthenticatedSubject:
    subject_id: str
    auth_scheme: str
    role: str
    email: str | None = None
    display_name: str | None = None


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token.strip()


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_password_salt() -> str:
    return secrets.token_hex(16)


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        390000,
    ).hex()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    return secrets.compare_digest(hash_password(password, salt), expected_hash)


def create_session_token() -> str:
    return secrets.token_urlsafe(32)


def create_invite_token() -> str:
    return secrets.token_urlsafe(32)


def authenticate_local_user(
    *,
    auth_repository: AuthRepository,
    email: str,
    password: str,
) -> dict[str, str]:
    user = auth_repository.authenticate_user(email)

    if user["auth_provider"] != "local_password":
        raise AuthenticationError("This account uses an external sign-in provider.")

    if not user["password_salt"] or not user["password_hash"]:
        raise AuthenticationError("This account does not have a password configured.")

    if not verify_password(password, user["password_salt"], user["password_hash"]):
        raise AuthenticationError("Authentication failed.")

    return user


def subject_from_user(user: dict[str, str], auth_scheme: str = "session") -> AuthenticatedSubject:
    return AuthenticatedSubject(
        subject_id=user["user_id"],
        auth_scheme=auth_scheme,
        role=user["role"],
        email=user["email"],
        display_name=user["full_name"],
    )


def get_auth_repository(request: Request) -> AuthRepository:
    return request.app.state.auth_repository


def require_authenticated_subject(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> AuthenticatedSubject:
    settings = get_settings()

    if not settings.enable_auth:
        return AuthenticatedSubject(
            subject_id="local-dev",
            auth_scheme="disabled",
            role=ROLE_ADMIN,
            display_name="Local Development",
        )

    provided_token = x_api_key or _extract_bearer_token(authorization)

    if provided_token:
        if not settings.api_keys:
            raise ConfigurationError(
                "Authentication is enabled, but no API keys are configured."
            )

        for candidate_key in settings.api_keys:
            if secrets.compare_digest(provided_token, candidate_key):
                fingerprint = hashlib.sha256(candidate_key.encode("utf-8")).hexdigest()[:12]
                return AuthenticatedSubject(
                    subject_id=f"api-key:{fingerprint}",
                    auth_scheme="api_key",
                    role=ROLE_ADMIN,
                    display_name="Service API Key",
                )

    session_token = request.cookies.get(settings.session_cookie_name)
    if session_token:
        session = get_auth_repository(request).get_session_by_token_hash(hash_token(session_token))
        if session:
            return AuthenticatedSubject(
                subject_id=session["user_id"],
                auth_scheme="session",
                role=session["role"],
                email=session["email"],
                display_name=session["full_name"],
            )

    raise AuthenticationError("Authentication credentials were not provided or were invalid.")


def require_roles(*allowed_roles: str) -> Callable[[AuthenticatedSubject], AuthenticatedSubject]:
    def dependency(
        subject: AuthenticatedSubject = Depends(require_authenticated_subject),
    ) -> AuthenticatedSubject:
        if subject.role not in allowed_roles:
            raise AuthorizationError("You do not have permission to access this resource.")
        return subject

    return dependency
