"""Pydantic models for linear algebra feature."""
from typing import Optional, List
from pydantic import BaseModel


class CreateMatrixRequest(BaseModel):
    session_id: str
    matrix_data: List[List[str]]
    name: Optional[str] = None


class MatrixKeyRequest(BaseModel):
    session_id: str
    matrix_key: str


class LinearAlgebraResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
