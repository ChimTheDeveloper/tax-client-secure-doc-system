from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Query, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.api.schemas import (
    DependencyHealth,
    DocumentListResponse,
    DocumentRecordResponse,
    DocumentSummaryResponse,
    HealthResponse,
    InviteResponse,
    InviteUserRequest,
    ProcessingStatus,
    ReadinessResponse,
    ReviewDecisionRequest,
    ReviewStatus,
    SessionResponse,
    UploadDocumentResponse,
    UploadUrlResponse,
    UserListResponse,
    UserResponse,
)
from src.auth.repository import AuthRepository
from src.auth.security import (
    ROLE_ADMIN,
    ROLE_REVIEWER,
    ROLE_UPLOADER,
    AuthenticatedSubject,
    authenticate_local_user,
    create_invite_token,
    create_password_salt,
    create_session_token,
    hash_password,
    hash_token,
    require_authenticated_subject,
    require_roles,
)
from src.core.config import Settings, get_settings
from src.core.logging import attach_request_context_filter, configure_logging
from src.documents.repository import DocumentRepository
from src.processing.exceptions import (
    ApplicationError,
    AuthorizationError,
    InvalidUploadError,
)
from src.processing.pipeline import process_tax_document
from src.upload.upload import generate_upload_url

configure_logging()
attach_request_context_filter()

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Secure Tax Document Intelligence System",
        version=settings.app_version,
    )
    app.state.settings = settings
    app.state.document_repository = DocumentRepository(settings.database_path)
    app.state.auth_repository = AuthRepository(settings.database_path)
    app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    _seed_bootstrap_admin(app.state.auth_repository, settings)

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query or ""),
                    "duration_ms": duration_ms,
                    "client_host": request.client.host if request.client else "unknown",
                },
            )

        response.headers["X-Request-ID"] = request_id
        return response

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError):
        response = JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
            },
        )
        response.headers["X-Request-ID"] = _request_id_from_request(request)
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled exception while processing request",
            exc_info=exc,
            extra={"request_id": _request_id_from_request(request)},
        )
        response = JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_code": "internal_server_error",
            },
        )
        response.headers["X-Request-ID"] = _request_id_from_request(request)
        return response

    @app.get("/", include_in_schema=False, response_model=None)
    def root():
        return RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)

    @app.get("/login", response_class=HTMLResponse, include_in_schema=False, response_model=None)
    def login_page(request: Request):
        subject = _get_optional_subject(request)
        if subject:
            return RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)

        return _render_template(
            request,
            "login.html",
            {
                "page_title": "Login",
                "error_message": None,
                "settings": settings,
            },
        )

    @app.post("/auth/login", include_in_schema=False, response_model=None)
    def login_submit(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
    ):
        try:
            user = authenticate_local_user(
                auth_repository=_get_auth_repository(request),
                email=email,
                password=password,
            )
        except ApplicationError as exc:
            return _render_template(
                request,
                "login.html",
                {
                    "page_title": "Login",
                    "error_message": exc.detail,
                    "settings": settings,
                },
                status_code=exc.status_code,
            )

        raw_session_token = create_session_token()
        _get_auth_repository(request).create_session(
            user_id=user["user_id"],
            token_hash=hash_token(raw_session_token),
            session_duration_hours=settings.session_duration_hours,
        )

        response = RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)
        _set_session_cookie(response, raw_session_token, settings)
        return response

    @app.post("/auth/logout", include_in_schema=False, response_model=None)
    def logout_submit(request: Request):
        session_token = request.cookies.get(settings.session_cookie_name)
        if session_token:
            _get_auth_repository(request).delete_session(hash_token(session_token))

        response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        response.delete_cookie(settings.session_cookie_name)
        return response

    @app.get("/accept-invite", response_class=HTMLResponse, include_in_schema=False, response_model=None)
    def accept_invite_page(
        request: Request,
        token: str = Query(..., min_length=10),
    ):
        invite = _get_auth_repository(request).get_invite_by_token_hash(hash_token(token))
        return _render_template(
            request,
            "accept_invite.html",
            {
                "page_title": "Accept Invite",
                "invite": invite,
                "token": token,
                "error_message": None,
                "settings": settings,
            },
        )

    @app.post("/auth/accept-invite", include_in_schema=False, response_model=None)
    def accept_invite_submit(
        request: Request,
        token: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
    ):
        invite = _get_auth_repository(request).get_invite_by_token_hash(hash_token(token))
        if password != confirm_password:
            return _render_template(
                request,
                "accept_invite.html",
                {
                    "page_title": "Accept Invite",
                    "invite": invite,
                    "token": token,
                    "error_message": "Passwords do not match.",
                    "settings": settings,
                },
                status_code=400,
            )

        if len(password) < 10:
            return _render_template(
                request,
                "accept_invite.html",
                {
                    "page_title": "Accept Invite",
                    "invite": invite,
                    "token": token,
                    "error_message": "Password must be at least 10 characters long.",
                    "settings": settings,
                },
                status_code=400,
            )

        password_salt = create_password_salt()
        user = _get_auth_repository(request).accept_invite(
            token_hash=hash_token(token),
            password_hash=hash_password(password, password_salt),
            password_salt=password_salt,
        )

        raw_session_token = create_session_token()
        _get_auth_repository(request).create_session(
            user_id=user["user_id"],
            token_hash=hash_token(raw_session_token),
            session_duration_hours=settings.session_duration_hours,
        )

        response = RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)
        _set_session_cookie(response, raw_session_token, settings)
        return response

    @app.get("/app", response_class=HTMLResponse, include_in_schema=False, response_model=None)
    def app_dashboard(request: Request):
        subject = _get_optional_subject(request)
        if not subject:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

        document_repository = _get_document_repository(request)
        submitted_by = _scope_submitted_by(subject)
        summary = document_repository.get_summary(submitted_by=submitted_by)
        documents = document_repository.list_document_records(
            submitted_by=submitted_by,
            limit=20,
        )
        users = _get_auth_repository(request).list_users() if subject.role == ROLE_ADMIN else []

        # Phase 3: Role-based dashboard templates
        template_name = "dashboard.html"  # default fallback
        if subject.role == ROLE_ADMIN:
            template_name = "dashboard-admin.html"
        elif subject.role == ROLE_REVIEWER:
            template_name = "dashboard-reviewer.html"
        elif subject.role == ROLE_UPLOADER:
            template_name = "dashboard-uploader.html"

        return _render_template(
            request,
            template_name,
            {
                "page_title": "Dashboard",
                "subject": subject,
                "summary": summary,
                "documents": documents,
                "users": users,
                "settings": settings,
                "can_review": subject.role in {ROLE_ADMIN, ROLE_REVIEWER},
                "can_invite": subject.role == ROLE_ADMIN,
                "notice": request.query_params.get("notice"),
                "uploaded_document_id": request.query_params.get("uploaded"),
            },
        )

    @app.get("/app/review-queue", response_class=HTMLResponse, include_in_schema=False, response_model=None)
    def app_review_queue(request: Request):
        subject = _get_optional_subject(request)
        if not subject:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        
        if subject.role not in {ROLE_ADMIN, ROLE_REVIEWER}:
            return RedirectResponse(url="/app", status_code=status.HTTP_302_FOUND)

        document_repository = _get_document_repository(request)
        # Get documents pending review, sorted by confidence (lowest first for priority)
        # Note: Database doesn't yet support ordering, so we'll get records and sort in Python
        documents = document_repository.list_document_records(
            review_status="pending",  # Only documents awaiting review
            limit=50,
        )
        
        # Sort by confidence ascending (lowest confidence first for priority review)
        documents = sorted(documents, key=lambda d: float(d.get('confidence', 100)))

        return _render_template(
            request,
            "review-queue.html",
            {
                "page_title": "Review Queue",
                "subject": subject,
                "documents": documents,
                "notice": request.query_params.get("notice"),
            },
        )

    @app.post("/app/upload", include_in_schema=False, response_model=None)
    async def app_upload_document(
        request: Request,
        file: UploadFile = File(...),
    ):
        subject = _get_optional_subject(request)
        if not subject:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

        record = await _process_and_store_upload(request, file, subject, settings)
        return RedirectResponse(
            url=f"/app?uploaded={record['document_id']}&notice=Upload%20complete",
            status_code=status.HTTP_302_FOUND,
        )

    @app.post("/app/invites", include_in_schema=False, response_model=None)
    def app_create_invite(
        request: Request,
        email: str = Form(...),
        full_name: str = Form(...),
        role: str = Form(...),
    ):
        subject = _get_optional_subject(request)
        if not subject:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        if subject.role != ROLE_ADMIN:
            return RedirectResponse(url="/app?notice=Invite%20creation%20requires%20admin%20access", status_code=status.HTTP_302_FOUND)

        invite = _create_invite_record(
            request=request,
            payload=InviteUserRequest(email=email, full_name=full_name, role=role),
            subject=subject,
        )
        return RedirectResponse(
            url=f"/app?notice=Invite%20created%20for%20{invite.email}",
            status_code=status.HTTP_302_FOUND,
        )

    @app.post("/app/documents/{document_id}/review", include_in_schema=False, response_model=None)
    def app_review_document(
        document_id: str,
        request: Request,
        decision: str = Form(...),
        reviewer_notes: str = Form(default=""),
    ):
        subject = _get_optional_subject(request)
        if not subject:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        if subject.role not in {ROLE_ADMIN, ROLE_REVIEWER}:
            return RedirectResponse(url="/app?notice=Review%20access%20is%20restricted", status_code=status.HTTP_302_FOUND)

        document_repository = _get_document_repository(request)
        record = document_repository.get_document_record(document_id)
        _assert_can_access_document(subject, record)
        document_repository.update_review_status(
            document_id=document_id,
            decision=decision,
            reviewer_notes=reviewer_notes or None,
            reviewed_by=subject.subject_id,
        )
        return RedirectResponse(url="/app?notice=Review%20saved", status_code=status.HTTP_302_FOUND)

    @app.get("/health", response_model=HealthResponse)
    def health_check() -> HealthResponse:
        return HealthResponse(
            version=settings.app_version,
            environment=settings.app_environment,
        )

    @app.get("/ready", response_model=ReadinessResponse)
    def readiness_check(request: Request) -> ReadinessResponse:
        dependencies: list[DependencyHealth] = []
        overall_status = "ready"

        document_repository = _get_document_repository(request)
        auth_repository = _get_auth_repository(request)

        try:
            document_repository.check_connection()
            dependencies.append(DependencyHealth(name="sqlite", status="ok"))
        except Exception as exc:
            overall_status = "degraded"
            dependencies.append(DependencyHealth(name="sqlite", status="error", detail=str(exc)))

        try:
            user_count = auth_repository.count_users()
            if settings.enable_auth and not settings.api_keys and user_count == 0:
                overall_status = "degraded"
                dependencies.append(
                    DependencyHealth(
                        name="auth",
                        status="error",
                        detail="Authentication is enabled but no API keys or local users are configured.",
                    )
                )
            else:
                dependencies.append(
                    DependencyHealth(
                        name="auth",
                        status="ok",
                        detail="disabled" if not settings.enable_auth else f"{user_count} local users configured",
                    )
                )
        except Exception as exc:
            overall_status = "degraded"
            dependencies.append(DependencyHealth(name="auth", status="error", detail=str(exc)))

        dependencies.append(DependencyHealth(name="s3", status="ok", detail=settings.s3_bucket_name))
        dependencies.append(
            DependencyHealth(
                name="textract_region",
                status="ok",
                detail=settings.aws_region,
            )
        )

        return ReadinessResponse(
            status=overall_status,
            version=settings.app_version,
            environment=settings.app_environment,
            dependencies=dependencies,
        )

    @app.get("/auth/me", response_model=SessionResponse)
    def get_session_subject(
        request: Request,
        subject: AuthenticatedSubject = Depends(require_authenticated_subject),
    ) -> SessionResponse:
        user = _resolve_subject_user(request, subject)
        return SessionResponse(user=UserResponse(**user))

    @app.get("/users", response_model=UserListResponse)
    def list_users(
        request: Request,
        _subject: AuthenticatedSubject = Depends(require_roles(ROLE_ADMIN)),
    ) -> UserListResponse:
        users = _get_auth_repository(request).list_users()
        return UserListResponse(users=[UserResponse(**user) for user in users])

    @app.post("/admin/invites", response_model=InviteResponse)
    def create_invite(
        request: Request,
        payload: InviteUserRequest,
        subject: AuthenticatedSubject = Depends(require_roles(ROLE_ADMIN)),
    ) -> InviteResponse:
        return _create_invite_record(request=request, payload=payload, subject=subject)

    @app.get("/generate-upload-url", response_model=UploadUrlResponse)
    def generate_upload_url_endpoint(
        filename: str = Query(..., min_length=1),
        _subject: AuthenticatedSubject = Depends(
            require_roles(ROLE_ADMIN, ROLE_REVIEWER, ROLE_UPLOADER)
        ),
    ) -> UploadUrlResponse:
        upload_url, generated_filename = generate_upload_url(
            filename=filename,
            bucket_name=settings.s3_bucket_name,
            region_name=settings.aws_region,
            expires_in=settings.presigned_url_ttl_seconds,
        )
        return UploadUrlResponse(upload_url=upload_url, filename=generated_filename)

    @app.post("/upload", response_model=UploadDocumentResponse)
    async def upload_document(
        request: Request,
        file: UploadFile = File(...),
        subject: AuthenticatedSubject = Depends(
            require_roles(ROLE_ADMIN, ROLE_REVIEWER, ROLE_UPLOADER)
        ),
    ) -> UploadDocumentResponse:
        record = await _process_and_store_upload(request, file, subject, settings)
        return UploadDocumentResponse(**record)

    @app.get("/documents", response_model=DocumentListResponse)
    def list_documents(
        request: Request,
        review_status: ReviewStatus | None = Query(default=None),
        processing_status: ProcessingStatus | None = Query(default=None),
        document_type: str | None = Query(default=None),
        search: str | None = Query(default=None, min_length=1),
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
        subject: AuthenticatedSubject = Depends(
            require_roles(ROLE_ADMIN, ROLE_REVIEWER, ROLE_UPLOADER)
        ),
    ) -> DocumentListResponse:
        document_repository = _get_document_repository(request)
        records = document_repository.list_document_records(
            review_status=review_status.value if review_status else None,
            processing_status=processing_status.value if processing_status else None,
            document_type=document_type,
            submitted_by=_scope_submitted_by(subject),
            search=search,
            limit=limit,
            offset=offset,
        )
        return DocumentListResponse(documents=[DocumentRecordResponse(**record) for record in records])

    @app.get("/documents/summary", response_model=DocumentSummaryResponse)
    def get_document_summary(
        request: Request,
        subject: AuthenticatedSubject = Depends(
            require_roles(ROLE_ADMIN, ROLE_REVIEWER, ROLE_UPLOADER)
        ),
    ) -> DocumentSummaryResponse:
        document_repository = _get_document_repository(request)
        return DocumentSummaryResponse(
            **document_repository.get_summary(submitted_by=_scope_submitted_by(subject))
        )

    @app.get("/documents/{document_id}", response_model=DocumentRecordResponse)
    def get_document(
        document_id: str,
        request: Request,
        subject: AuthenticatedSubject = Depends(
            require_roles(ROLE_ADMIN, ROLE_REVIEWER, ROLE_UPLOADER)
        ),
    ) -> DocumentRecordResponse:
        document_repository = _get_document_repository(request)
        record = document_repository.get_document_record(document_id)
        _assert_can_access_document(subject, record)
        return DocumentRecordResponse(**record)

    @app.patch("/documents/{document_id}/review", response_model=DocumentRecordResponse)
    def review_document(
        document_id: str,
        payload: ReviewDecisionRequest,
        request: Request,
        subject: AuthenticatedSubject = Depends(require_roles(ROLE_ADMIN, ROLE_REVIEWER)),
    ) -> DocumentRecordResponse:
        document_repository = _get_document_repository(request)
        record = document_repository.get_document_record(document_id)
        _assert_can_access_document(subject, record)
        updated = document_repository.update_review_status(
            document_id=document_id,
            decision=payload.decision.value,
            reviewer_notes=payload.reviewer_notes,
            reviewed_by=subject.subject_id,
        )
        return DocumentRecordResponse(**updated)

    return app


async def _process_and_store_upload(
    request: Request,
    file: UploadFile,
    subject: AuthenticatedSubject,
    settings: Settings,
) -> dict[str, object]:
    file_bytes = await file.read()
    _validate_upload(file, file_bytes, settings.max_file_size_bytes)

    result = process_tax_document(
        file_bytes=file_bytes,
        original_filename=file.filename or "upload.pdf",
        settings=settings,
    )

    document_repository = _get_document_repository(request)
    return document_repository.create_document_record(
        original_filename=file.filename or "upload.pdf",
        processing_result=result,
        submitted_by=subject.subject_id,
    )


def _create_invite_record(
    *,
    request: Request,
    payload: InviteUserRequest,
    subject: AuthenticatedSubject,
) -> InviteResponse:
    settings = request.app.state.settings
    raw_token = create_invite_token()
    invite = _get_auth_repository(request).create_invite(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role.value,
        created_by=subject.subject_id,
        token_hash=hash_token(raw_token),
        invite_duration_hours=settings.invite_duration_hours,
    )
    return InviteResponse(
        invite_id=invite["invite_id"],
        email=invite["email"],
        full_name=invite["full_name"],
        role=invite["role"],
        invite_url=str(request.base_url).rstrip("/") + f"/accept-invite?token={raw_token}",
        expires_at=invite["expires_at"],
        created_at=invite["created_at"],
    )


def _seed_bootstrap_admin(auth_repository: AuthRepository, settings: Settings) -> None:
    if not settings.bootstrap_admin_email or not settings.bootstrap_admin_password:
        return

    password_salt = create_password_salt()
    auth_repository.seed_bootstrap_admin(
        email=settings.bootstrap_admin_email,
        full_name=settings.bootstrap_admin_name,
        password_hash=hash_password(settings.bootstrap_admin_password, password_salt),
        password_salt=password_salt,
    )


def _resolve_subject_user(request: Request, subject: AuthenticatedSubject) -> dict[str, object]:
    if subject.auth_scheme == "disabled":
        return {
            "user_id": subject.subject_id,
            "email": "local-dev@example.com",
            "full_name": subject.display_name or "Local Development",
            "role": subject.role,
            "auth_provider": "disabled",
            "is_active": True,
            "created_at": "",
            "updated_at": "",
            "last_login_at": None,
        }

    if subject.auth_scheme == "api_key":
        return {
            "user_id": subject.subject_id,
            "email": "api-key@service.local",
            "full_name": subject.display_name or "Service API Key",
            "role": subject.role,
            "auth_provider": "api_key",
            "is_active": True,
            "created_at": "",
            "updated_at": "",
            "last_login_at": None,
        }

    return _get_auth_repository(request).get_user_by_id(subject.subject_id)


def _render_template(
    request: Request,
    template_name: str,
    context: dict[str, object],
    *,
    status_code: int = 200,
) -> HTMLResponse:
    templates: Jinja2Templates = request.app.state.templates
    merged_context = {"request": request, **context}
    return templates.TemplateResponse(request, template_name, merged_context, status_code=status_code)


def _scope_submitted_by(subject: AuthenticatedSubject) -> str | None:
    if subject.role == ROLE_UPLOADER:
        return subject.subject_id
    return None


def _assert_can_access_document(subject: AuthenticatedSubject, record: dict[str, object]) -> None:
    if subject.role == ROLE_UPLOADER and record["submitted_by"] != subject.subject_id:
        raise AuthorizationError("You can only access documents that you uploaded.")


def _get_optional_subject(request: Request) -> AuthenticatedSubject | None:
    try:
        return require_authenticated_subject(
            request=request,
            authorization=request.headers.get("Authorization"),
            x_api_key=request.headers.get("X-API-Key"),
        )
    except ApplicationError:
        return None


def _set_session_cookie(response: RedirectResponse, raw_session_token: str, settings: Settings) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_session_token,
        httponly=True,
        samesite="lax",
        secure=settings.app_environment == "production",
        max_age=settings.session_duration_hours * 3600,
    )


def _validate_upload(file: UploadFile, file_bytes: bytes, max_file_size_bytes: int) -> None:
    filename = file.filename or ""

    if not filename.lower().endswith(".pdf"):
        raise InvalidUploadError("Only PDF files are allowed.")

    if not file_bytes:
        raise InvalidUploadError("Uploaded file is empty.")

    if len(file_bytes) > max_file_size_bytes:
        limit_megabytes = max_file_size_bytes / (1024 * 1024)
        raise InvalidUploadError(f"File exceeds {limit_megabytes:.0f}MB limit.")

    if not file_bytes.startswith(b"%PDF"):
        raise InvalidUploadError("Uploaded file is not a valid PDF.")


def _get_document_repository(request: Request) -> DocumentRepository:
    return request.app.state.document_repository


def _get_auth_repository(request: Request) -> AuthRepository:
    return request.app.state.auth_repository


def _request_id_from_request(request: Request) -> str:
    return getattr(request.state, "request_id", "-")


app = create_app()
