"""Pydantic models for symbols feature."""
from typing import List, Optional, Any
from pydantic import BaseModel
from sympy_mcp.shared.enums import Assumption


class IntroRequest(BaseModel):
    session_id: str
    var_name: str
    pos_assumptions: List[Assumption] = []
    neg_assumptions: List[Assumption] = []


class IntroManyRequest(BaseModel):
    session_id: str
    variables: List[Any]  # List of [name, pos_assumptions, neg_assumptions] or just name strings


class SymbolResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
