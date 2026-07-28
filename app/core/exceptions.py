from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


class TrustAgentException(Exception):
    """
    Base exception class for all Trust-Agent application errors.
    """

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}


class DomainException(TrustAgentException):
    """Base exception for domain / business logic rules violations."""

    def __init__(
        self,
        message: str = "Domain rule violation",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "DOMAIN_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            code=code,
            details=details,
        )


class NotFoundException(DomainException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        message: str = "Requested resource was not found",
        code: str = "NOT_FOUND",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            code=code,
            details=details,
        )


class ValidationException(DomainException):
    """Raised when request payload or data validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=code,
            details=details,
        )


class UnauthorizedException(DomainException):
    """Raised when authentication fails or credentials are missing."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: str = "UNAUTHORIZED",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=code,
            details=details,
        )


class ForbiddenException(DomainException):
    """Raised when authenticated user lacks required permissions."""

    def __init__(
        self,
        message: str = "Access forbidden",
        code: str = "FORBIDDEN",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code=code,
            details=details,
        )


class ServiceUnavailableException(TrustAgentException):
    """Raised when an downstream dependency or service is unavailable."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        code: str = "SERVICE_UNAVAILABLE",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code=code,
            details=details,
        )


def _build_error_payload(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Helper utility to format standardized error JSON responses."""
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }


async def trust_agent_exception_handler(
    request: Request, exc: TrustAgentException
) -> JSONResponse:
    """Handler for application-specific custom exceptions."""
    logger.warning(
        f"Custom exception caught [{exc.code}]: {exc.message}",
        extra={"path": request.url.path},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_payload(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ),
    )


async def fastapi_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for FastAPI/Pydantic request payload validation errors."""
    logger.warning(
        f"Validation error on {request.url.path}: {exc.errors()}",
        extra={"path": request.url.path},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_build_error_payload(
            code="VALIDATION_ERROR",
            message="Input validation failed",
            details={"errors": exc.errors()},
        ),
    )


async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handler for Starlette/FastAPI HTTP exceptions."""
    code_map = {
        404: "NOT_FOUND",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        405: "METHOD_NOT_ALLOWED",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_payload(
            code=code,
            message=str(exc.detail),
        ),
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Fallback handler for unhandled exceptions to prevent leaking trace details."""
    logger.error(
        f"Unhandled exception caught on {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_build_error_payload(
            code="INTERNAL_SERVER_ERROR",
            message="An internal server error occurred.",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers all global exception handlers on the FastAPI app instance."""
    app.add_exception_handler(TrustAgentException, trust_agent_exception_handler)
    app.add_exception_handler(RequestValidationError, fastapi_validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
