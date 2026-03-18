"""
SymPy Session Manager — pure in-memory session store.

Each session gets its own SymPyState instance. Sessions must be created
explicitly via create() before use. All other tools require a valid session_id
returned by create(). SymPy objects cannot be serialized, so state lives
entirely in-process.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from sympy_mcp.state import SymPyState

logger = logging.getLogger(__name__)


@dataclass
class SessionEntry:
    """Metadata + state for a single session."""
    state: SymPyState = field(default_factory=SymPyState)
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SessionNotFoundError(Exception):
    """Raised when a session_id does not exist in the store."""


class SymPySessionManager:
    """Pure in-memory session manager. Each session_id maps to a SessionEntry."""

    def __init__(self, ttl_seconds: int = 1800):
        self._ttl = ttl_seconds
        self._store: Dict[str, SessionEntry] = {}

    async def create(self, description: str = "") -> dict:
        """Create a new session with a server-generated UUID.

        Returns a dict with session_id, description, and created_at.
        """
        session_id = str(uuid4())
        now = datetime.now(timezone.utc)
        self._store[session_id] = SessionEntry(
            state=SymPyState(),
            description=description,
            created_at=now,
            last_accessed=now,
        )
        logger.info(f"Created session: {session_id} — {description!r}")
        return {
            "session_id": session_id,
            "description": description,
            "created_at": now.isoformat(),
        }

    def get_sync(self, session_id: str) -> SymPyState:
        """Return the SymPyState for a session (synchronous).

        Raises SessionNotFoundError if the session_id does not exist.
        """
        entry = self._store.get(session_id)
        if entry is None:
            raise SessionNotFoundError(
                f"Session '{session_id}' not found. "
                f"Call create_session(description=\"...\") first to start a new session."
            )
        entry.last_accessed = datetime.now(timezone.utc)
        return entry.state

    async def get(self, session_id: str) -> Optional[SymPyState]:
        """Return the SymPyState for a session, or None if not found."""
        entry = self._store.get(session_id)
        if entry is None:
            return None
        entry.last_accessed = datetime.now(timezone.utc)
        return entry.state

    async def destroy(self, session_id: str) -> None:
        """Remove a session and its state."""
        self._store.pop(session_id, None)
        logger.info(f"Destroyed session: {session_id}")

    async def list_sessions(self) -> List[dict]:
        """List all active sessions with metadata."""
        return [
            {
                "session_id": sid,
                "description": entry.description,
                "created_at": entry.created_at.isoformat(),
                "last_accessed": entry.last_accessed.isoformat(),
            }
            for sid, entry in self._store.items()
        ]

    def session_count(self) -> int:
        return len(self._store)
