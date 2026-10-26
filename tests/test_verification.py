import json

import pytest
import sympy

from sympy_mcp import verification
from sympy_mcp.shared.enums import Assumption
from sympy_mcp.state import SymPyState


def check(state, a, b, samples=20):
    return json.loads(state.check_equivalence(a, b, samples))


@pytest.fixture
def state():
    return SymPyState()


class TestProvedEqual:
    def test_simplify(self, state):
        state.intro("x", [], [])
        assert check(state, "sin(x)**2 + cos(x)**2", "1") == {
            "verdict": "proved_equal", "method": "simplify"
        }

    def test_rewrite_exp(self, state):
        state.intro("x", [], [])
        result = check(state, "tanh(x)", "(exp(2*x) - 1)/(exp(2*x) + 1)")
        assert result == {"verdict": "proved_equal", "method": "rewrite(exp)"}

    def test_stored_keys_and_references(self, state):
        state.intro("x", [], [])
        a = state.introduce_expression("(x + 1)**2")
        b = state.introduce_expression("x**2 + 2*x + 1")
        assert check(state, a, b)["verdict"] == "proved_equal"
        assert check(state, f"@{a} - @{b}", "0")["verdict"] == "proved_equal"

    def test_assumptions_enable_proof(self, state):
        state.intro("x", [Assumption.POSITIVE], [])
        assert check(state, "sqrt(x**2)", "x")["verdict"] == "proved_equal"

    def test_matrices(self, state):
        state.intro("x", [], [])
        a = state.create_matrix([["sin(x)**2 + cos(x)**2", "x"], ["0", "1"]])
        b = state.create_matrix([["1", "x"], ["0", "1"]])
        assert check(state, a, b)["verdict"] == "proved_equal"


class TestNumericallyEqual:
    def test_identity_simplify_cannot_prove(self, state):
        state.intro("x", [Assumption.POSITIVE], [])
        result = check(state, "atan(x) + atan(1/x)", "pi/2")
        assert result["verdict"] == "numerically_equal"
        assert result["samples"] == 20
        assert float(result["max_relative_error"]) < 1e-20

    def test_samples_respect_assumptions(self, state):
        # atan(x) + atan(1/x) = -pi/2 for x < 0, so positive samples are required
        state.intro("x", [Assumption.POSITIVE], [])
        assert check(state, "atan(x) + atan(1/x)", "-pi/2")["verdict"] == "not_equal"


class TestNotEqual:
    def test_counterexample(self, state):
        state.intro("x", [Assumption.REAL], [])
        result = check(state, "sqrt(x**2)", "x")
        assert result["verdict"] == "not_equal"
        x_value = sympy.sympify(result["counterexample"]["x"])
        assert x_value < 0
        assert sympy.sympify(result["value_a"]) == pytest.approx(-x_value)

    def test_polynomial(self, state):
        state.intro("x", [], [])
        assert check(state, "x**2", "x")["verdict"] == "not_equal"

    def test_forced_log_rewrite_is_overridden_by_counterexample(self, state):
        # log(x*y) = log(x) + log(y) only on principal branches; x, y are complex here
        state.intro("x", [], [])
        state.intro("y", [], [])
        result = check(state, "log(x*y)", "log(x) + log(y)")
        assert result["verdict"] == "not_equal"
        assert "expand_log(force=True)" in result["note"]

    def test_forced_log_rewrite_with_positive_symbols(self, state):
        state.intro("x", [Assumption.POSITIVE], [])
        state.intro("y", [Assumption.POSITIVE], [])
        assert check(state, "log(x*y)", "log(x) + log(y)") == {
            "verdict": "proved_equal", "method": "simplify"
        }

    def test_matrix_shape_mismatch(self, state):
        a = state.create_matrix([["1", "0"]])
        b = state.create_matrix([["1"], ["0"]])
        assert check(state, a, b)["verdict"] == "not_equal"


class TestInconclusiveAndErrors:
    def test_undefined_functions(self, state):
        state.intro("x", [], [])
        state.introduce_function("f")
        result = check(state, "f(x)**2", "f(x)")
        assert result["verdict"] == "inconclusive"
        assert "undefined functions" in result["reason"]

    def test_numeric_disabled(self, state):
        state.intro("x", [Assumption.POSITIVE], [])
        assert check(state, "atan(x) + atan(1/x)", "pi/2", samples=0)["verdict"] == "inconclusive"

    def test_equations_rejected(self, state):
        state.intro("x", [], [])
        eq = state.introduce_equation("x", "1")
        assert check(state, eq, "x - 1")["verdict"] == "inconclusive"

    def test_unknown_key(self, state):
        assert state.check_equivalence("expr_404", "1").startswith("Error:")

    def test_constants(self, state):
        assert check(state, "exp(I*pi)", "-1")["verdict"] == "proved_equal"


def test_sampler_values_satisfy_assumptions():
    import random
    rng = random.Random(1)
    for assumptions in [
        {"positive": True}, {"negative": True}, {"integer": True, "positive": True},
        {"real": True, "nonzero": True}, {"rational": True, "negative": True}, {},
    ]:
        symbol = sympy.Symbol("s", **assumptions)
        for _ in range(20):
            point = verification._sample_point([symbol], rng)
            assert point is not None
            assert verification._satisfies(point[symbol], symbol)
