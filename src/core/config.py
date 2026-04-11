from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _get_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    aws_region: str
    s3_bucket_name: str
    max_file_size_bytes: int
    presigned_url_ttl_seconds: int
    min_confidence_score: float
    enable_local_audit_log: bool
    enable_local_result_storage: bool
    local_result_path: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        aws_region=os.getenv("TAX_APP_AWS_REGION", "us-east-1"),
        s3_bucket_name=os.getenv("TAX_APP_S3_BUCKET", "tax-doc-system-chim-dev"),
        max_file_size_bytes=int(os.getenv("TAX_APP_MAX_FILE_SIZE_BYTES", str(5 * 1024 * 1024))),
        presigned_url_ttl_seconds=int(os.getenv("TAX_APP_PRESIGNED_URL_TTL_SECONDS", "300")),
        min_confidence_score=float(os.getenv("TAX_APP_MIN_CONFIDENCE_SCORE", "0.6")),
        enable_local_audit_log=_get_bool_env("TAX_APP_ENABLE_LOCAL_AUDIT_LOG", False),
        enable_local_result_storage=_get_bool_env("TAX_APP_ENABLE_LOCAL_RESULT_STORAGE", False),
        local_result_path=os.getenv("TAX_APP_LOCAL_RESULT_PATH", "processed_results.json"),
    )

