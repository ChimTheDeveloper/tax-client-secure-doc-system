from __future__ import annotations


class ApplicationError(Exception):
    status_code = 500
    error_code = "application_error"
    detail = "Application error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)


class InvalidUploadError(ApplicationError):
    status_code = 400
    error_code = "invalid_upload"
    detail = "The uploaded file is invalid."


class AuthenticationError(ApplicationError):
    status_code = 401
    error_code = "authentication_error"
    detail = "Authentication failed."


class ConfigurationError(ApplicationError):
    status_code = 503
    error_code = "configuration_error"
    detail = "The service is not configured correctly."


class NotFoundError(ApplicationError):
    status_code = 404
    error_code = "not_found"
    detail = "The requested resource was not found."


class ConflictError(ApplicationError):
    status_code = 409
    error_code = "conflict"
    detail = "The requested operation conflicts with the current resource state."


class UnsupportedDocumentError(ApplicationError):
    status_code = 422
    error_code = "unsupported_document"
    detail = "The uploaded document is not supported."


class ExternalServiceError(ApplicationError):
    status_code = 502
    error_code = "external_service_error"
    detail = "An upstream dependency failed."


class StorageError(ApplicationError):
    status_code = 502
    error_code = "storage_error"
    detail = "Document storage failed."
