"""REST routes for vector calculus feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.features.vector_calc.models import (
    CreateCoordinateSystemRequest,
    CreateVectorFieldRequest,
    VectorFieldKeyRequest,
    ScalarFieldKeyRequest,
    VectorCalcResponse,
)

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/vector", tags=["Vector Calculus"])

    @router.post(
        "/coordinate_system",
        response_model=VectorCalcResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def coordinate_system(request: CreateCoordinateSystemRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.create_coordinate_system(request.name, request.coord_names)
            if raw in state.coordinate_systems:
                return VectorCalcResponse(success=True, result=raw, result_key=raw)
            return VectorCalcResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"create_coordinate_system error: {e}")
            return VectorCalcResponse(success=False, error=str(e))

    @router.post(
        "/field",
        response_model=VectorCalcResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def vector_field(request: CreateVectorFieldRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.create_vector_field(
                request.coord_sys_name, request.x, request.y, request.z
            )
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return VectorCalcResponse(success=True, result=resolved, result_key=raw)
            return VectorCalcResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"create_vector_field error: {e}")
            return VectorCalcResponse(success=False, error=str(e))

    @router.post(
        "/curl",
        response_model=VectorCalcResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def curl(request: VectorFieldKeyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.calculate_curl(request.vector_field_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return VectorCalcResponse(success=True, result=resolved, result_key=raw)
            return VectorCalcResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"calculate_curl error: {e}")
            return VectorCalcResponse(success=False, error=str(e))

    @router.post(
        "/divergence",
        response_model=VectorCalcResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def divergence(request: VectorFieldKeyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.calculate_divergence(request.vector_field_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return VectorCalcResponse(success=True, result=resolved, result_key=raw)
            return VectorCalcResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"calculate_divergence error: {e}")
            return VectorCalcResponse(success=False, error=str(e))

    @router.post(
        "/gradient",
        response_model=VectorCalcResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def gradient(request: ScalarFieldKeyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.calculate_gradient(request.scalar_field_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return VectorCalcResponse(success=True, result=resolved, result_key=raw)
            return VectorCalcResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"calculate_gradient error: {e}")
            return VectorCalcResponse(success=False, error=str(e))

    return router
