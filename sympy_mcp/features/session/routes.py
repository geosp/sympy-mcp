"""REST routes for session management."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError
from sympy_mcp.features.session.models import ResetStateRequest, ListStateRequest, DeleteStoredKeyRequest, SessionResponse

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/session", tags=["Session"])

    @router.post(
        "/reset",
        response_model=SessionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def reset_state(request: ResetStateRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return SessionResponse(success=False, error=str(e))
        try:
            result = state.reset_state()
            return SessionResponse(success=True, result=result)
        except Exception as e:
            logger.error(f"reset_state error: {e}")
            return SessionResponse(success=False, error=str(e))

    @router.post(
        "/list",
        response_model=SessionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def list_state(request: ListStateRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return SessionResponse(success=False, error=str(e))
        try:
            result = state.list_session_state()
            return SessionResponse(success=True, result=result)
        except Exception as e:
            logger.error(f"list_state error: {e}")
            return SessionResponse(success=False, error=str(e))

    @router.post(
        "/delete",
        response_model=SessionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def delete_stored_key(request: DeleteStoredKeyRequest):
        try:
            state = session_manager.get_sync(request.session_id)
        except SessionNotFoundError as e:
            return SessionResponse(success=False, error=str(e))
        try:
            result = state.delete_stored_key(request.key)
            if result.startswith("Error"):
                return SessionResponse(success=False, error=result)
            return SessionResponse(success=True, result=result)
        except Exception as e:
            logger.error(f"delete_stored_key error: {e}")
            return SessionResponse(success=False, error=str(e))

    return router
