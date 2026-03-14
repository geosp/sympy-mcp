"""MCP tools for vector calculus operations."""
import logging
from typing import Optional, List
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def create_coordinate_system(
        session_id: str,
        name: str,
        coord_names: Optional[List[str]] = None,
    ) -> str:
        """Create a 3D coordinate system."""
        state = session_manager.get_or_create_sync(session_id)
        return state.create_coordinate_system(name, coord_names)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def create_vector_field(
        session_id: str,
        coord_sys_name: str,
        x: str,
        y: str,
        z: str,
    ) -> str:
        """Create a vector field in a coordinate system."""
        state = session_manager.get_or_create_sync(session_id)
        return state.create_vector_field(coord_sys_name, x, y, z)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def calculate_curl(session_id: str, vector_field_key: str) -> str:
        """Calculate the curl of a vector field."""
        state = session_manager.get_or_create_sync(session_id)
        return state.calculate_curl(vector_field_key)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def calculate_divergence(session_id: str, vector_field_key: str) -> str:
        """Calculate the divergence of a vector field."""
        state = session_manager.get_or_create_sync(session_id)
        return state.calculate_divergence(vector_field_key)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def calculate_gradient(session_id: str, scalar_field_key: str) -> str:
        """Calculate the gradient of a scalar field."""
        state = session_manager.get_or_create_sync(session_id)
        return state.calculate_gradient(scalar_field_key)
