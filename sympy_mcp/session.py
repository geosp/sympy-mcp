"""
SymPy Session Manager — pure in-memory session store.

Each session gets its own SymPyState instance. Sessions are created on demand
by get_or_create_sync() (used by MCP tools) or explicitly via create() (REST API).
SymPy objects cannot be serialized, so state lives entirely in-process.
"""

import logging
from typing import Dict, List, Optional
from uuid import uuid4

from sympy_mcp.state import SymPyState

logger = logging.getLogger(__name__)


class SymPySessionManager:
    """Pure in-memory session manager. Each session_id maps to a SymPyState."""

    def __init__(self, ttl_seconds: int = 1800):
        self._ttl = ttl_seconds
        self._store: Dict[str, SymPyState] = {}

    async def create(self) -> str:
        """Generate a UUID session, create a fresh SymPyState, return the session_id."""
        session_id = str(uuid4())
        self._store[session_id] = SymPyState()
        logger.info(f"Created session: {session_id}")
        return session_id

    async def get(self, session_id: str) -> Optional[SymPyState]:
        """Return the SymPyState for a session, or None if not found."""
        return self._store.get(session_id)

    def get_or_create_sync(self, session_id: str) -> SymPyState:
        """Synchronous — used by MCP tools. Creates state on first access."""
        if session_id not in self._store:
            logger.info(f"Creating in-memory state for session: {session_id}")
            self._store[session_id] = SymPyState()
        return self._store[session_id]

    async def destroy(self, session_id: str) -> None:
        """Remove a session and its state."""
        self._store.pop(session_id, None)
        logger.info(f"Destroyed session: {session_id}")

    async def list_sessions(self) -> List[dict]:
        """List all active session IDs."""
        return [{"session_id": sid} for sid in self._store.keys()]

    def session_count(self) -> int:
        return len(self._store)
