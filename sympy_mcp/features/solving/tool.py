"""MCP tools for solving equations."""
import logging
from typing import List
from fastmcp import FastMCP
from core.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError
from sympy_mcp.shared.enums import Domain

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "solve_algebraically"))
    async def solve_algebraically(
        session_id: str,
        expr_key: str,
        var_name: str,
        domain: str = "complex",
    ) -> str:
        """Solve a stored expression/equation algebraically for a given variable."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.solve_algebraically(expr_key, var_name, domain)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "solve_linear_system"))
    async def solve_linear_system(
        session_id: str,
        expr_keys: List[str],
        var_names: List[str],
        domain: str = "complex",
    ) -> str:
        """Solve a linear system of equations."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.solve_linear_system(expr_keys, var_names, domain)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "solve_nonlinear_system"))
    async def solve_nonlinear_system(
        session_id: str,
        expr_keys: List[str],
        var_names: List[str],
        domain: str = "complex",
    ) -> str:
        """Solve a nonlinear system of equations."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.solve_nonlinear_system(expr_keys, var_names, domain)
