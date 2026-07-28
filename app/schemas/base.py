from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

DataType = TypeVar("DataType")


class ErrorDetail(BaseModel):
    """
    Standardized error payload detail schema.
    """

    code: str = Field(..., description="Application error classification code")
    message: str = Field(..., description="Human-readable error description")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional contextual error attributes"
    )


class APIResponse(BaseModel, Generic[DataType]):
    """
    Standard top-level JSON response envelope for all API endpoints.
    Provides predictable schema structure for clients across success and failure payloads.
    """

    success: bool = Field(
        ..., description="Indicates whether the API operation succeeded"
    )
    data: Optional[DataType] = Field(
        default=None, description="Response payload data when operation succeeds"
    )
    error: Optional[ErrorDetail] = Field(
        default=None, description="Error detail object when operation fails"
    )
    meta: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata such as pagination or request context"
    )

    @classmethod
    def ok(
        cls, data: Optional[DataType] = None, meta: Optional[Dict[str, Any]] = None
    ) -> "APIResponse[DataType]":
        """Factory helper to construct a successful API response."""
        return cls(
            success=True,
            data=data,
            error=None,
            meta=meta or {},
        )

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> "APIResponse[DataType]":
        """Factory helper to construct an error API response."""
        return cls(
            success=False,
            data=None,
            error=ErrorDetail(code=code, message=message, details=details or {}),
            meta=meta or {},
        )
