from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def app(monkeypatch, tmp_path) -> FastAPI:
    monkeypatch.setenv("TAX_APP_API_KEYS", "test-api-key")
    monkeypatch.setenv("TAX_APP_DATABASE_PATH", str(tmp_path / "tax_app.db"))
    monkeypatch.setenv("TAX_APP_ENABLE_LOCAL_AUDIT_LOG", "false")
    monkeypatch.setenv("TAX_APP_ENABLE_LOCAL_RESULT_STORAGE", "false")
    monkeypatch.setenv("TAX_APP_BOOTSTRAP_ADMIN_EMAIL", "admin@example.com")
    monkeypatch.setenv("TAX_APP_BOOTSTRAP_ADMIN_PASSWORD", "supersecurepass")
    monkeypatch.setenv("TAX_APP_BOOTSTRAP_ADMIN_NAME", "Admin User")

    from src.core.config import get_settings

    get_settings.cache_clear()

    from src.api.main import create_app

    return create_app()


@pytest.fixture
def client(app: FastAPI):
    with TestClient(app) as test_client:
        yield test_client

    from src.core.config import get_settings
    get_settings.cache_clear()
