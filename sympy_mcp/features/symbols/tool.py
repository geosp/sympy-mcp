"""MCP tools for symbol introduction."""
import logging
from typing import List, Any
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.shared.enums import Assumption

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def intro(
        session_id: str,
        var_name: str,
        pos_assumptions: List[str] = [],
        neg_assumptions: List[str] = [],
    ) -> str:
        """Introduce a symbolic variable with optional assumptions."""
        state = session_manager.get_or_create_sync(session_id)
        return state.intro(var_name, pos_assumptions, neg_assumptions)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def intro_many(
        session_id: str,
        variables: List[Any],
    ) -> str:
        """Introduce multiple symbolic variables at once."""
        state = session_manager.get_or_create_sync(session_id)
        return state.intro_many(variables)
