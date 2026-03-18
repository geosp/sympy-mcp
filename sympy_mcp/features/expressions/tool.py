"""MCP tools for expressions."""
import logging
from typing import Optional
from fastmcp import FastMCP
from core.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "introduce_expression"))
    async def introduce_expression(
        session_id: str,
        expression: str,
        canonicalize: bool = True,
        name: Optional[str] = None,
    ) -> str:
        """Parse and store a mathematical expression."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.introduce_expression(expression, canonicalize, name)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "introduce_equation"))
    async def introduce_equation(
        session_id: str,
        lhs_expression: str,
        rhs_expression: str,
    ) -> str:
        """Parse and store an equation (lhs = rhs)."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.introduce_equation(lhs_expression, rhs_expression)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "print_latex_expression"))
    async def print_latex_expression(
        session_id: str,
        expr_key: str,
    ) -> str:
        """Render a stored expression as a LaTeX string."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.print_latex_expression(expr_key)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "substitute_expression"))
    async def substitute_expression(
        session_id: str,
        expr_key: str,
        var_name: str,
        replacement_expr_key: str,
    ) -> str:
        """Substitute a variable in an expression with another stored expression."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.substitute_expression(expr_key, var_name, replacement_expr_key)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "factor_expression"))
    async def factor_expression(session_id: str, expr_key: str) -> str:
        """Factor an expression into irreducible components."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.factor_expression(expr_key)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "expand_expression"))
    async def expand_expression(session_id: str, expr_key: str) -> str:
        """Expand a product or power into a sum of terms."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.expand_expression(expr_key)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "collect_expression"))
    async def collect_expression(session_id: str, expr_key: str, var_name: str) -> str:
        """Collect and group terms by powers of a variable."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.collect_expression(expr_key, var_name)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "apart_expression"))
    async def apart_expression(session_id: str, expr_key: str, var_name: str) -> str:
        """Decompose a rational expression into partial fractions."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.apart_expression(expr_key, var_name)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "evalf_expression"))
    async def evalf_expression(session_id: str, expr_key: str, n: int = 15) -> str:
        """Numerically evaluate an expression to n significant digits."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.evalf_expression(expr_key, n)
