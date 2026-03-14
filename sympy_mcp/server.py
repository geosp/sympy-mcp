"""
SymPy MCP Server - extends BaseMCPServer from mcp-weather core.
"""

import logging
import sys
import importlib
import pkgutil
from pathlib import Path
from typing import List, Optional, Any

from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse

from core.server import BaseMCPServer

from sympy_mcp.config import AppConfig, get_config, load_config


class _WildcardOriginList(list):
    """List subclass that matches any origin when '*' is present."""
    def __contains__(self, item: object) -> bool:
        return list.__contains__(self, "*") or list.__contains__(self, item)
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.service import SymPyMCPService

logger = logging.getLogger(__name__)


class SymPyMCPServer(BaseMCPServer):
    """SymPy MCP Server - provides symbolic math via MCP and REST."""

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

    @property
    def allowed_cors_origins(self) -> List[str]:
        origins = (
            self.config.server.cors_origins
            if hasattr(self.config, "server") and hasattr(self.config.server, "cors_origins")
            else ["http://localhost:3000", "http://localhost:8080", "http://localhost:8081"]
        )
        return _WildcardOriginList(origins)

    def create_auth_provider(self) -> Optional[Any]:
        auth_enabled = self.get_config("server.auth_enabled", self.get_config("auth_enabled", False))
        if not auth_enabled:
            logger.info("Authentication is disabled")
            return None
        if not self.config.authentik:
            logger.warning("Authentication enabled but no Authentik config found")
            return None
        from core.auth_mcp import create_auth_provider
        return create_auth_provider("sympy")

    def create_router(self) -> APIRouter:
        router = APIRouter()
        session_manager: SymPySessionManager = self.service.session_manager

        @router.get("/health")
        async def health():
            return {
                "status": "ok",
                "service": "sympy",
                "version": self.service_version,
                "active_sessions": session_manager.session_count(),
            }

        @router.post("/sessions")
        async def create_session():
            session_id = await session_manager.create()
            return {"session_id": session_id}

        @router.delete("/sessions/{session_id}")
        async def destroy_session(session_id: str):
            await session_manager.destroy(session_id)
            return {"status": "deleted", "session_id": session_id}

        @router.get("/sessions")
        async def list_sessions():
            sessions = await session_manager.list_sessions()
            return {"sessions": sessions, "count": len(sessions)}

        # Auto-discover feature routes
        features_package = "sympy_mcp.features"
        features_path = Path(__file__).parent / "features"
        if features_path.exists():
            for _, feature_name, is_pkg in pkgutil.iter_modules([str(features_path)]):
                if not is_pkg:
                    continue
                try:
                    routes_module = importlib.import_module(
                        f"{features_package}.{feature_name}.routes"
                    )
                    if hasattr(routes_module, "create_router"):
                        feature_router = routes_module.create_router(session_manager)
                        router.include_router(feature_router)
                        logger.info(f"Included routes from feature: {feature_name}")
                except ModuleNotFoundError:
                    logger.debug(f"Feature '{feature_name}' has no routes.py, skipping")
                except Exception as e:
                    logger.error(f"Error including routes from feature '{feature_name}': {e}")

        return router

    def register_exception_handlers(self, app: FastAPI) -> None:
        @app.exception_handler(ValueError)
        async def value_error_handler(request: Request, exc: ValueError):
            return JSONResponse(
                status_code=400,
                content={"error": "Validation Error", "detail": str(exc)},
            )

        @app.exception_handler(KeyError)
        async def key_error_handler(request: Request, exc: KeyError):
            return JSONResponse(
                status_code=404,
                content={"error": "Not Found", "detail": f"Key not found: {exc}"},
            )

        @app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "detail": str(exc)},
            )


def main():
    """Main entry point for sympy-mcp server."""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="SymPy MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mode", choices=["stdio", "mcp", "rest"], default="stdio")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--no-auth", action="store_true")
    args = parser.parse_args()

    if args.mode == "stdio":
        os.environ["MCP_TRANSPORT"] = "stdio"
        os.environ["MCP_ONLY"] = "true"
    elif args.mode == "mcp":
        os.environ["MCP_TRANSPORT"] = "http"
        os.environ["MCP_ONLY"] = "true"
        os.environ["MCP_HOST"] = args.host
        os.environ["MCP_PORT"] = str(args.port)
        if args.no_auth:
            os.environ["AUTH_ENABLED"] = "false"
            os.environ["MCP_CORS_ORIGINS"] = "*"
    elif args.mode == "rest":
        os.environ["MCP_TRANSPORT"] = "http"
        os.environ["MCP_ONLY"] = "false"
        os.environ["MCP_HOST"] = args.host
        os.environ["MCP_PORT"] = str(args.port)
        if args.no_auth:
            os.environ["AUTH_ENABLED"] = "false"
            os.environ["MCP_CORS_ORIGINS"] = "*"

    try:
        config = load_config()
        session_manager = SymPySessionManager(ttl_seconds=config.sympy.session_ttl_seconds)
        mcp_service = SymPyMCPService(session_manager)
        server = SymPyMCPServer(config, mcp_service)
        server.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
