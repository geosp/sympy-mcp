import asyncio
import json
import subprocess
import sys

from fastmcp import Client

from sympy_mcp import transcript
from sympy_mcp.config import AppConfig
from sympy_mcp.server import SymPyMCPServer, create_service

CALLS = [
    ("intro", {"var_name": "x", "assumptions": ["real"]}),
    ("intro", {"var_name": "R", "assumptions": ["positive"]}),
    ("introduce_function", {"func_name": "theta"}),
    ("introduce_expression", {"expression": "exp(-x**2)"}),
    ("numeric_integrate", {"expr_key": "expr_0", "var_name": "x", "lower_bound": "-oo", "upper_bound": "oo", "precision": 20}),
    ("integrate_expression", {"expr_key": "expr_0", "var_name": "x", "lower_bound": "-oo", "upper_bound": "oo"}),
    ("check_equivalence", {"expr_a": "@expr_2", "expr_b": "sqrt(pi)"}),
    ("introduce_equation", {"lhs_expression": "Derivative(theta(x), x)", "rhs_expression": "-theta(x)**2/2 - R"}),
    ("dsolve_ode", {"expr_key": "eq_3", "func_name": "theta", "ics": {"theta(0)": "0"}}),
    ("simplify_expression", {"expr_key": "expr_404"}),
    ("print_latex_expression", {"expr_key": "expr_0", "include_assumptions": False}),
]


async def _run_session(mcp, client, description, calls):
    created = await client.call_tool("create_session", {"description": description})
    session_id = json.loads(created.data)["session_id"]
    results = []
    for name, args in calls:
        result = await client.call_tool(name, {"session_id": session_id, **args}, raise_on_error=False)
        results.append("".join(getattr(b, "text", "") for b in result.content))
    await client.call_tool("list_session_state", {"session_id": session_id})
    return session_id, results


def _export(calls, fmt, extra_session_calls=None):
    async def run():
        config = AppConfig()
        mcp = SymPyMCPServer(config.server, create_service(config)).create_mcp_app()
        async with Client(mcp) as client:
            session_id, results = await _run_session(mcp, client, "export test", calls)
            if extra_session_calls:
                await _run_session(mcp, client, "other", extra_session_calls)
            exported = await client.call_tool("export_session", {"session_id": session_id, "format": fmt})
            return results, exported.data
    return asyncio.run(run())


class TestJsonExport:
    def test_records_every_computation_in_order(self):
        results, exported = _export(CALLS, "json", extra_session_calls=[("intro", {"var_name": "z"})])
        document = json.loads(exported)
        assert document["format"] == "sympy-mcp-transcript"
        assert document["session"]["description"] == "export test"
        assert [c["tool"] for c in document["calls"]] == [name for name, _ in CALLS]
        for call, (_, args), result in zip(document["calls"], CALLS, results):
            assert call["arguments"] == args  # session_id is not recorded
            assert call.get("result", call.get("error")) == result
        # list_session_state ran after the computations but is bookkeeping, so not recorded;
        # the other session's call is in that session's transcript only

    def test_error_results_are_recorded(self):
        _, exported = _export(CALLS, "json")
        missing = json.loads(exported)["calls"][9]
        assert missing["tool"] == "simplify_expression"
        assert "not found" in missing["result"]

    def test_exceptions_are_recorded_as_errors(self):
        _, exported = _export([("introduce_expression", {"expression": "@nope + 1"})], "json")
        (call,) = json.loads(exported)["calls"]
        assert "Unknown reference" in call["error"]


class TestPythonExport:
    def _run_script(self, tmp_path, source):
        script = tmp_path / "replay.py"
        script.write_text(source)
        return subprocess.run(
            [sys.executable, str(script)], capture_output=True, text=True, timeout=300
        )

    def test_script_replays_and_matches(self, tmp_path):
        _, source = _export(CALLS, "python")
        completed = self._run_script(tmp_path, source)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert f"All {len(CALLS)} calls reproduced" in completed.stdout

    def test_script_reports_a_mismatch(self, tmp_path):
        _, exported = _export(CALLS[:5], "json")
        document = json.loads(exported)
        document["calls"][4]["result"] = document["calls"][4]["result"].replace("1.7724", "1.9999")
        completed = self._run_script(tmp_path, transcript.export_python(document))
        assert completed.returncode == 1
        assert "[MISMATCH] 5. numeric_integrate" in completed.stdout

    def test_description_cannot_break_the_script(self, tmp_path):
        document = transcript.export_document(
            {"session_id": "s", "description": 'quotes """ and \\ backslashes', "created_at": "now"}, []
        )
        completed = self._run_script(tmp_path, transcript.export_python(document))
        assert completed.returncode == 0, completed.stderr


def test_unknown_format_and_session():
    async def run():
        config = AppConfig()
        mcp = SymPyMCPServer(config.server, create_service(config)).create_mcp_app()
        async with Client(mcp) as client:
            created = await client.call_tool("create_session", {"description": "x"})
            sid = json.loads(created.data)["session_id"]
            bad_format = await client.call_tool("export_session", {"session_id": sid, "format": "yaml"})
            bad_session = await client.call_tool("export_session", {"session_id": "nope"})
            return bad_format.data, bad_session.data
    bad_format, bad_session = asyncio.run(run())
    assert "Unknown format" in bad_format
    assert "not found" in bad_session
