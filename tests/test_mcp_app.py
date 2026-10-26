"""
Smoke tests for the assembled MCP app: tool discovery and an in-memory round trip.
"""

import asyncio
import json
import re
from pathlib import Path

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
    assert config.server.auth_enabled is False
    assert config.sympy.session_ttl_seconds == 1800


def test_session_ttl_env(monkeypatch):
    monkeypatch.setenv("SYMPY_SESSION_TTL", "60")
    assert AppConfig().sympy.session_ttl_seconds == 60


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
