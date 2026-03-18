"""MCP tools for symbol introduction."""
import logging
from typing import List, Any
from fastmcp import FastMCP
from core.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError
from sympy_mcp.shared.enums import Assumption

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "intro"))
    async def intro(
        session_id: str,
        var_name: str,
        assumptions: List[str] = [],
        negative_assumptions: List[str] = [],
    ) -> str:
        """Introduce a symbolic variable with optional assumptions."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.intro(var_name, assumptions, negative_assumptions)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "intro_many"))
    async def intro_many(
        session_id: str,
        variables: List[Any],
    ) -> str:
        """Introduce multiple symbolic variables at once."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.intro_many(variables)
