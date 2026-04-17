from __future__ import annotations

import logging
import time
import uuid

from fastapi import Depends, FastAPI, File, Query, Request, UploadFile
from fastapi.responses import JSONResponse

from src.api.schemas import (
    DependencyHealth,
    DocumentListResponse,
    DocumentRecordResponse,
    DocumentSummaryResponse,
    HealthResponse,
    ProcessingStatus,
    ReadinessResponse,
    ReviewDecisionRequest,
    ReviewStatus,
    UploadDocumentResponse,
    UploadUrlResponse,
)
from src.auth.security import AuthenticatedSubject, require_api_key
from src.core.config import get_settings
from src.core.logging import attach_request_context_filter, configure_logging
from src.documents.repository import DocumentRepository
from src.processing.exceptions import ApplicationError, InvalidUploadError
from src.processing.pipeline import process_tax_document
from src.upload.upload import generate_upload_url

configure_logging()
attach_request_context_filter()

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Secure Tax Document Intelligence System",
        version="0.2.0",
    )
    app.state.document_repository = DocumentRepository(settings.database_path)

    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query or ""),
                    "duration_ms": duration_ms,
                    "client_host": request.client.host if request.client else "unknown",
                },
            )

        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError):
        response = JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
            },
        )
        response.headers["X-Request-ID"] = _request_id_from_request(request)
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled exception while processing request",
            exc_info=exc,
            extra={"request_id": _request_id_from_request(request)},
        )
        response = JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_code": "internal_server_error",
            },
        )
        response.headers["X-Request-ID"] = _request_id_from_request(request)
        return response

    @app.get("/health", response_model=HealthResponse)
    def health_check() -> HealthResponse:
        return HealthResponse()

    @app.get("/ready", response_model=ReadinessResponse)
    def readiness_check(request: Request) -> ReadinessResponse:
        dependencies: list[DependencyHealth] = []
        overall_status = "ready"

        document_repository = _get_document_repository(request)
        try:
            document_repository.check_connection()
            dependencies.append(DependencyHealth(name="sqlite", status="ok"))
        except Exception as exc:
            overall_status = "degraded"
            dependencies.append(
                DependencyHealth(name="sqlite", status="error", detail=str(exc))
            )

        if settings.enable_auth and not settings.api_keys:
            overall_status = "degraded"
            dependencies.append(
                DependencyHealth(
                    name="auth",
                    status="error",
                    detail="Authentication is enabled but no API keys are configured.",
                )
            )
        else:
            dependencies.append(
                DependencyHealth(
                    name="auth",
                    status="ok",
                    detail="disabled" if not settings.enable_auth else "configured",
                )
            )

        dependencies.append(
            DependencyHealth(
                name="s3",
                status="ok",
                detail=settings.s3_bucket_name,
            )
        )
        dependencies.append(
            DependencyHealth(
                name="textract_region",
                status="ok",
                detail=settings.aws_region,
            )
        )

        return ReadinessResponse(status=overall_status, dependencies=dependencies)

    @app.get("/generate-upload-url", response_model=UploadUrlResponse)
    def generate_upload_url_endpoint(
        filename: str = Query(..., min_length=1),
        _subject: AuthenticatedSubject = Depends(require_api_key),
    ) -> UploadUrlResponse:
        upload_url, generated_filename = generate_upload_url(
            filename=filename,
            bucket_name=settings.s3_bucket_name,
            region_name=settings.aws_region,
            expires_in=settings.presigned_url_ttl_seconds,
        )
        return UploadUrlResponse(upload_url=upload_url, filename=generated_filename)

    @app.post("/upload", response_model=UploadDocumentResponse)
    async def upload_document(
        request: Request,
        file: UploadFile = File(...),
        subject: AuthenticatedSubject = Depends(require_api_key),
    ) -> UploadDocumentResponse:
        file_bytes = await file.read()

        _validate_upload(file, file_bytes, settings.max_file_size_bytes)

        result = process_tax_document(
            file_bytes=file_bytes,
            original_filename=file.filename or "upload.pdf",
            settings=settings,
        )

        document_repository = _get_document_repository(request)
        record = document_repository.create_document_record(
            original_filename=file.filename or "upload.pdf",
            processing_result=result,
            submitted_by=subject.subject_id,
        )
        return UploadDocumentResponse(**record)

    @app.get("/documents", response_model=DocumentListResponse)
    def list_documents(
        request: Request,
        review_status: ReviewStatus | None = Query(default=None),
        processing_status: ProcessingStatus | None = Query(default=None),
        document_type: str | None = Query(default=None),
        search: str | None = Query(default=None, min_length=1),
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
        _subject: AuthenticatedSubject = Depends(require_api_key),
    ) -> DocumentListResponse:
        document_repository = _get_document_repository(request)
        records = document_repository.list_document_records(
            review_status=review_status.value if review_status else None,
            processing_status=processing_status.value if processing_status else None,
            document_type=document_type,
            search=search,
            limit=limit,
            offset=offset,
        )
        return DocumentListResponse(documents=[DocumentRecordResponse(**record) for record in records])

    @app.get("/documents/summary", response_model=DocumentSummaryResponse)
    def get_document_summary(
        request: Request,
        _subject: AuthenticatedSubject = Depends(require_api_key),
    ) -> DocumentSummaryResponse:
        document_repository = _get_document_repository(request)
        return DocumentSummaryResponse(**document_repository.get_summary())

    @app.get("/documents/{document_id}", response_model=DocumentRecordResponse)
    def get_document(
        document_id: str,
        request: Request,
        _subject: AuthenticatedSubject = Depends(require_api_key),
    ) -> DocumentRecordResponse:
        document_repository = _get_document_repository(request)
        record = document_repository.get_document_record(document_id)
        return DocumentRecordResponse(**record)

    @app.patch("/documents/{document_id}/review", response_model=DocumentRecordResponse)
    def review_document(
        document_id: str,
        payload: ReviewDecisionRequest,
        request: Request,
        subject: AuthenticatedSubject = Depends(require_api_key),
    ) -> DocumentRecordResponse:
        document_repository = _get_document_repository(request)
        record = document_repository.update_review_status(
            document_id=document_id,
            decision=payload.decision.value,
            reviewer_notes=payload.reviewer_notes,
            reviewed_by=subject.subject_id,
        )
        return DocumentRecordResponse(**record)

    return app


def _validate_upload(file: UploadFile, file_bytes: bytes, max_file_size_bytes: int) -> None:
    filename = file.filename or ""

    if not filename.lower().endswith(".pdf"):
        raise InvalidUploadError("Only PDF files are allowed.")

    if not file_bytes:
        raise InvalidUploadError("Uploaded file is empty.")

    if len(file_bytes) > max_file_size_bytes:
        limit_megabytes = max_file_size_bytes / (1024 * 1024)
        raise InvalidUploadError(f"File exceeds {limit_megabytes:.0f}MB limit.")

    if not file_bytes.startswith(b"%PDF"):
        raise InvalidUploadError("Uploaded file is not a valid PDF.")


def _get_document_repository(request: Request) -> DocumentRepository:
    return request.app.state.document_repository


def _request_id_from_request(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


app = create_app()
