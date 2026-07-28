from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class ComplianceException(Exception):
    """Base exception for all compliance service related errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationException(ComplianceException):
    """Exception raised when request data validation fails for compliance checks."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class AgentProcessingException(ComplianceException):
    """Exception raised when the agent encounters an issue processing the document."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers exception handlers to map custom exceptions to JSON responses."""
    
    @app.exception_handler(ComplianceException)
    async def compliance_exception_handler(request: Request, exc: ComplianceException) -> JSONResponse:
        logger.error(f"Compliance exception on {request.url.path}: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred in the service."},
        )
