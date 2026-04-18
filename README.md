## Secure Tax Document Intelligence System
An AI-powered, memory-resident processing engine for sensitive tax documents.

This system is designed to allow tax professionals to upload, store, and process sensitive client documents securely while maintaining auditability, validation, and scalability.

---

## 🚀 Getting Started

# Prerequisites
- Python 3.11+
- AWS CLI configured with `us-east-1`
- Active S3 Bucket: `tax-doc-system-chim-dev`
- AWS IAM credentials with access to:
  - S3 (PutObject)
  - Textract (AnalyzeDocument)

Recommended environment variables:
- `TAX_APP_ENVIRONMENT`
- `TAX_APP_VERSION`
- `TAX_APP_S3_BUCKET`
- `TAX_APP_AWS_REGION`
- `TAX_APP_MIN_CONFIDENCE_SCORE`
- `TAX_APP_ENABLE_AUTH`
- `TAX_APP_API_KEYS`
- `TAX_APP_SESSION_COOKIE_NAME`
- `TAX_APP_SESSION_DURATION_HOURS`
- `TAX_APP_INVITE_DURATION_HOURS`
- `TAX_APP_BOOTSTRAP_ADMIN_EMAIL`
- `TAX_APP_BOOTSTRAP_ADMIN_PASSWORD`
- `TAX_APP_BOOTSTRAP_ADMIN_NAME`
- `TAX_APP_DATABASE_PATH`
- `TAX_APP_LOG_LEVEL`
- `TAX_APP_ENABLE_LOCAL_AUDIT_LOG`
- `TAX_APP_ENABLE_LOCAL_RESULT_STORAGE`

---

# Installation
1. Clone the repository  
2. Create a virtual environment: `python3 -m venv venv`  
3. Activate: `source venv/bin/activate`  
4. Install dependencies: `pip install -r requirements.txt`  

For local test tooling:
5. Install dev dependencies: `pip install -r requirements-dev.txt`

---

# Running the Application

Because the application uses a modular structure, always run the server from the **root directory**:

# Set the Python Path so internal modules are discoverable
export PYTHONPATH=$PYTHONPATH:.

# Start the FastAPI server
uvicorn src.api.main:app --reload

# Run the automated tests
pytest -q

# One-time setup shortcut
make setup

# Start locally with the virtual environment
make dev

# Optional: run with Docker
make docker-up

# Example authenticated request
curl -H "X-API-Key: your-api-key" http://localhost:8000/documents

# Browser UI
open http://localhost:8000/login

# Example local-dev mode with auth disabled
TAX_APP_ENABLE_AUTH=false uvicorn src.api.main:app --reload

---

## Current Features

- Zero-Disk Processing: Documents are handled as in-memory byte streams to ensure no sensitive data is written to local storage.
- AI-Powered Extraction: Integrated with Amazon Textract for OCR and structured form extraction.
- Document Classification: Automatically identifies document types (W-2 supported).
- Typed FastAPI Contracts: Upload and health endpoints return validated response models.
- Environment-Driven Configuration: Bucket, region, confidence thresholds, and local persistence are configurable without code edits.
- Built-In Auth System: Invite-only local accounts support email/password login today, while preserving a clean path to future Google sign-in.
- Authenticated API Access: Protected endpoints accept API keys for service usage and session cookies for the browser UI.
- Role-Based Authorization: `admin`, `reviewer`, and `uploader` roles shape who can invite users, review documents, and access records.
- Multi-Pass Extraction Engine:
  - KEY_VALUE extraction (primary)
  - LINE-based fallback
  - Regex-based precision extraction
- Structured W-2 Mapping: Extracts SSN, EIN, wages, and tax fields.
- Validation Layer: Separates invalid inputs from low-confidence-but-reviewable documents.
- Normalization Layer: Converts extracted values into clean, usable formats.
- Manual Review Routing: Low-confidence extractions are returned as `needs_review` instead of being silently discarded.
- Durable Review Queue: Processed documents are stored in SQLite with review state, notes, and timestamps.
- Invite Workflow: Admins can issue invites, recipients can activate accounts, and sessions are stored server-side.
- Browser Review Workspace: A lightweight dashboard supports login, upload, invite management, and manual review.
- Health Check Endpoint: `/health` supports uptime checks and deployment probes.
- Health Metadata: `/health` returns environment and version details for release verification.
- Readiness Endpoint: `/ready` reports dependency and configuration state for deploy checks.
- Request Tracing: Each response includes `X-Request-ID`, and request logs capture timing and route information.
- Review Dashboard Data: `/documents/summary` exposes counts for pending, approved, rejected, and auto-processed documents.
- Docker Compose Workflow: `compose.yaml` provides a one-command container run path with a healthcheck and persisted local data.
- Makefile Shortcuts: `make setup`, `make dev`, `make test`, and `make docker-up` standardize common developer workflows.
- Audit Logging (Optional Local): Local audit logging is available for development but disabled by default.
- Modular Backend Structure: Clear separation between ingestion, processing, and storage.

---

## Security

This system uses IAM policies and application-layer role controls to enforce least-privilege access.

- Restricted permissions to only allow file uploads and Textract analysis  
- Scoped access to a specific S3 bucket  
- In-Memory Lifecycle: Files are processed in RAM and uploaded to S3 without hitting the server file system by default  
- Dev-only Local Persistence: Audit and extracted-result files are now opt-in so production can avoid unnecessary local PII storage
- Session cookies are `HttpOnly` and role-aware access prevents uploaders from reading other users' documents

---

## API File Validation
 
This system enforces strict validation rules:

- Only PDF files are accepted  
- Maximum file size limit: 5MB  
- Empty or invalid files are rejected before processing  

---

## System Flow

User --> FastAPI Ingestion --> AWS Textract --> Processing Pipeline --> AWS S3 --> Audit Logging

1. User provides a file via POST request  
2. API authenticates the caller before allowing protected operations  
3. System converts file to memory-resident byte stream  
4. API validates file extension, file size, and PDF signature before AWS calls  
5. Bytes are sent directly to Amazon Textract for OCR and form analysis  
6. Document is classified (W-2 detection)  
7. Multi-pass extraction is applied (KEY_VALUE → LINE → REGEX)  
8. Extracted data is validated  
9. Weighted confidence scoring determines `success` vs `needs_review`  
10. Data is normalized into structured format  
11. File is uploaded to AWS S3 via boto3  
12. A durable document record is written to SQLite with review status and audit metadata  
13. Optional local metadata is written only when explicitly enabled  

---

## Document Processing

Uploaded documents are processed using a hybrid AI and rule-based system.

Pipeline:
- Extract text and form data via Amazon Textract  
- Classify document type (W-2 currently supported)  
- Extract key fields (SSN, EIN, wages, tax fields)  
- Apply multi-pass extraction for reliability  
- Validate extracted data  
- Normalize values into usable formats  

Results are stored in structured JSON format for downstream tax workflows.

---

## Audit Logging

The system can maintain a local audit log for traceability during development.

Each upload records:
- Timestamp (UTC)  
- File name  
- File size (calculated from byte stream)  
- Processing status  

Note: Local audit logging is disabled by default and can be enabled with `TAX_APP_ENABLE_LOCAL_AUDIT_LOG=true`.

---

## Storage Layer

This system uses Amazon S3 for secure, durable document storage.

Implementation:
- File uploads handled via Python (boto3)  
- Objects stored directly from memory to S3 bucket  
- No local disk persistence by default  
- IAM-restricted access  
- SQLite-backed document metadata persists reviewable state and supports local and early-stage deployment

---

## Delivery Tooling

- Dockerfile included for containerized deployment
- `compose.yaml` provides local deployment-style orchestration
- `Makefile` standardizes setup, test, and run commands
- GitHub Actions CI workflow runs the automated test suite on pushes and pull requests
- `.env.example` documents runtime configuration
- `docs/deployment.md` documents local, Docker, and deployment readiness workflow

---

## Review Workflow

- `GET /documents` lists stored processing records
- `GET /documents?review_status=pending&search=sample` filters the review queue
- `GET /documents/summary` returns dashboard-style review and document counts
- `GET /documents/{document_id}` returns a specific record
- `PATCH /documents/{document_id}/review` records an approve/reject decision with reviewer notes
- Low-confidence uploads start as `review_status = pending`
- Documents that do not require manual review cannot be reviewed later, preventing invalid state transitions

## User And Auth Workflow

- A bootstrap admin can be seeded from environment variables
- Admins create invite links for new users
- Invite recipients activate accounts with an email/password flow
- Sessions are stored in SQLite and attached to browser requests with a secure cookie
- API keys remain available for service-to-service or local testing workflows

---

## Current Limitations

- Address extraction is heuristic-based (not layout-aware yet)  
- DynamoDB persistence is temporarily disabled  
- Only W-2 fully supported  
- Infrastructure-as-code for cloud provisioning is not committed yet  
- Google sign-in is not implemented yet  
- Password reset and self-service account recovery are not implemented yet  

---

## Roadmap

- Implement AWS KMS (Key Management Service) for S3 encryption  
- Add JWT-based authentication for tax professionals  
- Add Google sign-in and richer email/password account recovery  
- Reintroduce DynamoDB with structured schema  
- Expand support for additional tax forms (1099, Schedule C)  
- Introduce cost tracking and FinOps optimization  
- Add deployment automation and infrastructure-as-code for reproducible deployment

See [docs/deployment.md](/home/chimnedum/tax-python-app/docs/deployment.md) for the current deployment workflow.

---

## Positioning

This project demonstrates:

- Cloud-native backend engineering  
- Serverless architecture design  
- AI-assisted document processing  
- Data validation and normalization pipelines  
- Secure handling of sensitive financial data
- Production-minded API design and testing

## Engineering Notes

- Detailed architecture and decision notes live in `docs/architecture/engineering-decisions.md`

## Architecture Diagram

![Architecture](docs/architecture/architecture-v1.png)
