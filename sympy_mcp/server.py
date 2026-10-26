"""
SymPy MCP Server - extends BaseMCPServer from mcp-service-kit.
"""

from mcp_service_kit import BaseMCPServer, create_main_with_modes

from sympy_mcp.config import AppConfig
from sympy_mcp.service import SymPyMCPService
from sympy_mcp.session import SymPySessionManager


class SymPyMCPServer(BaseMCPServer):
    """SymPy MCP Server - provides symbolic math via MCP."""

    @property
    def service_title(self) -> str:
        return "SymPy MCP Server"

    @property
    def service_description(self) -> str:
        return (
            "Provides symbolic mathematics capabilities via Model Context Protocol (MCP). "
            "Supports symbolic computation, calculus, linear algebra, solving equations, "
            "vector calculus, units, and general relativity tensors."
        )

    @property
    def service_version(self) -> str:
        return "0.1.0"


def create_service(config: AppConfig) -> SymPyMCPService:
    """Build the MCP service with a session manager configured from the app config."""
    session_manager = SymPySessionManager(ttl_seconds=config.sympy.session_ttl_seconds)
    return SymPyMCPService(session_manager)


main = create_main_with_modes(
    SymPyMCPServer,
    create_service,
    AppConfig,
    "sympy-mcp",
    "SymPy MCP Server - symbolic mathematics via Model Context Protocol",
)


if __name__ == "__main__":
    main()
