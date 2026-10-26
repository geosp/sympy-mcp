"""MCP tools for verifying results."""
import logging
from fastmcp import FastMCP
from mcp_service_kit.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "check_equivalence"))
    async def check_equivalence(
        session_id: str,
        expr_a: str,
        expr_b: str,
        numeric_samples: int = 20,
    ) -> str:
        """Check whether two expressions are equal, symbolically and then numerically."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.check_equivalence(expr_a, expr_b, numeric_samples)
