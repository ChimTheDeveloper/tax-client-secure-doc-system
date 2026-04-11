from __future__ import annotations

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.processing.exceptions import ExternalServiceError, InvalidUploadError


def get_textract_client(region_name: str = "us-east-1"):
    return boto3.client("textract", region_name=region_name)


def analyze_document_bytes(
    file_bytes: bytes,
    *,
    region_name: str = "us-east-1",
    textract_client=None,
) -> dict:
    if not file_bytes:
        raise InvalidUploadError("Uploaded file is empty.")

    client = textract_client or get_textract_client(region_name)

    try:
        response = client.analyze_document(
            Document={"Bytes": file_bytes},
            FeatureTypes=["FORMS", "TABLES"],
        )
    except (ClientError, BotoCoreError) as exc:
        raise ExternalServiceError("Textract analysis failed.") from exc

    if not response.get("Blocks"):
        raise ExternalServiceError("Textract returned no document blocks.")

    return response
