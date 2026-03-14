"""MCP tools for functions and differential equations."""
import logging
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def introduce_function(
        session_id: str,
        func_name: str,
    ) -> str:
        """Introduce a symbolic function for use in differential equations."""
        state = session_manager.get_or_create_sync(session_id)
        return state.introduce_function(func_name)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def dsolve_ode(
        session_id: str,
        expr_key: str,
        func_name: str,
        hint: str = "default",
    ) -> str:
        """Solve an ordinary differential equation (ODE)."""
        state = session_manager.get_or_create_sync(session_id)
        return state.dsolve_ode(expr_key, func_name, hint)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def pdsolve_pde(
        session_id: str,
        expr_key: str,
        func_name: str,
        hint: str = "default",
    ) -> str:
        """Solve a partial differential equation (PDE)."""
        state = session_manager.get_or_create_sync(session_id)
        return state.pdsolve_pde(expr_key, func_name, hint)
