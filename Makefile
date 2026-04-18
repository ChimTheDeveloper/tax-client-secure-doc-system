PYTHON ?= python3
VENV ?= venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
UVICORN := $(VENV)/bin/uvicorn

.PHONY: setup dev test run docker-build docker-up docker-down

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt

dev:
	PYTHONPATH=. $(UVICORN) src.api.main:app --reload

run:
	PYTHONPATH=. $(UVICORN) src.api.main:app --host 0.0.0.0 --port 8000

test:
	PYTHONPATH=. $(PYTEST) -q

docker-build:
	docker compose build

docker-up:
	docker compose up --build

docker-down:
	docker compose down
