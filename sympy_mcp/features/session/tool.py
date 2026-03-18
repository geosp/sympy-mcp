"""MCP tools for session management."""
import logging
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def reset_state(
        session_id: str,
    ) -> str:
        """Clears all expressions, symbols, functions, etc. from the session."""
        state = session_manager.get_or_create_sync(session_id)
        return state.reset_state()

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def list_session_state(
        session_id: str,
    ) -> str:
        """List all stored items in the session (symbols, expressions, functions, etc.)."""
        state = session_manager.get_or_create_sync(session_id)
        return state.list_session_state()

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def delete_stored_key(
        session_id: str,
        key: str,
    ) -> str:
        """Delete a stored item by key, searching all stores."""
        state = session_manager.get_or_create_sync(session_id)
        return state.delete_stored_key(key)
