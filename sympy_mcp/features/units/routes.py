"""REST routes for units feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.features.units.models import (
    ConvertToUnitsRequest,
    QuantitySimplifyRequest,
    UnitsResponse,
)

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/units", tags=["Units"])

    @router.post(
        "/convert",
        response_model=UnitsResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def convert(request: ConvertToUnitsRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.convert_to_units(
                request.expr_key, request.target_units, request.unit_system
            )
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return UnitsResponse(success=True, result=resolved, result_key=raw)
            return UnitsResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"convert_to_units error: {e}")
            return UnitsResponse(success=False, error=str(e))

    @router.post(
        "/simplify",
        response_model=UnitsResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def simplify(request: QuantitySimplifyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.quantity_simplify_units(request.expr_key, request.unit_system)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return UnitsResponse(success=True, result=resolved, result_key=raw)
            return UnitsResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"quantity_simplify_units error: {e}")
            return UnitsResponse(success=False, error=str(e))

    return router
