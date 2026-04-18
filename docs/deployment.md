# Deployment Guide

This project now supports two reliable operating modes:

1. Local Python execution for development and debugging
2. Docker Compose execution for demo and deployment-style testing

## Local Python Run

1. Create the virtual environment:
   `make setup`
2. Copy the example environment file:
   `cp .env.example .env`
3. Adjust values in `.env`
4. Start the API:
   `make dev`

For the browser workspace, open:

`http://localhost:8000/login`

For a first local admin account, set:

- `TAX_APP_BOOTSTRAP_ADMIN_EMAIL`
- `TAX_APP_BOOTSTRAP_ADMIN_PASSWORD`
- `TAX_APP_BOOTSTRAP_ADMIN_NAME`

For local testing without auth:

`TAX_APP_ENABLE_AUTH=false PYTHONPATH=. venv/bin/uvicorn src.api.main:app --reload`

## Docker Run

1. Copy the example environment file:
   `cp .env.example .env`
2. Update `.env` with your AWS and runtime values
3. Start the stack:
   `make docker-up`

The container exposes the API on `http://localhost:8000` and persists SQLite data in the local `data/` directory.
It also serves the login and review dashboard UI from the same container.

## Runtime Signals

- `GET /health` confirms the app is running and returns version and environment metadata
- `GET /ready` confirms SQLite connectivity and basic runtime configuration
- Each response includes `X-Request-ID` for tracing

## Production Checklist

- Set `TAX_APP_ENABLE_AUTH=true`
- Replace `TAX_APP_API_KEYS` with strong secrets managed outside source control
- Replace bootstrap admin credentials with real secrets and rotate them after first setup
- Use a production S3 bucket and IAM role with least privilege
- Move SQLite to a managed database if you need multi-instance deployment
- Disable local result storage and local audit logging unless explicitly required
- Route application logs to your platform log sink
- Protect the API behind HTTPS and a reverse proxy or load balancer
- Monitor `/health` and `/ready` in your deployment platform

## Deployment Direction

This repository is ready for:

- local demo runs
- Docker-based showcase deployments
- single-instance early production environments

For full multi-user production, the next infrastructure step should be replacing SQLite with a managed database and adding infrastructure-as-code for repeatable cloud provisioning.
