"""MCP tools for linear algebra operations."""
import logging
from typing import List, Optional
from fastmcp import FastMCP
from core.utils import inject_docstring, load_instruction
from sympy_mcp.session import SymPySessionManager

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def create_matrix(
        session_id: str,
        matrix_data: List[List[str]],
        name: Optional[str] = None,
    ) -> str:
        """Create a symbolic matrix from a 2D list of expression strings."""
        state = session_manager.get_or_create_sync(session_id)
        return state.create_matrix(matrix_data, name)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def matrix_determinant(session_id: str, matrix_key: str) -> str:
        """Calculate the determinant of a matrix."""
        state = session_manager.get_or_create_sync(session_id)
        return state.matrix_determinant(matrix_key)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def matrix_inverse(session_id: str, matrix_key: str) -> str:
        """Calculate the inverse of a matrix."""
        state = session_manager.get_or_create_sync(session_id)
        return state.matrix_inverse(matrix_key)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def matrix_eigenvalues(session_id: str, matrix_key: str) -> str:
        """Calculate the eigenvalues of a matrix."""
        state = session_manager.get_or_create_sync(session_id)
        return state.matrix_eigenvalues(matrix_key)

    @mcp.tool()
    @inject_docstring(lambda: load_instruction("instructions.md", __file__))
    async def matrix_eigenvectors(session_id: str, matrix_key: str) -> str:
        """Calculate the eigenvectors of a matrix."""
        state = session_manager.get_or_create_sync(session_id)
        return state.matrix_eigenvectors(matrix_key)
