"""MCP tools for calculus operations."""
import logging
from typing import Optional
from fastmcp import FastMCP
from mcp_service_kit.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.results import format_output
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "simplify_expression"))
    async def simplify_expression(session_id: str, expr_key: str, output_format: str = "structured") -> str:
        """Simplify a symbolic expression."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.simplify_expression(expr_key), output_format)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "integrate_expression"))
    async def integrate_expression(
        session_id: str,
        expr_key: str,
        var_name: str,
        lower_bound: Optional[str] = None,
        upper_bound: Optional[str] = None,
        output_format: str = "structured",
    ) -> str:
        """Integrate an expression with respect to a variable."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.integrate_expression(expr_key, var_name, lower_bound, upper_bound), output_format)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "differentiate_expression"))
    async def differentiate_expression(
        session_id: str,
        expr_key: str,
        var_name: str,
        order: int = 1,
        output_format: str = "structured",
    ) -> str:
        """Differentiate an expression with respect to a variable."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.differentiate_expression(expr_key, var_name, order), output_format)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "limit_expression"))
    async def limit_expression(
        session_id: str,
        expr_key: str,
        var_name: str,
        point: str,
        direction: str = "+",
        output_format: str = "structured",
    ) -> str:
        """Compute the limit of an expression as a variable approaches a point."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.limit_expression(expr_key, var_name, point, direction), output_format)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "series_expansion"))
    async def series_expansion(
        session_id: str,
        expr_key: str,
        var_name: str,
        point: str = "0",
        order: int = 6,
        output_format: str = "structured",
    ) -> str:
        """Compute the Taylor/Maclaurin series expansion of an expression."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        raw = state.series_expansion(expr_key, var_name, point, order)
        if output_format != "legacy" or raw.startswith("Error"):
            return format_output(raw, output_format)
        key, display = raw.split("|||", 1)
        return f"{display} [stored as {key}]"

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "summation_expression"))
    async def summation_expression(
        session_id: str,
        expr_key: str,
        var_name: str,
        lower_bound: str,
        upper_bound: str,
        output_format: str = "structured",
    ) -> str:
        """Compute a symbolic summation over a variable range."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.summation_expression(expr_key, var_name, lower_bound, upper_bound), output_format)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "fourier_transform"))
    async def fourier_transform(
        session_id: str,
        expr_key: str,
        var_name: str,
        k_name: str,
        output_format: str = "structured",
    ) -> str:
        """Fourier transform F(k) = integral of f(x) exp(-2 pi i x k) dx."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.fourier_transform(expr_key, var_name, k_name), output_format)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "inverse_fourier_transform"))
    async def inverse_fourier_transform(
        session_id: str,
        expr_key: str,
        k_name: str,
        var_name: str,
        output_format: str = "structured",
    ) -> str:
        """Inverse Fourier transform (SymPy convention)."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.inverse_fourier_transform(expr_key, k_name, var_name), output_format)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "laplace_transform"))
    async def laplace_transform(
        session_id: str,
        expr_key: str,
        t_name: str,
        s_name: str,
        output_format: str = "structured",
    ) -> str:
        """Laplace transform F(s) = integral from 0 to oo of f(t) exp(-s t) dt."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.laplace_transform(expr_key, t_name, s_name), output_format)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "inverse_laplace_transform"))
    async def inverse_laplace_transform(
        session_id: str,
        expr_key: str,
        s_name: str,
        t_name: str,
        output_format: str = "structured",
    ) -> str:
        """Inverse Laplace transform."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.inverse_laplace_transform(expr_key, s_name, t_name), output_format)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "numeric_integrate"))
    async def numeric_integrate(
        session_id: str,
        expr_key: str,
        var_name: str,
        lower_bound: str,
        upper_bound: str,
        precision: int = 15,
        output_format: str = "structured",
    ) -> str:
        """Numeric definite integral with mpmath quadrature at a chosen precision."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return format_output(state.numeric_integrate(expr_key, var_name, lower_bound, upper_bound, precision), output_format)
