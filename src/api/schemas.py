from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    SUCCESS = "success"
    NEEDS_REVIEW = "needs_review"


class HealthResponse(BaseModel):
    status: str = "ok"


class UploadUrlResponse(BaseModel):
    upload_url: str
    filename: str


class UploadDocumentResponse(BaseModel):
    status: ProcessingStatus
    file_name: str
    file_size: int = Field(ge=0)
    document_type: str
    confidence: float = Field(ge=0, le=1)
    requires_manual_review: bool
    warnings: list[str] = Field(default_factory=list)
    field_confidence: dict[str, str] = Field(default_factory=dict)
    data: dict[str, Any] = Field(default_factory=dict)

