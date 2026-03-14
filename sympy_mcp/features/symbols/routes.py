"""REST routes for symbols feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.features.symbols.models import IntroRequest, IntroManyRequest, SymbolResponse

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/symbols", tags=["Symbols"])

    @router.post(
        "/intro",
        response_model=SymbolResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def intro(request: IntroRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.intro(request.var_name, request.pos_assumptions, request.neg_assumptions)
            return SymbolResponse(success=True, result=result)
        except Exception as e:
            logger.error(f"intro error: {e}")
            return SymbolResponse(success=False, error=str(e))

    @router.post(
        "/intro_many",
        response_model=SymbolResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def intro_many(request: IntroManyRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.intro_many(request.variables)
            return SymbolResponse(success=True, result=result)
        except Exception as e:
            logger.error(f"intro_many error: {e}")
            return SymbolResponse(success=False, error=str(e))

    return router
