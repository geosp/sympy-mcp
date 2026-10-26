"""SymPy MCP Server package."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sympy-mcp")
except PackageNotFoundError:  # running from a source tree without install
    __version__ = "0.0.0"
