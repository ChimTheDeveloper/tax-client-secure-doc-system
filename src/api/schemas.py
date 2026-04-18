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


class UserRole(str, Enum):
    ADMIN = "admin"
    REVIEWER = "reviewer"
    UPLOADER = "uploader"


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    environment: str


class DependencyHealth(BaseModel):
    name: str
    status: str
    detail: str | None = None


class ReadinessResponse(BaseModel):
    status: str
    version: str
    environment: str
    dependencies: list[DependencyHealth] = Field(default_factory=list)


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


class DocumentSummaryResponse(BaseModel):
    total_documents: int
    pending_review: int
    approved_review: int
    rejected_review: int
    auto_processed: int
    needs_review: int
    by_document_type: dict[str, int] = Field(default_factory=dict)


class ReviewDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewDecisionRequest(BaseModel):
    decision: ReviewDecision
    reviewer_notes: str | None = Field(default=None, max_length=2000)


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: UserRole
    auth_provider: str
    is_active: bool
    created_at: str
    updated_at: str
    last_login_at: str | None = None


class UserListResponse(BaseModel):
    users: list[UserResponse] = Field(default_factory=list)


class InviteUserRequest(BaseModel):
    email: str
    full_name: str = Field(min_length=1, max_length=120)
    role: UserRole


class InviteResponse(BaseModel):
    invite_id: str
    email: str
    full_name: str
    role: UserRole
    invite_url: str
    expires_at: str
    created_at: str


class AcceptInviteRequest(BaseModel):
    token: str
    password: str = Field(min_length=10, max_length=128)


class SessionResponse(BaseModel):
    user: UserResponse
