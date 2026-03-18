"""REST routes for calculus feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError
from sympy_mcp.features.calculus.models import (
    SimplifyRequest,
    IntegrateRequest,
    DifferentiateRequest,
    LimitRequest,
    SeriesExpansionRequest,
    SummationRequest,
    CalculusResponse,
)

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/calculus", tags=["Calculus"])

    @router.post(
        "/simplify",
        response_model=CalculusResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def simplify(request: SimplifyRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return CalculusResponse(success=False, error=str(e))
        try:
            raw = state.simplify_expression(request.expr_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return CalculusResponse(success=True, result=resolved, result_key=raw)
            return CalculusResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"simplify error: {e}")
            return CalculusResponse(success=False, error=str(e))

    @router.post(
        "/integrate",
        response_model=CalculusResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def integrate(request: IntegrateRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return CalculusResponse(success=False, error=str(e))
        try:
            raw = state.integrate_expression(
                request.expr_key, request.var_name, request.lower_bound, request.upper_bound
            )
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return CalculusResponse(success=True, result=resolved, result_key=raw)
            return CalculusResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"integrate error: {e}")
            return CalculusResponse(success=False, error=str(e))

    @router.post(
        "/differentiate",
        response_model=CalculusResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def differentiate(request: DifferentiateRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return CalculusResponse(success=False, error=str(e))
        try:
            raw = state.differentiate_expression(
                request.expr_key, request.var_name, request.order
            )
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return CalculusResponse(success=True, result=resolved, result_key=raw)
            return CalculusResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"differentiate error: {e}")
            return CalculusResponse(success=False, error=str(e))

    @router.post(
        "/limit",
        response_model=CalculusResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def limit(request: LimitRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return CalculusResponse(success=False, error=str(e))
        try:
            raw = state.limit_expression(request.expr_key, request.var_name, request.point, request.direction)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return CalculusResponse(success=True, result=resolved, result_key=raw)
            return CalculusResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"limit error: {e}")
            return CalculusResponse(success=False, error=str(e))

    @router.post(
        "/series",
        response_model=CalculusResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def series(request: SeriesExpansionRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return CalculusResponse(success=False, error=str(e))
        try:
            raw = state.series_expansion(request.expr_key, request.var_name, request.point, request.order)
            if raw.startswith("Error"):
                return CalculusResponse(success=False, error=raw)
            key, display = raw.split("|||", 1)
            return CalculusResponse(success=True, result=display, result_key=key)
        except Exception as e:
            logger.error(f"series error: {e}")
            return CalculusResponse(success=False, error=str(e))

    @router.post(
        "/summation",
        response_model=CalculusResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def summation(request: SummationRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return CalculusResponse(success=False, error=str(e))
        try:
            raw = state.summation_expression(request.expr_key, request.var_name, request.lower_bound, request.upper_bound)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return CalculusResponse(success=True, result=resolved, result_key=raw)
            return CalculusResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"summation error: {e}")
            return CalculusResponse(success=False, error=str(e))

    return router
