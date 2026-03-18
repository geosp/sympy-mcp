"""Shared Pydantic models for SymPy MCP REST API."""

from typing import Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
