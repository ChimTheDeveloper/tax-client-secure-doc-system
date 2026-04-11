from __future__ import annotations

import os
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.processing.exceptions import InvalidUploadError, StorageError


def get_s3_client(region_name: str = "us-east-1"):
    return boto3.client("s3", region_name=region_name)


def sanitize_filename(filename: str) -> str:
    cleaned = os.path.basename((filename or "").strip())
    if not cleaned:
        raise InvalidUploadError("A filename is required.")

    return cleaned


def build_storage_filename(filename: str) -> str:
    return f"{uuid.uuid4()}_{sanitize_filename(filename)}"


def generate_upload_url(
    filename: str,
    bucket_name: str,
    region_name: str,
    expires_in: int = 300,
    s3_client=None,
) -> tuple[str, str]:
    sanitized_filename = sanitize_filename(filename)
    if not sanitized_filename.lower().endswith(".pdf"):
        raise InvalidUploadError("Only PDF files are allowed.")

    object_key = build_storage_filename(sanitized_filename)
    client = s3_client or get_s3_client(region_name)

    try:
        url = client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_key,
                "ContentType": "application/pdf",
            },
            ExpiresIn=expires_in,
        )
    except (ClientError, BotoCoreError) as exc:
        raise StorageError("Failed to generate a presigned upload URL.") from exc

    return url, object_key


def upload_file(
    file_bytes: bytes,
    bucket_name: str,
    filename: str,
    *,
    region_name: str = "us-east-1",
    s3_client=None,
) -> None:
    client = s3_client or get_s3_client(region_name)

    try:
        client.put_object(
            Bucket=bucket_name,
            Key=filename,
            Body=file_bytes,
            ContentType="application/pdf",
        )
    except (ClientError, BotoCoreError) as exc:
        raise StorageError("Failed to upload document to S3.") from exc
