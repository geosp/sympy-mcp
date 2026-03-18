"""REST routes for linear algebra feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.features.linear_algebra.models import (
    CreateMatrixRequest,
    MatrixKeyRequest,
    LinearAlgebraResponse,
)

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/matrix", tags=["Linear Algebra"])

    @router.post(
        "/create",
        response_model=LinearAlgebraResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def create_matrix(request: CreateMatrixRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.create_matrix(request.matrix_data, request.name)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return LinearAlgebraResponse(success=True, result=resolved, result_key=raw)
            return LinearAlgebraResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"create_matrix error: {e}")
            return LinearAlgebraResponse(success=False, error=str(e))

    @router.post(
        "/determinant",
        response_model=LinearAlgebraResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def determinant(request: MatrixKeyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.matrix_determinant(request.matrix_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return LinearAlgebraResponse(success=True, result=resolved, result_key=raw)
            return LinearAlgebraResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"matrix_determinant error: {e}")
            return LinearAlgebraResponse(success=False, error=str(e))

    @router.post(
        "/inverse",
        response_model=LinearAlgebraResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def inverse(request: MatrixKeyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.matrix_inverse(request.matrix_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return LinearAlgebraResponse(success=True, result=resolved, result_key=raw)
            return LinearAlgebraResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"matrix_inverse error: {e}")
            return LinearAlgebraResponse(success=False, error=str(e))

    @router.post(
        "/eigenvalues",
        response_model=LinearAlgebraResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def eigenvalues(request: MatrixKeyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.matrix_eigenvalues(request.matrix_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return LinearAlgebraResponse(success=True, result=resolved, result_key=raw)
            return LinearAlgebraResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"matrix_eigenvalues error: {e}")
            return LinearAlgebraResponse(success=False, error=str(e))

    @router.post(
        "/eigenvectors",
        response_model=LinearAlgebraResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def eigenvectors(request: MatrixKeyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.matrix_eigenvectors(request.matrix_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return LinearAlgebraResponse(success=True, result=resolved, result_key=raw)
            return LinearAlgebraResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"matrix_eigenvectors error: {e}")
            return LinearAlgebraResponse(success=False, error=str(e))

    return router
