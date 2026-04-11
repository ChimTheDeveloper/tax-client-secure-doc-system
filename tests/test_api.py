from __future__ import annotations

from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app

TEST_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"


def _upload_payload(filename: str, content: bytes, content_type: str = "application/pdf"):
    return {"file": (filename, BytesIO(content), content_type)}


def test_health_endpoint_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_rejects_non_pdf_extension():
    client = TestClient(app)

    response = client.post(
        "/upload",
        files=_upload_payload("sample.txt", b"hello world", "text/plain"),
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_upload"


def test_upload_rejects_invalid_pdf_signature():
    client = TestClient(app)

    response = client.post(
        "/upload",
        files=_upload_payload("sample.pdf", b"not-a-real-pdf"),
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_upload"


@patch("src.api.main.process_tax_document")
def test_upload_returns_success_payload(mock_process_tax_document):
    mock_process_tax_document.return_value = {
        "status": "success",
        "file_name": "generated.pdf",
        "file_size": len(TEST_PDF_BYTES),
        "document_type": "W2",
        "data": {"wages_box_1": 55000.0},
        "confidence": 0.9,
        "requires_manual_review": False,
        "warnings": [],
        "field_confidence": {
            "employee_ssn": "high",
            "employer_ein": "high",
            "wages_box_1": "high",
            "federal_tax_box_2": "high",
        },
    }

    client = TestClient(app)
    response = client.post("/upload", files=_upload_payload("sample.pdf", TEST_PDF_BYTES))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["requires_manual_review"] is False
    assert body["data"]["wages_box_1"] == 55000.0


@patch("src.api.main.process_tax_document")
def test_upload_returns_manual_review_payload(mock_process_tax_document):
    mock_process_tax_document.return_value = {
        "status": "needs_review",
        "file_name": "generated.pdf",
        "file_size": len(TEST_PDF_BYTES),
        "document_type": "W2",
        "data": {"wages_box_1": None},
        "confidence": 0.38,
        "requires_manual_review": True,
        "warnings": ["Confidence score is below threshold."],
        "field_confidence": {
            "employee_ssn": "medium",
            "employer_ein": "low",
            "wages_box_1": "low",
            "federal_tax_box_2": "medium",
        },
    }

    client = TestClient(app)
    response = client.post("/upload", files=_upload_payload("sample.pdf", TEST_PDF_BYTES))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "needs_review"
    assert body["requires_manual_review"] is True
    assert body["confidence"] == 0.38


@patch("src.api.main.generate_upload_url")
def test_presigned_upload_url_endpoint_returns_generated_filename(mock_generate_upload_url):
    mock_generate_upload_url.return_value = ("https://example.com/upload", "generated.pdf")

    client = TestClient(app)
    response = client.get("/generate-upload-url", params={"filename": "sample.pdf"})

    assert response.status_code == 200
    assert response.json() == {
        "upload_url": "https://example.com/upload",
        "filename": "generated.pdf",
    }
