"""MCP tools for functions and differential equations."""
import logging
from typing import List
from fastmcp import FastMCP
from core.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "introduce_function"))
    async def introduce_function(
        session_id: str,
        func_name: str,
    ) -> str:
        """Introduce a symbolic function for use in differential equations."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.introduce_function(func_name)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "dsolve_ode"))
    async def dsolve_ode(
        session_id: str,
        expr_key: str,
        func_name: str,
        hint: str = "default",
    ) -> str:
        """Solve an ordinary differential equation (ODE)."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.dsolve_ode(expr_key, func_name, hint)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "dsolve_system"))
    async def dsolve_system(
        session_id: str,
        expr_keys: List[str],
        func_names: List[str],
    ) -> str:
        """Solve a coupled system of ordinary differential equations."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.dsolve_system(expr_keys, func_names)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "pdsolve_pde"))
    async def pdsolve_pde(
        session_id: str,
        expr_key: str,
        func_name: str,
        hint: str = "default",
    ) -> str:
        """Solve a partial differential equation (PDE)."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.pdsolve_pde(expr_key, func_name, hint)
