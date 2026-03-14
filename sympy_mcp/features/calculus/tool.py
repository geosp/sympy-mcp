"""MCP tools for calculus operations."""
import logging
from typing import Optional
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def simplify_expression(session_id: str, expr_key: str) -> str:
        """Simplify a symbolic expression."""
        state = session_manager.get_or_create_sync(session_id)
        return state.simplify_expression(expr_key)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def integrate_expression(
        session_id: str,
        expr_key: str,
        var_name: str,
        lower: Optional[str] = None,
        upper: Optional[str] = None,
    ) -> str:
        """Integrate an expression with respect to a variable."""
        state = session_manager.get_or_create_sync(session_id)
        return state.integrate_expression(expr_key, var_name, lower, upper)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def differentiate_expression(
        session_id: str,
        expr_key: str,
        var_name: str,
        order: int = 1,
    ) -> str:
        """Differentiate an expression with respect to a variable."""
        state = session_manager.get_or_create_sync(session_id)
        return state.differentiate_expression(expr_key, var_name, order)
