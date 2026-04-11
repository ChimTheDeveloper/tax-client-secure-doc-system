from __future__ import annotations

import os
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(BASE_DIR, "audit_log.txt")


def log_upload(
    filename: str,
    bucket_name: str,
    file_size: int | None = None,
    processing_status: str | None = None,
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    display_size = f"{file_size:,}" if file_size is not None else "Unknown"

    log_entry = (
        f"Timestamp: {timestamp}\n"
        f"File:      {filename}\n"
        f"Size:      {display_size} bytes\n"
        f"Bucket:    {bucket_name}\n"
        f"Status:    {processing_status or 'Unknown'}\n"
        f"{'-' * 40}\n"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as log_handle:
        log_handle.write(log_entry)
