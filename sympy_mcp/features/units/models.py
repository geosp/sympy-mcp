"""Pydantic models for units feature."""
from typing import Optional, List
from pydantic import BaseModel
from sympy_mcp.shared.enums import UnitSystem


class ConvertToUnitsRequest(BaseModel):
    session_id: str
    expr_key: str
    target_units: List[str]
    unit_system: UnitSystem = UnitSystem.SI


class QuantitySimplifyRequest(BaseModel):
    session_id: str
    expr_key: str
    unit_system: UnitSystem = UnitSystem.SI


class UnitsResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
