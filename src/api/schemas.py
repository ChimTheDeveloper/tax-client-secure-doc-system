from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    SUCCESS = "success"
    NEEDS_REVIEW = "needs_review"


class ReviewStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class HealthResponse(BaseModel):
    status: str = "ok"


class UploadUrlResponse(BaseModel):
    upload_url: str
    filename: str


class DocumentRecordResponse(BaseModel):
    document_id: str
    original_filename: str
    status: ProcessingStatus
    review_status: ReviewStatus
    file_name: str
    file_size: int = Field(ge=0)
    document_type: str
    confidence: float = Field(ge=0, le=1)
    requires_manual_review: bool
    warnings: list[str] = Field(default_factory=list)
    field_confidence: dict[str, str] = Field(default_factory=dict)
    data: dict[str, Any] = Field(default_factory=dict)
    submitted_by: str
    reviewer_notes: str | None = None
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    created_at: str
    updated_at: str


class UploadDocumentResponse(DocumentRecordResponse):
    pass


class DocumentListResponse(BaseModel):
    documents: list[DocumentRecordResponse] = Field(default_factory=list)


class ReviewDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewDecisionRequest(BaseModel):
    decision: ReviewDecision
    reviewer_notes: str | None = Field(default=None, max_length=2000)
