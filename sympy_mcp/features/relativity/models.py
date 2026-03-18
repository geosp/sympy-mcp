"""Pydantic models for relativity feature."""
from typing import Optional, List
from pydantic import BaseModel
from sympy_mcp.shared.enums import Metric, Tensor


class CreatePredefinedMetricRequest(BaseModel):
    session_id: str
    metric_name: Metric


class SearchPredefinedMetricsRequest(BaseModel):
    session_id: str
    query: str


class CalculateTensorRequest(BaseModel):
    session_id: str
    metric_key: str
    tensor_type: Tensor
    simplify: bool = True


class CreateCustomMetricRequest(BaseModel):
    session_id: str
    components: List[List[str]]
    coord_symbols: List[str]
    config: str = "ll"


class PrintLatexTensorRequest(BaseModel):
    session_id: str
    tensor_key: str


class RelativityResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
