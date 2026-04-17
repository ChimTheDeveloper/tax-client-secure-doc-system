from __future__ import annotations

import logging
import os


def configure_logging() -> None:
    log_level_name = os.getenv("TAX_APP_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(log_level)
        return

    logging.basicConfig(
        level=log_level,
        format=(
            "%(asctime)s %(levelname)s %(name)s "
            "request_id=%(request_id)s message=%(message)s"
        ),
    )


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def attach_request_context_filter() -> None:
    context_filter = RequestContextFilter()
    for handler in logging.getLogger().handlers:
        handler.addFilter(context_filter)

