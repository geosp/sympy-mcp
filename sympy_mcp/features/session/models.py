"""Pydantic models for session feature."""
from typing import Optional
from pydantic import BaseModel


class ResetStateRequest(BaseModel):
    session_id: str


class SessionResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
