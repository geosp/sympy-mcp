"""MCP tools for relativity feature (requires einsteinpy)."""
import logging
from typing import List
from fastmcp import FastMCP
from core.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "create_predefined_metric"))
    async def create_predefined_metric(
        session_id: str,
        metric_name: str,
    ) -> str:
        """Create a predefined spacetime metric."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.create_predefined_metric(metric_name)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "search_predefined_metrics"))
    async def search_predefined_metrics(
        session_id: str,
        query: str,
    ) -> str:
        """Search available predefined metrics by name."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.search_predefined_metrics(query)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "calculate_tensor"))
    async def calculate_tensor(
        session_id: str,
        metric_key: str,
        tensor_type: str,
        simplify: bool = True,
    ) -> str:
        """Calculate a curvature tensor from a stored metric."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.calculate_tensor(metric_key, tensor_type, simplify_result=simplify)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "create_custom_metric"))
    async def create_custom_metric(
        session_id: str,
        components: List[List[str]],
        coord_symbols: List[str],
        config: str = "ll",
    ) -> str:
        """Create a custom metric tensor from a 2D array of SymPy expression strings."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.create_custom_metric(components, coord_symbols, config)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "print_latex_tensor"))
    async def print_latex_tensor(
        session_id: str,
        tensor_key: str,
    ) -> str:
        """Return the LaTeX representation of a stored tensor or metric."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.print_latex_tensor(tensor_key)
