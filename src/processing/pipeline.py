from __future__ import annotations

import logging
from typing import Any

from src.api.schemas import ProcessingStatus
from src.audit.logger import log_upload
from src.core.config import Settings, get_settings
from src.processing.classifier import classify_document
from src.processing.confidence import calculate_confidence
from src.processing.exceptions import UnsupportedDocumentError
from src.processing.field_mapper import map_textract_to_tax_fields
from src.processing.normalizer import normalize_w2_data
from src.processing.parser import process_document
from src.processing.storage import save_result
from src.processing.textract_service import analyze_document_bytes
from src.processing.validator import validate_w2_data
from src.upload.upload import build_storage_filename, upload_file

logger = logging.getLogger(__name__)


def process_tax_document(
    file_bytes: bytes,
    original_filename: str,
    settings: Settings | None = None,
) -> dict[str, Any]:
    active_settings = settings or get_settings()

    raw_text_data = analyze_document_bytes(
        file_bytes,
        region_name=active_settings.aws_region,
    )
    document_type = classify_document(raw_text_data)

    if document_type != "W2":
        raise UnsupportedDocumentError(
            "Uploaded document is not a supported W-2. Processing aborted."
        )

    parser_result = process_document(file_bytes, raw_text_data)
    mapped_data = map_textract_to_tax_fields(raw_text_data)
    validated_data, field_confidence, warnings = validate_w2_data(mapped_data)
    normalized_data = normalize_w2_data(validated_data)
    confidence_score = calculate_confidence(normalized_data, field_confidence)

    requires_manual_review = confidence_score < active_settings.min_confidence_score
    status = (
        ProcessingStatus.NEEDS_REVIEW.value
        if requires_manual_review
        else ProcessingStatus.SUCCESS.value
    )

    if requires_manual_review:
        warnings = [
            *warnings,
            "Confidence score is below the review threshold; route this document to manual review.",
        ]

    storage_filename = build_storage_filename(original_filename)
    file_size = len(file_bytes)

    upload_file(
        file_bytes,
        active_settings.s3_bucket_name,
        storage_filename,
        region_name=active_settings.aws_region,
    )

    processing_record = {
        "status": status,
        "document_type": document_type,
        "confidence": confidence_score,
        "requires_manual_review": requires_manual_review,
        "warnings": warnings,
        "field_confidence": field_confidence,
        "parser_result": parser_result,
        "mapped_data": mapped_data,
        "normalized_data": normalized_data,
        "file_name": storage_filename,
        "size": file_size,
    }

    if active_settings.enable_local_result_storage:
        save_result(processing_record, active_settings.local_result_path)

    if active_settings.enable_local_audit_log:
        log_upload(
            storage_filename,
            active_settings.s3_bucket_name,
            file_size=file_size,
            processing_status=status,
        )

    logger.info(
        "Processed tax document",
        extra={
            "document_type": document_type,
            "status": status,
            "confidence": confidence_score,
            "file_name": storage_filename,
        },
    )

    return {
        "status": status,
        "file_name": storage_filename,
        "file_size": file_size,
        "document_type": document_type,
        "data": normalized_data,
        "confidence": confidence_score,
        "requires_manual_review": requires_manual_review,
        "warnings": warnings,
        "field_confidence": field_confidence,
    }
