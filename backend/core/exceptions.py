from enum import StrEnum
from django.forms.utils import ErrorDict


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NOT_FOUND = "NOT_FOUND"
    INVALID_OPERATION = "INVALID_OPERATION"
    CONFLICT = "CONFLICT"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    BAD_REQUEST = "BAD_REQUEST"


# Rework to accept different error codes
class DomainException(Exception):
    """Base class for all expected domain-level exceptions."""

    code: ErrorCode

    def __init__(self, message: str):
        super().__init__(message)


class ValidationException(DomainException):
    """Exception raised for validation errors."""

    code = ErrorCode.VALIDATION_ERROR

    def __init__(self, message: str):
        super().__init__(message)


class FormValidationException(ValidationException):
    """Exception raised for form validation errors."""

    def __init__(self, message: str, errors: ErrorDict):
        self.errors = self._format_form_errors(errors)
        super().__init__(message)

    @staticmethod
    def _format_form_errors(errors: ErrorDict) -> dict[str, list[str]]:
        return {
            field: [e["message"] for e in errs]
            for field, errs in errors.get_json_data().items()
        }


class PermissionException(DomainException):
    """Exception raised for permission errors."""

    code = ErrorCode.PERMISSION_DENIED

    def __init__(self, message: str):
        super().__init__(message)


class NotFoundException(DomainException):
    """Exception raised when an entity is not found."""

    code = ErrorCode.NOT_FOUND

    def __init__(self, message: str):
        super().__init__(message)


class ConflictException(DomainException):
    """Exception raised for conflict errors."""

    code = ErrorCode.CONFLICT

    def __init__(self, message: str):
        super().__init__(message)
