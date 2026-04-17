from __future__ import annotations

from io import BytesIO
from unittest.mock import patch

TEST_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
AUTH_HEADERS = {"X-API-Key": "test-api-key"}


def _upload_payload(filename: str, content: bytes, content_type: str = "application/pdf"):
    return {"file": (filename, BytesIO(content), content_type)}


def test_health_endpoint_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


def test_upload_requires_authentication(client):
    response = client.post("/upload", files=_upload_payload("sample.pdf", TEST_PDF_BYTES))

    assert response.status_code == 401
    assert response.json()["error_code"] == "authentication_error"
    assert response.headers["X-Request-ID"]


def test_upload_rejects_non_pdf_extension(client):
    response = client.post(
        "/upload",
        files=_upload_payload("sample.txt", b"hello world", "text/plain"),
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_upload"


def test_upload_rejects_invalid_pdf_signature(client):
    response = client.post(
        "/upload",
        files=_upload_payload("sample.pdf", b"not-a-real-pdf"),
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_upload"


@patch("src.api.main.process_tax_document")
def test_upload_returns_success_payload(mock_process_tax_document, client):
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

    response = client.post(
        "/upload",
        files=_upload_payload("sample.pdf", TEST_PDF_BYTES),
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["requires_manual_review"] is False
    assert body["data"]["wages_box_1"] == 55000.0
    assert body["document_id"]
    assert body["review_status"] == "not_required"
    assert body["submitted_by"].startswith("api-key:")
    assert response.headers["X-Request-ID"]


@patch("src.api.main.process_tax_document")
def test_upload_returns_manual_review_payload(mock_process_tax_document, client):
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

    response = client.post(
        "/upload",
        files=_upload_payload("sample.pdf", TEST_PDF_BYTES),
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "needs_review"
    assert body["requires_manual_review"] is True
    assert body["confidence"] == 0.38
    assert body["review_status"] == "pending"


@patch("src.api.main.generate_upload_url")
def test_presigned_upload_url_endpoint_returns_generated_filename(mock_generate_upload_url, client):
    mock_generate_upload_url.return_value = ("https://example.com/upload", "generated.pdf")

    response = client.get(
        "/generate-upload-url",
        params={"filename": "sample.pdf"},
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {
        "upload_url": "https://example.com/upload",
        "filename": "generated.pdf",
    }


@patch("src.api.main.process_tax_document")
def test_document_can_be_listed_and_reviewed(mock_process_tax_document, client):
    mock_process_tax_document.return_value = {
        "status": "needs_review",
        "file_name": "generated.pdf",
        "file_size": len(TEST_PDF_BYTES),
        "document_type": "W2",
        "data": {"wages_box_1": None},
        "confidence": 0.25,
        "requires_manual_review": True,
        "warnings": ["Needs review"],
        "field_confidence": {
            "employee_ssn": "low",
            "employer_ein": "low",
            "wages_box_1": "low",
            "federal_tax_box_2": "low",
        },
    }

    upload_response = client.post(
        "/upload",
        files=_upload_payload("sample.pdf", TEST_PDF_BYTES),
        headers=AUTH_HEADERS,
    )
    assert upload_response.status_code == 200
    document_id = upload_response.json()["document_id"]

    list_response = client.get("/documents", headers=AUTH_HEADERS)
    assert list_response.status_code == 200
    assert len(list_response.json()["documents"]) == 1

    filtered_response = client.get(
        "/documents",
        params={"review_status": "pending", "search": "sample"},
        headers=AUTH_HEADERS,
    )
    assert filtered_response.status_code == 200
    assert len(filtered_response.json()["documents"]) == 1

    summary_response = client.get("/documents/summary", headers=AUTH_HEADERS)
    assert summary_response.status_code == 200
    assert summary_response.json()["pending_review"] == 1
    assert summary_response.json()["needs_review"] == 1

    detail_response = client.get(f"/documents/{document_id}", headers=AUTH_HEADERS)
    assert detail_response.status_code == 200
    assert detail_response.json()["review_status"] == "pending"

    review_response = client.patch(
        f"/documents/{document_id}/review",
        json={"decision": "approved", "reviewer_notes": "Validated manually."},
        headers=AUTH_HEADERS,
    )
    assert review_response.status_code == 200
    assert review_response.json()["review_status"] == "approved"
    assert review_response.json()["reviewer_notes"] == "Validated manually."


@patch("src.api.main.process_tax_document")
def test_non_reviewable_document_cannot_be_reviewed(mock_process_tax_document, client):
    mock_process_tax_document.return_value = {
        "status": "success",
        "file_name": "generated.pdf",
        "file_size": len(TEST_PDF_BYTES),
        "document_type": "W2",
        "data": {"wages_box_1": 100.0},
        "confidence": 0.92,
        "requires_manual_review": False,
        "warnings": [],
        "field_confidence": {
            "employee_ssn": "high",
            "employer_ein": "high",
            "wages_box_1": "high",
            "federal_tax_box_2": "high",
        },
    }

    upload_response = client.post(
        "/upload",
        files=_upload_payload("clean.pdf", TEST_PDF_BYTES),
        headers=AUTH_HEADERS,
    )
    document_id = upload_response.json()["document_id"]

    review_response = client.patch(
        f"/documents/{document_id}/review",
        json={"decision": "approved", "reviewer_notes": "Not needed."},
        headers=AUTH_HEADERS,
    )

    assert review_response.status_code == 409
    assert review_response.json()["error_code"] == "conflict"


def test_readiness_reports_auth_state(client):
    response = client.get("/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    dependency_names = {dependency["name"] for dependency in body["dependencies"]}
    assert {"sqlite", "auth", "s3", "textract_region"} <= dependency_names
