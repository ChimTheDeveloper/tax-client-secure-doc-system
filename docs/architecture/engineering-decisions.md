# Engineering Decisions

This document explains the major engineering decisions in the current version of the tax document system. It is written to support code reviews, deployment planning, and interview conversations.

## 1. Why Introduce Explicit Configuration

The original implementation hard-coded operational values such as the S3 bucket name, AWS region, file-size limit, and confidence threshold directly inside the API module.

That worked for a first prototype, but it created three problems:

1. The code was tightly coupled to one environment.
2. Interviewers or teammates could not easily tell which values were product choices versus environment choices.
3. Deployment changes required code edits instead of configuration changes.

The new `src/core/config.py` module moves those values into a small settings object backed by environment variables. This keeps the runtime behavior explicit while making the app easier to deploy to multiple environments such as local, staging, and production.

## 2. Why Split the API Layer from the Processing Pipeline

The first version of `src/api/main.py` performed every responsibility in one route handler:

- file validation
- Textract calls
- document classification
- field mapping
- validation
- confidence scoring
- normalization
- local persistence
- S3 upload
- audit logging

That structure is common in early-stage projects because it helps get something working quickly. The downside is that the route becomes hard to reason about, hard to test, and hard to explain under pressure.

The new `src/processing/pipeline.py` module centralizes the business workflow. The FastAPI route now acts as a transport boundary:

- it accepts the request
- validates the raw upload
- delegates to the pipeline
- returns a typed response

This separation makes the code easier to test and easier to narrate in an interview:

"The API boundary is responsible for HTTP concerns, and the pipeline is responsible for document-processing concerns."

## 3. Why Add Typed Response Models

FastAPI works best when the API contract is explicit. The new `src/api/schemas.py` file formalizes the shape of the responses for:

- `/health`
- `/generate-upload-url`
- `/upload`

This improves the project in four ways:

1. The response shape is visible in code and in generated OpenAPI docs.
2. Teammates can reason about the API without reading route internals.
3. Tests can assert a stable contract.
4. It signals production maturity to employers because it shows that the service is designed as a predictable interface, not just a script behind an endpoint.

## 4. Why Change Low Confidence From Hard Failure to Manual Review

In the earlier version, low-confidence extraction caused a `422` rejection. That is simple, but it creates a product problem: the system throws away a partially useful result instead of routing it to a human reviewer.

For tax-document processing, "uncertain" and "invalid" are not the same thing.

- Invalid upload: should fail fast.
- Unsupported document type: should be rejected.
- Low-confidence extraction: should remain usable, but flagged for review.

The new design returns a `needs_review` status when the confidence score falls below the configured threshold. That is a better production pattern because it preserves workflow continuity and reflects how document operations teams actually work.

## 5. Why Keep Confidence Scoring Simple and Rule-Based

The current confidence score is intentionally transparent.

The score is based on weighted confidence for a small set of critical W-2 fields:

- employee SSN
- employer EIN
- wages box 1
- federal tax box 2

Each field is graded as `high`, `medium`, or `low`, and then converted into a weighted numeric score.

This is not a machine-learning confidence model. That is deliberate.

For a showcase project, a transparent scoring system has two advantages:

1. You can explain exactly how it works.
2. You can test it deterministically.

In interviews, "simple, explicit, and measurable" is often stronger than "clever but opaque."

## 6. Why Make Local Persistence Optional

The README described zero-disk processing, but the older implementation always wrote extracted results and audit data locally. That mismatch weakened the security story.

The updated design keeps local persistence available for development, but disables it by default through configuration flags:

- `TAX_APP_ENABLE_LOCAL_AUDIT_LOG`
- `TAX_APP_ENABLE_LOCAL_RESULT_STORAGE`

This is a practical compromise:

- local files are useful during development and demos
- production should minimize unnecessary local storage of sensitive tax data

This also gives you a strong explanation in interviews:

"I preserved development ergonomics, but moved sensitive local persistence behind explicit operational controls."

## 7. Why Tighten Error Handling

The original upload route raised `HTTPException` objects for expected validation problems, but then wrapped everything in a broad `except Exception`, which converted those errors into `500` responses.

That made the outward behavior inaccurate.

The new `src/processing/exceptions.py` module introduces application-specific exceptions such as:

- `InvalidUploadError`
- `UnsupportedDocumentError`
- `ExternalServiceError`
- `StorageError`

FastAPI exception handlers now translate those into consistent error responses with both:

- an HTTP status code
- a machine-readable `error_code`

This is important in production because clients should be able to distinguish:

- bad input
- unsupported input
- upstream failures
- internal failures

## 8. Why Add a Health Endpoint

Production systems need a simple readiness/liveness signal. The `/health` endpoint supports:

- uptime checks
- container probes
- load balancer health checks
- deployment smoke tests

It is a small feature, but it signals that the project is moving from prototype thinking to service-operability thinking.

## 9. Why Add Tests This Early

The project previously had no automated test suite. That makes it difficult to refactor safely and difficult to claim production readiness with confidence.

The new test suite focuses first on API contract stability:

- health endpoint behavior
- invalid upload rejection
- malformed PDF rejection
- successful upload response shape
- manual-review response shape
- presigned-upload URL response shape

The tests currently mock the processing pipeline for route-level validation. That is a deliberate first step:

- route tests verify API behavior cleanly
- pipeline tests can be added next with frozen Textract fixtures

This sequencing is useful because it locks down the outer contract first, which gives the rest of the refactor a safe shell.

## 10. Why Add API Authentication Before User Accounts

The new review and document-list endpoints expose sensitive tax-processing data, so leaving them open would weaken the entire system.

Instead of jumping straight to a full user-account system, the current version adds authenticated API access using environment-managed API keys.

That decision was intentional:

1. It creates an immediate security boundary around sensitive routes.
2. It works well for internal tools and service-to-service access.
3. It keeps the auth layer understandable while the rest of the product matures.

This is not the final auth model. It is the first production-minded control layer. JWT-based auth and role-aware user management can build on top of it later.

## 11. Why Add Durable Document Persistence

Before this change, the API behaved like a one-shot processing endpoint: upload a file, get a response, and lose the operational context unless you captured it somewhere else.

That is fine for a prototype, but not for a review workflow.

The new document repository stores:

- upload metadata
- normalized extraction output
- confidence and warning details
- review status
- reviewer notes
- created and updated timestamps

This turns the system into an actual workflow backend instead of a transient processing demo.

SQLite is used as the first persistence layer because it is built into Python, easy to test, and simple to explain. The long-term path can still evolve toward PostgreSQL or DynamoDB depending on the deployment model.

## 12. What Still Needs to Happen

This refactor makes the project stronger, but it does not make the app magically complete.

The biggest remaining production steps are:

- add authenticated users and authorization boundaries
- persist reviewable extraction state in a proper database
- expand CI into deployment automation
- add infrastructure-as-code
- add fixture-driven tests around real Textract response samples
- expand beyond W-2 support
- define retention and encryption strategy for stored sensitive data

That is the right posture for interviews too: strong engineering work paired with honest scope management.
