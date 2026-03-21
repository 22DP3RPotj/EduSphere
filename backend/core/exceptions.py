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


def format_form_errors(errors: ErrorDict) -> dict[str, list[str]]:
    return {
        field: list(dict.fromkeys(e.get("message", str(e)) for e in errs))
        for field, errs in errors.get_json_data().items()
    }


class FormValidationException(ValidationException):
    """Exception raised for form validation errors."""

    def __init__(self, message: str, errors: ErrorDict):
        self.errors = format_form_errors(errors)
        super().__init__(message)


class PermissionException(DomainException):
    """Exception raised for permission errors."""

    code = ErrorCode.PERMISSION_DENIED


class NotFoundException(DomainException):
    """Exception raised when an entity is not found."""

    code = ErrorCode.NOT_FOUND


class ConflictException(DomainException):
    """Exception raised for conflict errors."""

    code = ErrorCode.CONFLICT


class AlreadyExistsException(DomainException):
    """Exception raised when trying to create an entity that already exists."""

    code = ErrorCode.ALREADY_EXISTS


class InternalErrorException(DomainException):
    """Exception raised for unexpected internal errors."""

    code = ErrorCode.INTERNAL_ERROR


class BadRequestException(DomainException):
    """Exception raised for bad requests."""

    code = ErrorCode.BAD_REQUEST
