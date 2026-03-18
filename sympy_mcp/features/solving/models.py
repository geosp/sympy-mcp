"""Pydantic models for solving feature."""
from typing import List, Optional
from pydantic import BaseModel
from sympy_mcp.shared.enums import Domain


class SolveAlgebraicallyRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str
    domain: Domain = Domain.COMPLEX


class SolveLinearSystemRequest(BaseModel):
    session_id: str
    expr_keys: List[str]
    var_names: List[str]
    domain: Domain = Domain.COMPLEX


class SolveNonlinearSystemRequest(BaseModel):
    session_id: str
    expr_keys: List[str]
    var_names: List[str]
    domain: Domain = Domain.COMPLEX


class SolveResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
