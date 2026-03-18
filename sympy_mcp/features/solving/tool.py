"""MCP tools for solving equations."""
import logging
from typing import List
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.shared.enums import Domain

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def solve_algebraically(
        session_id: str,
        expr_key: str,
        solve_for_var_name: str,
        domain: str = "complex",
    ) -> str:
        """Solve a stored expression/equation algebraically for a given variable."""
        state = session_manager.get_or_create_sync(session_id)
        return state.solve_algebraically(expr_key, solve_for_var_name, domain)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def solve_linear_system(
        session_id: str,
        expr_keys: List[str],
        var_names: List[str],
        domain: str = "complex",
    ) -> str:
        """Solve a linear system of equations."""
        state = session_manager.get_or_create_sync(session_id)
        return state.solve_linear_system(expr_keys, var_names, domain)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def solve_nonlinear_system(
        session_id: str,
        expr_keys: List[str],
        var_names: List[str],
        domain: str = "complex",
    ) -> str:
        """Solve a nonlinear system of equations."""
        state = session_manager.get_or_create_sync(session_id)
        return state.solve_nonlinear_system(expr_keys, var_names, domain)
