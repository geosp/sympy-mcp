"""MCP tools for relativity feature (requires einsteinpy)."""
import logging
from typing import List
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def create_predefined_metric(
        session_id: str,
        metric_name: str,
    ) -> str:
        """Create a predefined spacetime metric."""
        state = session_manager.get_or_create_sync(session_id)
        return state.create_predefined_metric(metric_name)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def search_predefined_metrics(
        session_id: str,
        query: str,
    ) -> str:
        """Search available predefined metrics by name."""
        state = session_manager.get_or_create_sync(session_id)
        return state.search_predefined_metrics(query)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def calculate_tensor(
        session_id: str,
        metric_key: str,
        tensor_type: str,
        simplify: bool = True,
    ) -> str:
        """Calculate a curvature tensor from a stored metric."""
        state = session_manager.get_or_create_sync(session_id)
        return state.calculate_tensor(metric_key, tensor_type, simplify_result=simplify)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def create_custom_metric(
        session_id: str,
        components: List[List[str]],
        symbols: List[str],
        config: str = "ll",
    ) -> str:
        """Create a custom metric tensor from a 2D array of SymPy expression strings."""
        state = session_manager.get_or_create_sync(session_id)
        return state.create_custom_metric(components, symbols, config)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def print_latex_tensor(
        session_id: str,
        tensor_key: str,
    ) -> str:
        """Return the LaTeX representation of a stored tensor or metric."""
        state = session_manager.get_or_create_sync(session_id)
        return state.print_latex_tensor(tensor_key)
