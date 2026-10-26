"""
Smoke tests for the assembled MCP app: tool discovery and an in-memory round trip.
"""

import asyncio
import json
import re
from pathlib import Path

import pytest
from fastmcp import Client

from sympy_mcp.config import AppConfig
from sympy_mcp.server import SymPyMCPServer, create_service

FEATURES_PATH = Path(__file__).parent.parent / "sympy_mcp" / "features"


def _create_mcp():
    config = AppConfig()
    return SymPyMCPServer(config.server, create_service(config)).create_mcp_app()


def _expected_tool_count() -> int:
    return sum(
        len(re.findall(r"@mcp\.tool\(", path.read_text()))
        for path in FEATURES_PATH.glob("*/tool.py")
    )


def test_config_defaults():
    config = AppConfig()
    assert config.server.port == 8081
    assert config.server.host == "0.0.0.0"  # deliberate: listen on all interfaces
    assert config.server.auth_enabled is False
    assert config.sympy.session_ttl_seconds == 1800


def test_session_ttl_env(monkeypatch):
    monkeypatch.setenv("SYMPY_SESSION_TTL", "60")
    assert AppConfig().sympy.session_ttl_seconds == 60


def test_http_starts_without_auth_by_default(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    config = AppConfig()
    assert config.server.transport == "http"
    assert _create_mcp_for(config) is not None


def test_http_with_auth_enabled_fails_closed(monkeypatch):
    # sympy-mcp has no auth provider, so mcp-service-kit >= 0.2 refuses to serve HTTP
    # with auth enabled instead of silently serving without it
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    monkeypatch.setenv("MCP_AUTH_ENABLED", "true")
    with pytest.raises(ValueError):
        _create_mcp_for(AppConfig())


def _create_mcp_for(config):
    return SymPyMCPServer(config.server, create_service(config)).create_mcp_app()


def test_all_feature_tools_registered():
    async def run():
        async with Client(_create_mcp()) as client:
            return await client.list_tools()

    tools = asyncio.run(run())
    assert len(tools) == _expected_tool_count()
    assert all(tool.description for tool in tools)


def test_session_round_trip():
    async def run():
        async with Client(_create_mcp()) as client:
            created = await client.call_tool("create_session", {"description": "smoke"})
            session_id = json.loads(created.data)["session_id"]
            return await client.call_tool("intro", {"session_id": session_id, "var_name": "x"})

    result = asyncio.run(run())
    assert result.data == "x"


@pytest.mark.parametrize(
    "env, argv, expected",
    [
        ({}, [], "stdio"),
        ({"MCP_TRANSPORT": "http"}, [], "http"),  # honoured since mcp-service-kit 0.2.1
        ({"MCP_TRANSPORT": "http"}, ["--mode", "stdio"], "stdio"),  # --mode wins
        ({}, ["--mode", "http"], "http"),
    ],
)
def test_main_selects_transport(monkeypatch, env, argv, expected):
    from sympy_mcp import server

    # main() writes these into os.environ; setenv first so monkeypatch restores them afterwards
    for name in ("MCP_TRANSPORT", "MCP_HOST", "MCP_PORT", "MCP_AUTH_ENABLED", "LOG_LEVEL"):
        monkeypatch.setenv(name, "")
        monkeypatch.delenv(name)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr("sys.argv", ["sympy-mcp", *argv])
    started = []
    monkeypatch.setattr(server.SymPyMCPServer, "run", lambda self: started.append(self.config.transport))
    server.main()
    assert started == [expected]


def test_version_has_a_single_source():
    from importlib.metadata import version

    import sympy_mcp

    config = AppConfig()
    server = SymPyMCPServer(config.server, create_service(config))
    assert server.service_version == sympy_mcp.__version__ == version("sympy-mcp")
    assert sympy_mcp.__version__ != "0.1.0"  # now derived from git tags (>= v1.0.9)


def test_initialize_reports_the_package_version():
    import sympy_mcp

    async def run():
        async with Client(_create_mcp()) as client:
            return client.server_info.version

    assert asyncio.run(run()) == sympy_mcp.__version__
