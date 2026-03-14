"""REST routes for functions feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.features.functions.models import (
    IntroduceFunctionRequest, DsolveODERequest, PdsolvePDERequest, FunctionResponse
)

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/functions", tags=["Functions"])

    @router.post(
        "/introduce",
        response_model=FunctionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def introduce_function(request: IntroduceFunctionRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.introduce_function(request.func_name)
            if raw in state.functions:
                return FunctionResponse(success=True, result=raw, result_key=raw)
            return FunctionResponse(success=False, error=raw)
        except Exception as e:
            return FunctionResponse(success=False, error=str(e))

    @router.post(
        "/dsolve",
        response_model=FunctionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def dsolve(request: DsolveODERequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.dsolve_ode(request.expr_key, request.func_name, request.hint)
            return FunctionResponse(success=True, result=result)
        except Exception as e:
            return FunctionResponse(success=False, error=str(e))

    @router.post(
        "/pdsolve",
        response_model=FunctionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def pdsolve(request: PdsolvePDERequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.pdsolve_pde(request.expr_key, request.func_name, request.hint)
            return FunctionResponse(success=True, result=result)
        except Exception as e:
            return FunctionResponse(success=False, error=str(e))

    return router
