"""MCP tools for relativity feature (requires einsteinpy)."""
import logging
from typing import Any, List, Optional, Union
from fastmcp import FastMCP
from mcp_service_kit.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.results import format_output, run_tool
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "create_predefined_metric"))
    async def create_predefined_metric(
        session_id: str,
        metric_name: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Create a predefined spacetime metric."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.create_predefined_metric(metric_name), output_format, timeout_seconds)

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
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Calculate a curvature tensor from a stored metric."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.calculate_tensor(metric_key, tensor_type, simplify_result=simplify), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "create_custom_metric"))
    async def create_custom_metric(
        session_id: str,
        components: List[List[str]],
        coord_symbols: List[str],
        config: str = "ll",
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Create a custom metric tensor from a 2D array of SymPy expression strings."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.create_custom_metric(components, coord_symbols, config), output_format, timeout_seconds)

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

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "create_tensor"))
    async def create_tensor(
        session_id: str,
        metric_key: str,
        components: Any,
        config: str,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Create a tensor from components in a stored metric's coordinates."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.create_tensor(metric_key, components, config), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "covariant_derivative"))
    async def covariant_derivative(
        session_id: str,
        tensor_key: str,
        metric_key: Optional[str] = None,
        simplify: bool = True,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Covariant derivative of a stored tensor; the derivative index is appended last."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.covariant_derivative(tensor_key, metric_key, simplify), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "tensor_divergence"))
    async def tensor_divergence(
        session_id: str,
        tensor_key: str,
        index: int = 0,
        metric_key: Optional[str] = None,
        simplify: bool = True,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Divergence of a stored tensor on one index, e.g. nabla^a G_ab."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.tensor_divergence(tensor_key, index, metric_key, simplify), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "contract_indices"))
    async def contract_indices(
        session_id: str,
        tensor_key: str,
        index_a: int,
        index_b: int,
        metric_key: Optional[str] = None,
        simplify: bool = True,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Contract two indices of a stored tensor."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.contract_indices(tensor_key, index_a, index_b, metric_key, simplify), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "raise_index"))
    async def raise_index(
        session_id: str,
        tensor_key: str,
        index: int,
        metric_key: Optional[str] = None,
        simplify: bool = True,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Raise one index of a stored tensor with the metric."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.raise_index(tensor_key, index, metric_key, simplify), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "lower_index"))
    async def lower_index(
        session_id: str,
        tensor_key: str,
        index: int,
        metric_key: Optional[str] = None,
        simplify: bool = True,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Lower one index of a stored tensor with the metric."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.lower_index(tensor_key, index, metric_key, simplify), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "tensor_component"))
    async def tensor_component(
        session_id: str,
        tensor_key: str,
        indices: List[Union[int, str]],
        simplify: bool = True,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Store one component of a tensor as an expression."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.tensor_component(tensor_key, indices, simplify), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "kretschmann_scalar"))
    async def kretschmann_scalar(
        session_id: str,
        metric_key: str,
        simplify: bool = True,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Kretschmann scalar R_abcd R^abcd of a stored metric."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.kretschmann_scalar(metric_key, simplify), output_format, timeout_seconds)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "killing_equation"))
    async def killing_equation(
        session_id: str,
        metric_key: str,
        vector: List[str],
        vector_config: str = "u",
        simplify: bool = True,
        timeout_seconds: Optional[float] = None,
        output_format: str = "structured",
    ) -> str:
        """Killing's equation nabla_(a xi_b) for a vector field on a stored metric."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return format_output(str(e), output_format)
        return run_tool(lambda: state.killing_equation(metric_key, vector, vector_config, simplify), output_format, timeout_seconds)
