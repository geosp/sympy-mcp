"""
Configuration management for SymPy MCP Server.
"""

import os
from typing import Optional, List
from pydantic import BaseModel, Field

from core.config import (
    AuthentikConfig,
    BaseServerConfig,
)

try:
    from core.config import load_dotenv
    load_dotenv()
except ImportError:
    pass


class SymPyConfig(BaseModel):
    """SymPy-specific configuration."""
    session_ttl_seconds: int = Field(
        default=1800,
        description="Session TTL in seconds (default: 30 minutes)"
    )

    @classmethod
    def from_env(cls) -> "SymPyConfig":
        ttl = int(os.getenv("SYMPY_SESSION_TTL", "1800"))
        return cls(session_ttl_seconds=ttl)


class ServerConfig(BaseServerConfig):
    """Server configuration for SymPy MCP."""
    mcp_only: bool = Field(default=False)
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:8081"]
    )

    @classmethod
    def from_env(cls) -> "ServerConfig":
        config = super().from_env(env_prefix="MCP_")
        mcp_only = os.getenv("MCP_ONLY", "false").lower() == "true"
        auth_enabled = os.getenv("MCP_AUTH_ENABLED", "false").lower() == "true"
        config.mcp_only = mcp_only
        config.auth_enabled = auth_enabled
        cors_str = os.getenv("MCP_CORS_ORIGINS", "*")
        config.cors_origins = [o.strip() for o in cors_str.split(",")]
        return config


class AppConfig(BaseModel):
    """Complete application configuration."""
    server: ServerConfig
    sympy: SymPyConfig
    authentik: Optional[AuthentikConfig] = None

    @classmethod
    def from_env(cls) -> "AppConfig":
        server = ServerConfig.from_env()
        sympy_cfg = SymPyConfig.from_env()
        authentik = None
        if server.transport == "http" and server.auth_enabled:
            authentik = AuthentikConfig.from_env_optional()
        return cls(server=server, sympy=sympy_cfg, authentik=authentik)


_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = AppConfig.from_env()
    return _config


def load_config() -> AppConfig:
    global _config
    _config = AppConfig.from_env()
    return _config
