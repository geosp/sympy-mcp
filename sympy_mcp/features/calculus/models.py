"""Pydantic models for calculus feature."""
from typing import Optional
from pydantic import BaseModel


class SimplifyRequest(BaseModel):
    session_id: str
    expr_key: str


class IntegrateRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str
    lower: Optional[str] = None
    upper: Optional[str] = None


class DifferentiateRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str
    order: int = 1


class CalculusResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
