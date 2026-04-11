from __future__ import annotations

from unittest.mock import patch

import pytest

from src.core.config import Settings
from src.processing.exceptions import UnsupportedDocumentError
from src.processing.pipeline import process_tax_document


TEST_SETTINGS = Settings(
    aws_region="us-east-1",
    s3_bucket_name="test-bucket",
    max_file_size_bytes=5 * 1024 * 1024,
    presigned_url_ttl_seconds=300,
    min_confidence_score=0.6,
    enable_local_audit_log=False,
    enable_local_result_storage=False,
    local_result_path="processed_results.json",
)


@patch("src.processing.pipeline.analyze_document_bytes")
@patch("src.processing.pipeline.classify_document")
def test_pipeline_rejects_unsupported_documents(mock_classify_document, mock_analyze_document_bytes):
    mock_analyze_document_bytes.return_value = {"Blocks": [{"BlockType": "LINE", "Text": "not a w2"}]}
    mock_classify_document.return_value = "UNKNOWN"

    with pytest.raises(UnsupportedDocumentError):
        process_tax_document(b"%PDF-sample", "sample.pdf", TEST_SETTINGS)


@patch("src.processing.pipeline.upload_file")
@patch("src.processing.pipeline.build_storage_filename")
@patch("src.processing.pipeline.calculate_confidence")
@patch("src.processing.pipeline.normalize_w2_data")
@patch("src.processing.pipeline.validate_w2_data")
@patch("src.processing.pipeline.map_textract_to_tax_fields")
@patch("src.processing.pipeline.process_document")
@patch("src.processing.pipeline.classify_document")
@patch("src.processing.pipeline.analyze_document_bytes")
def test_pipeline_returns_success_result(
    mock_analyze_document_bytes,
    mock_classify_document,
    mock_process_document,
    mock_map_textract_to_tax_fields,
    mock_validate_w2_data,
    mock_normalize_w2_data,
    mock_calculate_confidence,
    mock_build_storage_filename,
    mock_upload_file,
):
    mock_analyze_document_bytes.return_value = {"Blocks": [{"BlockType": "LINE", "Text": "w-2"}]}
    mock_classify_document.return_value = "W2"
    mock_process_document.return_value = {"document_type": "W2", "extracted_fields": {}}
    mock_map_textract_to_tax_fields.return_value = {"wages_box_1": "$55,000.00"}
    mock_validate_w2_data.return_value = (
        {
            "employee_ssn": "123-45-6789",
            "employer_ein": "12-3456789",
            "wages_box_1": "$55,000.00",
            "federal_tax_box_2": "$5,000.00",
        },
        {
            "employee_ssn": "high",
            "employer_ein": "high",
            "wages_box_1": "high",
            "federal_tax_box_2": "high",
        },
        [],
    )
    mock_normalize_w2_data.return_value = {
        "employee_ssn": "123-45-6789",
        "employer_ein": "12-3456789",
        "wages_box_1": 55000.0,
        "federal_tax_box_2": 5000.0,
    }
    mock_calculate_confidence.return_value = 0.96
    mock_build_storage_filename.return_value = "stored.pdf"

    result = process_tax_document(b"%PDF-sample", "sample.pdf", TEST_SETTINGS)

    assert result["status"] == "success"
    assert result["requires_manual_review"] is False
    assert result["file_name"] == "stored.pdf"
    assert result["confidence"] == 0.96
    mock_upload_file.assert_called_once()


@patch("src.processing.pipeline.upload_file")
@patch("src.processing.pipeline.build_storage_filename")
@patch("src.processing.pipeline.calculate_confidence")
@patch("src.processing.pipeline.normalize_w2_data")
@patch("src.processing.pipeline.validate_w2_data")
@patch("src.processing.pipeline.map_textract_to_tax_fields")
@patch("src.processing.pipeline.process_document")
@patch("src.processing.pipeline.classify_document")
@patch("src.processing.pipeline.analyze_document_bytes")
def test_pipeline_routes_low_confidence_documents_to_manual_review(
    mock_analyze_document_bytes,
    mock_classify_document,
    mock_process_document,
    mock_map_textract_to_tax_fields,
    mock_validate_w2_data,
    mock_normalize_w2_data,
    mock_calculate_confidence,
    mock_build_storage_filename,
    mock_upload_file,
):
    mock_analyze_document_bytes.return_value = {"Blocks": [{"BlockType": "LINE", "Text": "w-2"}]}
    mock_classify_document.return_value = "W2"
    mock_process_document.return_value = {"document_type": "W2", "extracted_fields": {}}
    mock_map_textract_to_tax_fields.return_value = {"wages_box_1": None}
    mock_validate_w2_data.return_value = (
        {
            "employee_ssn": None,
            "employer_ein": None,
            "wages_box_1": None,
            "federal_tax_box_2": None,
        },
        {
            "employee_ssn": "low",
            "employer_ein": "low",
            "wages_box_1": "low",
            "federal_tax_box_2": "low",
        },
        ["Box 1 wages are missing or malformed."],
    )
    mock_normalize_w2_data.return_value = {
        "employee_ssn": None,
        "employer_ein": None,
        "wages_box_1": None,
        "federal_tax_box_2": None,
    }
    mock_calculate_confidence.return_value = 0.15
    mock_build_storage_filename.return_value = "stored.pdf"

    result = process_tax_document(b"%PDF-sample", "sample.pdf", TEST_SETTINGS)

    assert result["status"] == "needs_review"
    assert result["requires_manual_review"] is True
    assert any("manual review" in warning.lower() for warning in result["warnings"])
    mock_upload_file.assert_called_once()
