"""Pydantic models for vector calculus feature."""
from typing import Optional, List
from pydantic import BaseModel


class CreateCoordinateSystemRequest(BaseModel):
    session_id: str
    name: str
    coord_names: Optional[List[str]] = None


class CreateVectorFieldRequest(BaseModel):
    session_id: str
    coord_sys_name: str
    x: str
    y: str
    z: str


class VectorFieldKeyRequest(BaseModel):
    session_id: str
    vector_field_key: str


class ScalarFieldKeyRequest(BaseModel):
    session_id: str
    scalar_field_key: str


class VectorCalcResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    result_key: Optional[str] = None
    error: Optional[str] = None
