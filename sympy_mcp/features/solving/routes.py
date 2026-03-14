"""REST routes for solving feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.features.solving.models import (
    SolveAlgebraicallyRequest, SolveLinearSystemRequest,
    SolveNonlinearSystemRequest, SolveResponse
)

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/solve", tags=["Solving"])

    @router.post(
        "/algebraic",
        response_model=SolveResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def solve_algebraically(request: SolveAlgebraicallyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.solve_algebraically(request.expr_key, request.solve_for_var_name, request.domain)
            return SolveResponse(success=True, result=result)
        except Exception as e:
            return SolveResponse(success=False, error=str(e))

    @router.post(
        "/linear",
        response_model=SolveResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def solve_linear(request: SolveLinearSystemRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.solve_linear_system(request.expr_keys, request.var_names, request.domain)
            return SolveResponse(success=True, result=result)
        except Exception as e:
            return SolveResponse(success=False, error=str(e))

    @router.post(
        "/nonlinear",
        response_model=SolveResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def solve_nonlinear(request: SolveNonlinearSystemRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.solve_nonlinear_system(request.expr_keys, request.var_names, request.domain)
            return SolveResponse(success=True, result=result)
        except Exception as e:
            return SolveResponse(success=False, error=str(e))

    return router
