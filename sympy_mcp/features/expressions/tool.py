"""MCP tools for expressions."""
import logging
from typing import Dict, List, Optional
from fastmcp import FastMCP
from mcp_service_kit.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.results import format_output, run_tool
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "introduce_expression"))
    async def introduce_expression(
        session_id: str,
        expression: str,
        canonicalize: bool = True,
        name: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Parse and store a mathematical expression."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.introduce_expression(expression, canonicalize, name), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "introduce_equation"))
    async def introduce_equation(
        session_id: str,
        lhs_expression: str,
        rhs_expression: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Parse and store an equation (lhs = rhs)."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.introduce_equation(lhs_expression, rhs_expression), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "print_latex_expression"))
    async def print_latex_expression(
        session_id: str,
        expr_key: str,
        include_assumptions: bool = True,
    ) -> str:
        """Render a stored expression as a LaTeX string."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.print_latex_expression(expr_key, include_assumptions)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "substitute_expression"))
    async def substitute_expression(
        session_id: str,
        expr_key: str,
        var_name: str,
        replacement_expr_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Substitute a variable in an expression with another stored expression."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.substitute_expression(expr_key, var_name, replacement_expr_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "factor_expression"))
    async def factor_expression(session_id: str, expr_key: str, timeout_seconds: Optional[float] = None, output_format: str = "structured") -> str:
        """Factor an expression into irreducible components."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.factor_expression(expr_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "expand_expression"))
    async def expand_expression(session_id: str, expr_key: str, timeout_seconds: Optional[float] = None, output_format: str = "structured") -> str:
        """Expand a product or power into a sum of terms."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.expand_expression(expr_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "collect_expression"))
    async def collect_expression(session_id: str, expr_key: str, var_name: str, timeout_seconds: Optional[float] = None, output_format: str = "structured") -> str:
        """Collect and group terms by powers of a variable."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.collect_expression(expr_key, var_name), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "apart_expression"))
    async def apart_expression(session_id: str, expr_key: str, var_name: str, timeout_seconds: Optional[float] = None, output_format: str = "structured") -> str:
        """Decompose a rational expression into partial fractions."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.apart_expression(expr_key, var_name), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "evalf_expression"))
    async def evalf_expression(session_id: str, expr_key: str, n: int = 15, timeout_seconds: Optional[float] = None, output_format: str = "structured") -> str:
        """Numerically evaluate an expression to n significant digits."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.evalf_expression(expr_key, n), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "rewrite_expression"))
    async def rewrite_expression(
        session_id: str,
        expr_key: str,
        target: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Rewrite an expression in terms of another function, e.g. exp."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.rewrite_expression(expr_key, target), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "expand_log_expression"))
    async def expand_log_expression(
        session_id: str,
        expr_key: str,
        force: bool = False,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Expand logarithms of products and powers."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.expand_log_expression(expr_key, force), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "trigsimp_expression"))
    async def trigsimp_expression(
        session_id: str,
        expr_key: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Simplify using trigonometric identities."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.trigsimp_expression(expr_key), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "powsimp_expression"))
    async def powsimp_expression(
        session_id: str,
        expr_key: str,
        force: bool = False,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Combine powers with the same base or exponent."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.powsimp_expression(expr_key, force), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "nsimplify_expression"))
    async def nsimplify_expression(
        session_id: str,
        expr_key: str,
        constants: Optional[List[str]] = None,
        tolerance: Optional[float] = None,
        rational: bool = False,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Find a simple exact expression for a floating-point number."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.nsimplify_expression(expr_key, constants, tolerance, rational), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "substitute_values"))
    async def substitute_values(
        session_id: str,
        expr_key: str,
        substitutions: Dict[str, str],
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Substitute several symbols with values or expressions at once."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.substitute_values(expr_key, substitutions), output_format, timeout_seconds)
