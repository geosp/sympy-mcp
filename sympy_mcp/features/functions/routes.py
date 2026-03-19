"""REST routes for functions feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError
from sympy_mcp.features.functions.models import (
    IntroduceFunctionRequest, DsolveODERequest, DsolveSystemRequest, PdsolvePDERequest, FunctionResponse
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
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return FunctionResponse(success=False, error=str(e))
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
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return FunctionResponse(success=False, error=str(e))
        try:
            result = state.dsolve_ode(request.expr_key, request.func_name, request.hint)
            return FunctionResponse(success=True, result=result)
        except Exception as e:
            return FunctionResponse(success=False, error=str(e))

    @router.post(
        "/dsolve-system",
        response_model=FunctionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def dsolve_system(request: DsolveSystemRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return FunctionResponse(success=False, error=str(e))
        try:
            result = state.dsolve_system(request.expr_keys, request.func_names)
            return FunctionResponse(success=True, result=result)
        except Exception as e:
            return FunctionResponse(success=False, error=str(e))

    @router.post(
        "/pdsolve",
        response_model=FunctionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def pdsolve(request: PdsolvePDERequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return FunctionResponse(success=False, error=str(e))
        try:
            result = state.pdsolve_pde(request.expr_key, request.func_name, request.hint)
            return FunctionResponse(success=True, result=result)
        except Exception as e:
            return FunctionResponse(success=False, error=str(e))

    return router
