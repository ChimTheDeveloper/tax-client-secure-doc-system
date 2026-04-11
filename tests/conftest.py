from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("TAX_APP_API_KEYS", "test-api-key")
    monkeypatch.setenv("TAX_APP_DATABASE_PATH", str(tmp_path / "tax_app.db"))
    monkeypatch.setenv("TAX_APP_ENABLE_LOCAL_AUDIT_LOG", "false")
    monkeypatch.setenv("TAX_APP_ENABLE_LOCAL_RESULT_STORAGE", "false")

    from src.core.config import get_settings

    get_settings.cache_clear()

    from src.api.main import create_app

    test_app = create_app()

    with TestClient(test_app) as test_client:
        yield test_client

    get_settings.cache_clear()
