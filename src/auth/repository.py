from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from src.processing.exceptions import AuthenticationError, ConflictError, NotFoundError


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _iso_after_hours(hours: int) -> str:
    return (_utc_now() + timedelta(hours=hours)).isoformat()


def _is_expired(iso_value: str) -> bool:
    return datetime.fromisoformat(iso_value) <= _utc_now()


@dataclass(frozen=True)
class AuthRepository:
    database_path: str

    def __post_init__(self) -> None:
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        database_file = Path(self.database_path)
        if database_file.parent and not database_file.parent.exists():
            database_file.parent.mkdir(parents=True, exist_ok=True)

        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    auth_provider TEXT NOT NULL,
                    password_salt TEXT,
                    password_hash TEXT,
                    is_active INTEGER NOT NULL,
                    invited_by TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_login_at TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_invites (
                    invite_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,
                    created_by TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    accepted_at TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
                """
                )
            connection.commit()

    def count_users(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        return int(row["count"] or 0)

    def seed_bootstrap_admin(
        self,
        *,
        email: str,
        full_name: str,
        password_hash: str,
        password_salt: str,
    ) -> dict[str, Any]:
        existing = self.get_user_by_email(email, raise_if_missing=False)
        if existing:
            return existing

        timestamp = _utc_now_iso()
        user_id = str(uuid.uuid4())

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    user_id,
                    email,
                    full_name,
                    role,
                    auth_provider,
                    password_salt,
                    password_hash,
                    is_active,
                    invited_by,
                    created_at,
                    updated_at,
                    last_login_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    email.lower(),
                    full_name,
                    "admin",
                    "local_password",
                    password_salt,
                    password_hash,
                    1,
                    None,
                    timestamp,
                    timestamp,
                    None,
                ),
            )
            connection.commit()

        return self.get_user_by_id(user_id)

    def create_invite(
        self,
        *,
        email: str,
        full_name: str,
        role: str,
        created_by: str,
        token_hash: str,
        invite_duration_hours: int,
    ) -> dict[str, Any]:
        normalized_email = email.strip().lower()

        if self.get_user_by_email(normalized_email, raise_if_missing=False):
            raise ConflictError(f"An active user with email '{normalized_email}' already exists.")

        existing_invite = self.get_invite_by_email(normalized_email, raise_if_missing=False)
        if existing_invite and not existing_invite["accepted_at"] and not _is_expired(existing_invite["expires_at"]):
            raise ConflictError(f"A pending invite already exists for '{normalized_email}'.")

        invite_id = str(uuid.uuid4())
        created_at = _utc_now_iso()
        expires_at = _iso_after_hours(invite_duration_hours)

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO user_invites (
                    invite_id,
                    email,
                    full_name,
                    role,
                    token_hash,
                    created_by,
                    expires_at,
                    accepted_at,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    full_name = excluded.full_name,
                    role = excluded.role,
                    token_hash = excluded.token_hash,
                    created_by = excluded.created_by,
                    expires_at = excluded.expires_at,
                    accepted_at = NULL,
                    created_at = excluded.created_at
                """,
                (
                    invite_id,
                    normalized_email,
                    full_name.strip(),
                    role,
                    token_hash,
                    created_by,
                    expires_at,
                    None,
                    created_at,
                ),
            )
            connection.commit()

        return self.get_invite_by_email(normalized_email)

    def accept_invite(
        self,
        *,
        token_hash: str,
        password_hash: str,
        password_salt: str,
    ) -> dict[str, Any]:
        invite = self.get_invite_by_token_hash(token_hash)

        if invite["accepted_at"]:
            raise ConflictError("This invite has already been accepted.")

        if _is_expired(invite["expires_at"]):
            raise AuthenticationError("This invite has expired.")

        timestamp = _utc_now_iso()
        user_id = str(uuid.uuid4())

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    user_id,
                    email,
                    full_name,
                    role,
                    auth_provider,
                    password_salt,
                    password_hash,
                    is_active,
                    invited_by,
                    created_at,
                    updated_at,
                    last_login_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    invite["email"],
                    invite["full_name"],
                    invite["role"],
                    "local_password",
                    password_salt,
                    password_hash,
                    1,
                    invite["created_by"],
                    timestamp,
                    timestamp,
                    None,
                ),
            )
            connection.execute(
                """
                UPDATE user_invites
                SET accepted_at = ?
                WHERE invite_id = ?
                """,
                (timestamp, invite["invite_id"]),
            )
            connection.commit()

        return self.get_user_by_id(user_id)

    def create_session(
        self,
        *,
        user_id: str,
        token_hash: str,
        session_duration_hours: int,
    ) -> dict[str, Any]:
        session_id = str(uuid.uuid4())
        timestamp = _utc_now_iso()
        expires_at = _iso_after_hours(session_duration_hours)

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO user_sessions (
                    session_id,
                    user_id,
                    token_hash,
                    expires_at,
                    created_at,
                    last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    user_id,
                    token_hash,
                    expires_at,
                    timestamp,
                    timestamp,
                ),
            )
            connection.execute(
                """
                UPDATE users
                SET last_login_at = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (timestamp, timestamp, user_id),
            )
            connection.commit()

        return self.get_session_by_token_hash(token_hash)

    def get_session_by_token_hash(self, token_hash: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    s.session_id,
                    s.user_id,
                    s.expires_at,
                    s.created_at,
                    s.last_seen_at,
                    u.email,
                    u.full_name,
                    u.role,
                    u.auth_provider,
                    u.is_active,
                    u.last_login_at
                FROM user_sessions s
                JOIN users u ON u.user_id = s.user_id
                WHERE s.token_hash = ?
                """,
                (token_hash,),
            ).fetchone()

        if not row:
            return None

        session = self._row_to_session(row)
        if _is_expired(session["expires_at"]) or not session["is_active"]:
            self.delete_session(token_hash)
            return None

        with self._connect() as connection:
            connection.execute(
                "UPDATE user_sessions SET last_seen_at = ? WHERE token_hash = ?",
                (_utc_now_iso(), token_hash),
            )
            connection.commit()

        return session

    def delete_session(self, token_hash: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM user_sessions WHERE token_hash = ?", (token_hash,))
            connection.commit()

    def authenticate_user(self, email: str) -> dict[str, Any]:
        user = self.get_user_by_email(email)
        if not user["is_active"]:
            raise AuthenticationError("This user account is inactive.")
        return user

    def list_users(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM users
                ORDER BY created_at ASC
                """
            ).fetchall()

        return [self._row_to_user(row) for row in rows]

    def get_user_by_id(self, user_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()

        if not row:
            raise NotFoundError(f"User '{user_id}' was not found.")

        return self._row_to_user(row)

    def get_user_by_email(
        self,
        email: str,
        *,
        raise_if_missing: bool = True,
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM users WHERE email = ?",
                (email.strip().lower(),),
            ).fetchone()

        if not row:
            if raise_if_missing:
                raise AuthenticationError("Authentication failed.")
            return None

        return self._row_to_user(row)

    def get_invite_by_token_hash(self, token_hash: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM user_invites WHERE token_hash = ?",
                (token_hash,),
            ).fetchone()

        if not row:
            raise AuthenticationError("Invite token is invalid.")

        return self._row_to_invite(row)

    def get_invite_by_email(
        self,
        email: str,
        *,
        raise_if_missing: bool = True,
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM user_invites WHERE email = ?",
                (email.strip().lower(),),
            ).fetchone()

        if not row:
            if raise_if_missing:
                raise NotFoundError(f"No invite was found for '{email}'.")
            return None

        return self._row_to_invite(row)

    def _row_to_user(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "user_id": row["user_id"],
            "email": row["email"],
            "full_name": row["full_name"],
            "role": row["role"],
            "auth_provider": row["auth_provider"],
            "password_salt": row["password_salt"],
            "password_hash": row["password_hash"],
            "is_active": bool(row["is_active"]),
            "invited_by": row["invited_by"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "last_login_at": row["last_login_at"],
        }

    def _row_to_invite(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "invite_id": row["invite_id"],
            "email": row["email"],
            "full_name": row["full_name"],
            "role": row["role"],
            "token_hash": row["token_hash"],
            "created_by": row["created_by"],
            "expires_at": row["expires_at"],
            "accepted_at": row["accepted_at"],
            "created_at": row["created_at"],
        }

    def _row_to_session(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "session_id": row["session_id"],
            "user_id": row["user_id"],
            "expires_at": row["expires_at"],
            "created_at": row["created_at"],
            "last_seen_at": row["last_seen_at"],
            "email": row["email"],
            "full_name": row["full_name"],
            "role": row["role"],
            "auth_provider": row["auth_provider"],
            "is_active": bool(row["is_active"]),
            "last_login_at": row["last_login_at"],
        }
