"""Pydantic models for expressions feature."""
from typing import Optional
from pydantic import BaseModel


class IntroduceExpressionRequest(BaseModel):
    session_id: str
    expression: str
    canonicalize: bool = True
    name: Optional[str] = None


class IntroduceEquationRequest(BaseModel):
    session_id: str
    lhs_expression: str
    rhs_expression: str


class PrintLatexRequest(BaseModel):
    session_id: str
    expr_key: str


class SubstituteExpressionRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str
    replacement_expr_key: str


class FactorRequest(BaseModel):
    session_id: str
    expr_key: str


class ExpandRequest(BaseModel):
    session_id: str
    expr_key: str


class CollectRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str


class ApartRequest(BaseModel):
    session_id: str
    expr_key: str
    var_name: str


class EvalfRequest(BaseModel):
    session_id: str
    expr_key: str
    n: int = 15


class ExpressionResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
