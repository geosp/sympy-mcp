"""
SymPy MCP Service wrapper with automatic feature discovery.
"""

import logging
import importlib
import pkgutil
from pathlib import Path

from core.server import BaseService
from fastmcp import FastMCP

from sympy_mcp.session import SymPySessionManager

logger = logging.getLogger(__name__)


class SymPyMCPService(BaseService):
    """MCP Service wrapper - holds session manager, auto-discovers feature tools."""

    def __init__(self, session_manager: SymPySessionManager):
        self.session_manager = session_manager

    def initialize(self) -> None:
        logger.info("SymPyMCPService initialized")

    def get_service_name(self) -> str:
        return "sympy"

    def register_mcp_tools(self, mcp: FastMCP) -> None:
        logger.info("Discovering and registering MCP tools from features...")
        features_package = "sympy_mcp.features"
        features_path = Path(__file__).parent / "features"

        if not features_path.exists():
            logger.warning(f"Features directory not found: {features_path}")
            return

        feature_count = 0
        for _, feature_name, is_pkg in pkgutil.iter_modules([str(features_path)]):
            if not is_pkg:
                continue
            try:
                tool_module = importlib.import_module(f"{features_package}.{feature_name}.tool")
                if hasattr(tool_module, "register_tool"):
                    tool_module.register_tool(mcp, self.session_manager)
                    feature_count += 1
                    logger.info(f"Registered tools from feature: {feature_name}")
                else:
                    logger.warning(f"Feature '{feature_name}' has no register_tool() function")
            except ModuleNotFoundError:
                logger.debug(f"Feature '{feature_name}' has no tool.py, skipping")
            except Exception as e:
                logger.error(
                    f"Error registering tools from feature '{feature_name}': {e}",
                    exc_info=True,
                )

        logger.info(f"Registered MCP tools from {feature_count} features")

    def cleanup(self) -> None:
        logger.info("SymPyMCPService cleanup")
