"""MCP tools for expressions."""
import logging
from typing import Optional
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def introduce_expression(
        session_id: str,
        expr_str: str,
        canonicalize: bool = True,
        name: Optional[str] = None,
    ) -> str:
        """Parse and store a mathematical expression."""
        state = session_manager.get_or_create_sync(session_id)
        return state.introduce_expression(expr_str, canonicalize, name)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def introduce_equation(
        session_id: str,
        lhs_str: str,
        rhs_str: str,
    ) -> str:
        """Parse and store an equation (lhs = rhs)."""
        state = session_manager.get_or_create_sync(session_id)
        return state.introduce_equation(lhs_str, rhs_str)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def print_latex_expression(
        session_id: str,
        expr_key: str,
    ) -> str:
        """Render a stored expression as a LaTeX string."""
        state = session_manager.get_or_create_sync(session_id)
        return state.print_latex_expression(expr_key)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def substitute_expression(
        session_id: str,
        expr_key: str,
        var_name: str,
        replacement_expr_key: str,
    ) -> str:
        """Substitute a variable in an expression with another stored expression."""
        state = session_manager.get_or_create_sync(session_id)
        return state.substitute_expression(expr_key, var_name, replacement_expr_key)
