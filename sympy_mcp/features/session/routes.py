"""REST routes for session management."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.features.session.models import ResetStateRequest, SessionResponse

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/session", tags=["Session"])

    @router.post(
        "/reset",
        response_model=SessionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def reset_state(request: ResetStateRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.reset_state()
            return SessionResponse(success=True, result=result)
        except Exception as e:
            logger.error(f"reset_state error: {e}")
            return SessionResponse(success=False, error=str(e))

    return router
