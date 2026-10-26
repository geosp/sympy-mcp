"""
Configuration management for SymPy MCP Server.
"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from mcp_service_kit import BaseServerConfig


class SymPyConfig(BaseSettings):
    """SymPy-specific configuration. Environment variables: SYMPY_SESSION_TTL, SYMPY_TIMEOUT."""
    model_config = SettingsConfigDict(extra="ignore")

    session_ttl_seconds: int = Field(
        default=1800,
        validation_alias="SYMPY_SESSION_TTL",
        description="Session TTL in seconds (default: 30 minutes)"
    )
    timeout_seconds: float = Field(
        default=30.0,
        ge=0,
        validation_alias="SYMPY_TIMEOUT",
        description="Default time limit per computation in seconds (0: no limit)"
    )


class SymPyServerConfig(BaseServerConfig):
    """Server configuration for SymPy MCP: port 8081, auth off (handled at the gateway)."""
    port: int = Field(default=8081, ge=1, le=65535, description="Port number for HTTP server")
    auth_enabled: bool = Field(
        default=False,
        description="Whether authentication is enabled (when transport=http)"
    )


class AppConfig(BaseModel):
    """Complete application configuration."""
    server: SymPyServerConfig = Field(default_factory=SymPyServerConfig)
    sympy: SymPyConfig = Field(default_factory=SymPyConfig)
