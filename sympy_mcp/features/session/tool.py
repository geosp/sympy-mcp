"""MCP tools for session management."""
import logging
from fastmcp import FastMCP
from mcp_service_kit.utils import inject_docstring
from sympy_mcp.utils import load_tool_instruction
from sympy_mcp.session import SymPySessionManager, SessionNotFoundError
from sympy_mcp import transcript

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, session_manager: SymPySessionManager) -> None:
    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "create_session"))
    async def create_session(
        description: str,
    ) -> str:
        """Create a new session. The server generates a unique session_id. Returns JSON with session_id, description, and created_at."""
        import json
        result = await session_manager.create(description)
        return json.dumps(result)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "list_sessions"))
    async def list_sessions() -> str:
        """List all active sessions with their descriptions and timestamps."""
        import json
        sessions = await session_manager.list_sessions()
        return json.dumps({"sessions": sessions, "count": len(sessions)}, indent=2)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "reset_state"))
    async def reset_state(
        session_id: str,
    ) -> str:
        """Clears all expressions, symbols, functions, etc. from the session."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.reset_state()

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "list_session_state"))
    async def list_session_state(
        session_id: str,
    ) -> str:
        """List all stored items in the session (symbols, expressions, functions, etc.)."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.list_session_state()

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "delete_stored_key"))
    async def delete_stored_key(
        session_id: str,
        key: str,
    ) -> str:
        """Delete a stored item by key, searching all stores."""
        try:
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        return state.delete_stored_key(key)

    @mcp.tool()
    @inject_docstring(lambda: load_tool_instruction("instructions.md", __file__, "export_session"))
    async def export_session(
        session_id: str,
        format: str = "python",
    ) -> str:
        """Export the session's tool calls as a replayable Python script or a JSON transcript."""
        import json
        try:
            info = session_manager.info(session_id)
            state = session_manager.get_sync(session_id)
        except SessionNotFoundError as e:
            return str(e)
        if format not in transcript.EXPORT_FORMATS:
            return f"Error: Unknown format '{format}'. Use one of: {', '.join(transcript.EXPORT_FORMATS)}."
        document = transcript.export_document(info, list(state.transcript))
        if format == "json":
            return json.dumps(document, indent=2)
        return transcript.export_python(document)
