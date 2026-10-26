"""MCP tools for linear algebra operations."""
import logging
from typing import List, Optional
from fastmcp import FastMCP
from mcp_service_kit.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.results import format_output, run_tool
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "create_matrix"))
    async def create_matrix(
        session_id: str,
        matrix_data: List[List[str]],
        name: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Create a symbolic matrix from a 2D list of expression strings."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.create_matrix(matrix_data, name), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_determinant"))
    async def matrix_determinant(session_id: str, matrix_key: str, timeout_seconds: Optional[float] = None, output_format: str = "structured") -> str:
        """Calculate the determinant of a matrix."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_determinant(matrix_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_inverse"))
    async def matrix_inverse(session_id: str, matrix_key: str, timeout_seconds: Optional[float] = None, output_format: str = "structured") -> str:
        """Calculate the inverse of a matrix."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_inverse(matrix_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_eigenvalues"))
    async def matrix_eigenvalues(session_id: str, matrix_key: str, timeout_seconds: Optional[float] = None, output_format: str = "structured") -> str:
        """Calculate the eigenvalues of a matrix."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_eigenvalues(matrix_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_eigenvectors"))
    async def matrix_eigenvectors(session_id: str, matrix_key: str, timeout_seconds: Optional[float] = None, output_format: str = "structured") -> str:
        """Calculate the eigenvectors of a matrix."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_eigenvectors(matrix_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_multiply"))
    async def matrix_multiply(
        session_id: str,
        a_key: str,
        b_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Multiply two stored matrices (A times B)."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_multiply(a_key, b_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_power"))
    async def matrix_power(
        session_id: str,
        matrix_key: str,
        exponent: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Raise a square matrix to a power, which may be symbolic."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_power(matrix_key, exponent), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_exp"))
    async def matrix_exp(
        session_id: str,
        matrix_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Matrix exponential exp(A)."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_exp(matrix_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_trace"))
    async def matrix_trace(
        session_id: str,
        matrix_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Trace of a square matrix."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_trace(matrix_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_transpose"))
    async def matrix_transpose(
        session_id: str,
        matrix_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Transpose of a matrix."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_transpose(matrix_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_adjoint"))
    async def matrix_adjoint(
        session_id: str,
        matrix_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Conjugate transpose (Hermitian adjoint) of a matrix."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_adjoint(matrix_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_commutator"))
    async def matrix_commutator(
        session_id: str,
        a_key: str,
        b_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Commutator AB - BA of two square matrices."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_commutator(a_key, b_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_rank"))
    async def matrix_rank(
        session_id: str,
        matrix_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Rank of a matrix."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_rank(matrix_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "matrix_nullspace"))
    async def matrix_nullspace(
        session_id: str,
        matrix_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Basis of the nullspace of a matrix."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.matrix_nullspace(matrix_key), output_format, timeout_seconds)
