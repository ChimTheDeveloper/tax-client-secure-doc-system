from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.processing.exceptions import NotFoundError


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class DocumentRepository:
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
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    original_filename TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    document_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    review_status TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    requires_manual_review INTEGER NOT NULL,
                    warnings_json TEXT NOT NULL,
                    field_confidence_json TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    submitted_by TEXT NOT NULL,
                    reviewer_notes TEXT,
                    reviewed_by TEXT,
                    reviewed_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def create_document_record(
        self,
        *,
        original_filename: str,
        processing_result: dict[str, Any],
        submitted_by: str,
    ) -> dict[str, Any]:
        timestamp = _utc_now_iso()
        document_id = str(uuid.uuid4())
        review_status = (
            "pending" if processing_result["requires_manual_review"] else "not_required"
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id,
                    original_filename,
                    file_name,
                    file_size,
                    document_type,
                    status,
                    review_status,
                    confidence,
                    requires_manual_review,
                    warnings_json,
                    field_confidence_json,
                    data_json,
                    submitted_by,
                    reviewer_notes,
                    reviewed_by,
                    reviewed_at,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    original_filename,
                    processing_result["file_name"],
                    processing_result["file_size"],
                    processing_result["document_type"],
                    processing_result["status"],
                    review_status,
                    processing_result["confidence"],
                    int(processing_result["requires_manual_review"]),
                    json.dumps(processing_result["warnings"]),
                    json.dumps(processing_result["field_confidence"]),
                    json.dumps(processing_result["data"]),
                    submitted_by,
                    None,
                    None,
                    None,
                    timestamp,
                    timestamp,
                ),
            )
            connection.commit()

        return self.get_document_record(document_id)

    def get_document_record(self, document_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?",
                (document_id,),
            ).fetchone()

        if not row:
            raise NotFoundError(f"Document '{document_id}' was not found.")

        return self._row_to_record(row)

    def list_document_records(
        self,
        *,
        review_status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        query = "SELECT * FROM documents"
        params: list[Any] = []

        if review_status:
            query += " WHERE review_status = ?"
            params.append(review_status)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()

        return [self._row_to_record(row) for row in rows]

    def update_review_status(
        self,
        *,
        document_id: str,
        decision: str,
        reviewer_notes: str | None,
        reviewed_by: str,
    ) -> dict[str, Any]:
        existing = self.get_document_record(document_id)
        reviewed_at = _utc_now_iso()

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE documents
                SET review_status = ?,
                    reviewer_notes = ?,
                    reviewed_by = ?,
                    reviewed_at = ?,
                    updated_at = ?
                WHERE document_id = ?
                """,
                (
                    decision,
                    reviewer_notes,
                    reviewed_by,
                    reviewed_at,
                    reviewed_at,
                    document_id,
                ),
            )
            connection.commit()

        updated = self.get_document_record(document_id)
        updated["status"] = existing["status"]
        return updated

    def _row_to_record(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "document_id": row["document_id"],
            "original_filename": row["original_filename"],
            "file_name": row["file_name"],
            "file_size": row["file_size"],
            "document_type": row["document_type"],
            "status": row["status"],
            "review_status": row["review_status"],
            "confidence": row["confidence"],
            "requires_manual_review": bool(row["requires_manual_review"]),
            "warnings": json.loads(row["warnings_json"]),
            "field_confidence": json.loads(row["field_confidence_json"]),
            "data": json.loads(row["data_json"]),
            "submitted_by": row["submitted_by"],
            "reviewer_notes": row["reviewer_notes"],
            "reviewed_by": row["reviewed_by"],
            "reviewed_at": row["reviewed_at"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
