from __future__ import annotations

import logging

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import JSONResponse

from src.api.schemas import HealthResponse, UploadDocumentResponse, UploadUrlResponse
from src.core.config import get_settings
from src.processing.exceptions import ApplicationError, InvalidUploadError
from src.processing.pipeline import process_tax_document
from src.upload.upload import generate_upload_url

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Secure Tax Document Intelligence System",
        version="0.2.0",
    )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(_request, exc: ApplicationError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request, exc: Exception):
        logger.exception("Unhandled exception while processing request", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_code": "internal_server_error",
            },
        )

    @app.get("/health", response_model=HealthResponse)
    def health_check() -> HealthResponse:
        return HealthResponse()

    @app.get("/generate-upload-url", response_model=UploadUrlResponse)
    def generate_upload_url_endpoint(filename: str = Query(..., min_length=1)) -> UploadUrlResponse:
        settings = get_settings()
        upload_url, generated_filename = generate_upload_url(
            filename=filename,
            bucket_name=settings.s3_bucket_name,
            region_name=settings.aws_region,
            expires_in=settings.presigned_url_ttl_seconds,
        )
        return UploadUrlResponse(upload_url=upload_url, filename=generated_filename)

    @app.post("/upload", response_model=UploadDocumentResponse)
    async def upload_document(file: UploadFile = File(...)) -> UploadDocumentResponse:
        settings = get_settings()
        file_bytes = await file.read()

        _validate_upload(file, file_bytes, settings.max_file_size_bytes)

        result = process_tax_document(
            file_bytes=file_bytes,
            original_filename=file.filename or "upload.pdf",
            settings=settings,
        )
        return UploadDocumentResponse(**result)

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


app = create_app()
