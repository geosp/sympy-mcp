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


class LimitRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str
    point: str
    direction: str = "+"


class SeriesExpansionRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str
    point: str = "0"
    order: int = 6


class SummationRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str
    lower: str
    upper: str


class CalculusResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
