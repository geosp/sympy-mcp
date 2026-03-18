"""MCP tools for vector calculus operations."""
import logging
from typing import Optional, List
from fastmcp import FastMCP
from core.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "create_coordinate_system"))
    async def create_coordinate_system(
        session_id: str,
        coord_sys_name: str,
        coord_names: Optional[List[str]] = None,
    ) -> str:
        """Create a 3D coordinate system."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.create_coordinate_system(coord_sys_name, coord_names)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "create_vector_field"))
    async def create_vector_field(
        session_id: str,
        coord_sys_name: str,
        comp_x: str,
        comp_y: str,
        comp_z: str,
    ) -> str:
        """Create a vector field in a coordinate system."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.create_vector_field(coord_sys_name, comp_x, comp_y, comp_z)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "calculate_curl"))
    async def calculate_curl(session_id: str, vector_field_key: str) -> str:
        """Calculate the curl of a vector field."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.calculate_curl(vector_field_key)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "calculate_divergence"))
    async def calculate_divergence(session_id: str, vector_field_key: str) -> str:
        """Calculate the divergence of a vector field."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.calculate_divergence(vector_field_key)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "calculate_gradient"))
    async def calculate_gradient(session_id: str, scalar_field_key: str) -> str:
        """Calculate the gradient of a scalar field."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.calculate_gradient(scalar_field_key)
