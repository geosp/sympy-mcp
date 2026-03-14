"""Pydantic models for expressions feature."""
from typing import Optional
from pydantic import BaseModel


class IntroduceExpressionRequest(BaseModel):
    session_id: str
    expr_str: str
    canonicalize: bool = True
    name: Optional[str] = None


class IntroduceEquationRequest(BaseModel):
    session_id: str
    lhs_str: str
    rhs_str: str


class PrintLatexRequest(BaseModel):
    session_id: str
    expr_key: str


class SubstituteExpressionRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str
    replacement_expr_key: str


class ExpressionResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
