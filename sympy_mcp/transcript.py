"""
Session transcripts and export_session.

TranscriptMiddleware records every tool call made in a session (tool name,
arguments and the text it returned) on that session's SymPyState. The
transcript can be exported as JSON, or as a Python script that replays the
calls against a fresh in-process server and checks each result against the
recorded one.
"""

import json
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Dict, List

import sympy
from fastmcp.server.middleware import Middleware

from sympy_mcp.session import SessionNotFoundError, SymPySessionManager

# Session bookkeeping calls are not part of a session's computations
NOT_RECORDED = {"create_session", "list_sessions", "list_session_state", "export_session"}

EXPORT_FORMATS = ("python", "json")


def _text(result: Any) -> str:
    return "".join(getattr(block, "text", "") for block in getattr(result, "content", []) or [])


class TranscriptMiddleware(Middleware):
    """Append each tool call to the transcript of the session it names."""

    def __init__(self, session_manager: SymPySessionManager):
        self.session_manager = session_manager

    async def on_call_tool(self, context, call_next):
        name = context.message.name
        arguments = dict(context.message.arguments or {})
        session_id = arguments.pop("session_id", None)
        try:
            result = await call_next(context)
        except Exception as e:
            self._record(session_id, name, {"tool": name, "arguments": arguments, "error": str(e)})
            raise
        entry = {"tool": name, "arguments": arguments, "result": _text(result)}
        if getattr(result, "is_error", False):
            entry["error"] = entry.pop("result")
        self._record(session_id, name, entry)
        return result

    def _record(self, session_id: Any, name: str, entry: Dict[str, Any]) -> None:
        if name in NOT_RECORDED or not isinstance(session_id, str):
            return
        try:
            state = self.session_manager.get_sync(session_id)
        except SessionNotFoundError:
            return
        state.transcript.append(entry)


def _package_version() -> str:
    try:
        return version("sympy-mcp")
    except PackageNotFoundError:
        return "unknown"


def export_document(info: Dict[str, Any], calls: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "format": "sympy-mcp-transcript",
        "format_version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "sympy_mcp_version": _package_version(),
        "sympy_version": sympy.__version__,
        "session": info,
        "calls": calls,
    }


PYTHON_TEMPLATE = '''#!/usr/bin/env python3
"""Replay of sympy-mcp session {session_id}.

Exported {exported_at} from sympy-mcp {sympy_mcp_version} with SymPy {sympy_version}.

Runs the {count} recorded tool calls again, in order, against a fresh
in-process sympy-mcp server and compares each result with the recorded one.
Requires sympy-mcp (and the same SymPy version, for identical output) to be
installed. Exit status: 0 if every call reproduces its recorded result, 1 if
not. A call that hit its time limit may not time out again on another machine.
"""

import asyncio
import json
import sys

DESCRIPTION = {description_repr}

# Each call: {{"tool": name, "arguments": {{...}}, "result": text}} or {{..., "error": text}}
CALLS = json.loads({calls_literal})


async def replay() -> int:
    from fastmcp import Client

    from sympy_mcp.config import AppConfig
    from sympy_mcp.server import SymPyMCPServer, create_service

    config = AppConfig()
    mcp = SymPyMCPServer(config.server, create_service(config)).create_mcp_app()
    mismatches = 0
    async with Client(mcp) as client:
        created = await client.call_tool("create_session", {{"description": DESCRIPTION}})
        session_id = json.loads(created.data)["session_id"]
        for number, call in enumerate(CALLS, 1):
            arguments = {{"session_id": session_id, **call["arguments"]}}
            result = await client.call_tool(call["tool"], arguments, raise_on_error=False)
            text = "".join(getattr(block, "text", "") for block in result.content)
            if "error" in call:
                ok = result.is_error or text == call["error"]
                expected = "an error: " + call["error"]
            else:
                ok = not result.is_error and text == call["result"]
                expected = call["result"]
            print(f"[{{'ok' if ok else 'MISMATCH'}}] {{number}}. {{call['tool']}}({{json.dumps(call['arguments'])}})")
            if not ok:
                mismatches += 1
                print(f"    expected: {{expected}}")
                print(f"    got:      {{text}}")
    if mismatches:
        print(f"{{mismatches}} of {{len(CALLS)}} calls did not reproduce their recorded result.")
        return 1
    print(f"All {{len(CALLS)}} calls reproduced their recorded results.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(replay()))
'''


def export_python(document: Dict[str, Any]) -> str:
    session = document["session"]
    return PYTHON_TEMPLATE.format(
        session_id=session["session_id"],
        description_repr=repr(session.get("description", "")),
        exported_at=document["exported_at"],
        sympy_mcp_version=document["sympy_mcp_version"],
        sympy_version=document["sympy_version"],
        count=len(document["calls"]),
        calls_literal=repr(json.dumps(document["calls"], indent=1)),
    )
