"""Pydantic models for functions feature."""
from typing import List, Optional
from pydantic import BaseModel
from sympy_mcp.shared.enums import ODEHint, PDEHint


class IntroduceFunctionRequest(BaseModel):
    session_id: str
    func_name: str


class DsolveODERequest(BaseModel):
    session_id: str
    expr_key: str
    func_name: str
    hint: ODEHint = ODEHint.FACTORABLE


class DsolveSystemRequest(BaseModel):
    session_id: str
    expr_keys: List[str]
    func_names: List[str]


class PdsolvePDERequest(BaseModel):
    session_id: str
    expr_key: str
    func_name: str
    hint: PDEHint = PDEHint.FIRST_LINEAR_CONSTANT_COEFF_HOMOGENEOUS


class FunctionResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
