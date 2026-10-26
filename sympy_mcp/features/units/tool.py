"""MCP tools for unit conversion operations."""
import logging
from typing import List, Optional
from fastmcp import FastMCP
from mcp_service_kit.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.results import format_output, run_tool
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError
from sympy_mcp.shared.enums import UnitSystem

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "convert_to_units"))
    async def convert_to_units(
        session_id: str,
        expr_key: str,
        target_units: List[str],
        unit_system: str = "SI",
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Convert an expression to specified target units."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        try:
            us = UnitSystem(unit_system)
        except ValueError:
            us = UnitSystem.SI
        return run_tool(lambda: state.convert_to_units(expr_key, target_units, us), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "quantity_simplify_units"))
    async def quantity_simplify_units(
        session_id: str,
        expr_key: str,
        unit_system: str = "SI",
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Simplify a quantity expression with units."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        try:
            us = UnitSystem(unit_system)
        except ValueError:
            us = UnitSystem.SI
        return run_tool(lambda: state.quantity_simplify_units(expr_key, us), output_format, timeout_seconds)
