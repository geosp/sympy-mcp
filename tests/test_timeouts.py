import asyncio
import json
import time

import pytest
from fastmcp import Client

from sympy_mcp import timeouts
from sympy_mcp.config import AppConfig
from sympy_mcp.results import run_tool
from sympy_mcp.server import SymPyMCPServer, create_service
from sympy_mcp.state import SymPyState

# An exact ODE whose dsolve runs for minutes in SymPy 1.14
SLOW_ODE = "(2*x*y(x) + cos(y(x))) + (x**2 - x*sin(y(x)))*Derivative(y(x), x)"


def busy(seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        pass
    return "done"


@pytest.fixture(autouse=True)
def default_limit():
    timeouts.configure(timeouts.DEFAULT_SECONDS)
    yield
    timeouts.configure(timeouts.DEFAULT_SECONDS)


class TestTimeLimit:
    def test_interrupts(self):
        started = time.monotonic()
        with pytest.raises(timeouts.ComputationTimeout):
            with timeouts.time_limit(0.2):
                busy(5)
        assert time.monotonic() - started < 1

    def test_zero_means_no_limit(self):
        with timeouts.time_limit(0):
            assert busy(0.3) == "done"

    def test_not_swallowed_by_except_exception(self):
        def swallow():
            try:
                busy(5)
            except Exception:
                return "swallowed"
        assert timeouts.run_limited(swallow, 0.2).startswith("Error: Computation timed out after 0.2 seconds")

    def test_nested_limits_restore_the_outer_one(self):
        with pytest.raises(timeouts.ComputationTimeout):
            with timeouts.time_limit(0.5):
                with timeouts.time_limit(5):
                    busy(0.1)
                busy(5)  # the outer 0.5 s limit must still fire

    def test_default_and_override(self):
        timeouts.configure(0.2)
        assert timeouts.run_limited(lambda: busy(5)).startswith("Error: Computation timed out after 0.2")
        assert timeouts.run_limited(lambda: busy(0.4), 2) == "done"


class TestToolTimeouts:
    def test_slow_dsolve_returns_an_error(self):
        state = SymPyState()
        state.intro("x", [], [])
        state.introduce_function("y")
        ode = state.introduce_expression(SLOW_ODE)
        started = time.monotonic()
        result = json.loads(run_tool(lambda: state.dsolve_ode(ode, "y"), "structured", 1))
        assert time.monotonic() - started < 5
        assert "timed out after 1 seconds" in result["error"]
        # The session keeps working afterwards
        assert state.integrate_expression(state.introduce_expression("x**2"), "x")

    def test_through_mcp(self):
        async def run():
            config = AppConfig()
            mcp = SymPyMCPServer(config.server, create_service(config)).create_mcp_app()
            async with Client(mcp) as client:
                created = await client.call_tool("create_session", {"description": "timeouts"})
                sid = json.loads(created.data)["session_id"]
                await client.call_tool("intro", {"session_id": sid, "var_name": "x"})
                await client.call_tool("introduce_function", {"session_id": sid, "func_name": "y"})
                await client.call_tool("introduce_expression", {"session_id": sid, "expression": SLOW_ODE})
                started = time.monotonic()
                slow = await client.call_tool(
                    "dsolve_ode", {"session_id": sid, "expr_key": "expr_0", "func_name": "y", "timeout_seconds": 1}
                )
                elapsed = time.monotonic() - started
                fast = await client.call_tool("simplify_expression", {"session_id": sid, "expr_key": "expr_0"})
                return slow.data, elapsed, fast.data
        slow, elapsed, fast = asyncio.run(run())
        assert "timed out" in json.loads(slow)["error"]
        assert elapsed < 5
        assert "key" in json.loads(fast)

    def test_config_sets_server_default(self, monkeypatch):
        monkeypatch.setenv("SYMPY_TIMEOUT", "2.5")
        config = AppConfig()
        assert config.sympy.timeout_seconds == 2.5
        create_service(config)
        assert timeouts.resolve(None) == 2.5
