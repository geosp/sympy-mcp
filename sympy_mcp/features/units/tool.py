"""MCP tools for unit conversion operations."""
import logging
from typing import List, Optional
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.shared.enums import UnitSystem

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def convert_to_units(
        session_id: str,
        expr_key: str,
        target_units: List[str],
        unit_system: str = "SI",
    ) -> str:
        """Convert an expression to specified target units."""
        state = session_manager.get_or_create_sync(session_id)
        try:
            us = UnitSystem(unit_system)
        except ValueError:
            us = UnitSystem.SI
        return state.convert_to_units(expr_key, target_units, us)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def quantity_simplify_units(
        session_id: str,
        expr_key: str,
        unit_system: str = "SI",
    ) -> str:
        """Simplify a quantity expression with units."""
        state = session_manager.get_or_create_sync(session_id)
        try:
            us = UnitSystem(unit_system)
        except ValueError:
            us = UnitSystem.SI
        return state.quantity_simplify_units(expr_key, us)
