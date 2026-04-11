from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from fastapi import Header

from src.core.config import get_settings
from src.processing.exceptions import AuthenticationError, ConfigurationError


@dataclass(frozen=True)
class AuthenticatedSubject:
    subject_id: str
    auth_scheme: str


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token.strip()


def require_api_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> AuthenticatedSubject:
    settings = get_settings()

    if not settings.enable_auth:
        return AuthenticatedSubject(subject_id="anonymous", auth_scheme="disabled")

    if not settings.api_keys:
        raise ConfigurationError(
            "Authentication is enabled, but no API keys are configured."
        )

    provided_token = x_api_key or _extract_bearer_token(authorization)

    if not provided_token:
        raise AuthenticationError("Authentication credentials were not provided.")

    for candidate_key in settings.api_keys:
        if secrets.compare_digest(provided_token, candidate_key):
            fingerprint = hashlib.sha256(candidate_key.encode("utf-8")).hexdigest()[:12]
            return AuthenticatedSubject(
                subject_id=f"api-key:{fingerprint}",
                auth_scheme="api_key",
            )

    raise AuthenticationError("Authentication failed.")
