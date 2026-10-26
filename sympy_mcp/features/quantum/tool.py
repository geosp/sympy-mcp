"""MCP tools for bosonic quantum operators."""
import logging
from typing import Optional
from fastmcp import FastMCP
from mcp_service_kit.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.results import format_output, run_tool
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "introduce_boson_operator"))
    async def introduce_boson_operator(
        session_id: str,
        name: str,
    ) -> str:
        """Introduce a bosonic annihilation operator a (its creation operator is Dagger(a))."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.introduce_boson_operator(name)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "normal_order_expression"))
    async def normal_order_expression(
        session_id: str,
        expr_key: str,
        mode: str = "symbol",
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Normal-order an operator expression."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.normal_order_expression(expr_key, mode), output_format, timeout_seconds)


    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "evaluate_commutator"))
    async def evaluate_commutator(
        session_id: str,
        expr_a: str,
        expr_b: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Evaluate the commutator [A, B] of two operator expressions."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.evaluate_commutator(expr_a, expr_b), output_format, timeout_seconds)


    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "quantum_apply"))
    async def quantum_apply(
        session_id: str,
        expr_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Apply operators to the kets and bras in an expression (qapply)."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.quantum_apply(expr_key), output_format, timeout_seconds)


    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "coherent_state_expectation"))
    async def coherent_state_expectation(
        session_id: str,
        expr_key: str,
        operator_name: str,
        alpha: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Expectation value of an operator expression in a coherent state."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.coherent_state_expectation(expr_key, operator_name, alpha), output_format, timeout_seconds)
