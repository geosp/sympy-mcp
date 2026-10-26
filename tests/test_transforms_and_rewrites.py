import pytest
import sympy

from sympy_mcp.shared.enums import Assumption
from sympy_mcp.state import SymPyState


@pytest.fixture
def state():
    state = SymPyState()
    state.intro_many(["x", "y", "k", "t", "s"])
    state.intro("a", [Assumption.POSITIVE], [])
    return state


def value(state, result):
    assert not result.startswith("Error"), result
    return state.expressions[result.key]


class TestFourier:
    def test_gaussian_and_back(self, state):
        f = state.introduce_expression("exp(-x**2)")
        F = state.fourier_transform(f, "x", "k")
        k = state.local_vars["k"]
        assert value(state, F) == sympy.sqrt(sympy.pi) * sympy.exp(-sympy.pi**2 * k**2)
        back = state.inverse_fourier_transform(F.key, "k", "x")
        assert value(state, back) == sympy.exp(-state.local_vars["x"] ** 2)

    def test_unknown_symbol(self, state):
        f = state.introduce_expression("exp(-x**2)")
        assert "Symbol 'q' not found" in state.fourier_transform(f, "x", "q")


class TestLaplace:
    def test_exponential(self, state):
        f = state.introduce_expression("exp(-a*t)")
        F = state.laplace_transform(f, "t", "s")
        assert value(state, F) == 1 / (state.local_vars["a"] + state.local_vars["s"])
        assert F.extras["convergence_abscissa"] == "-a"

    def test_inverse(self, state):
        F = state.introduce_expression("1/(s + 1)")
        f = state.inverse_laplace_transform(F, "s", "t")
        t = state.local_vars["t"]
        assert value(state, f) == sympy.exp(-t) * sympy.Heaviside(t)

    def test_unevaluated_transform_is_flagged(self, state):
        f = state.introduce_expression("exp(t**2)")  # grows too fast to have a Laplace transform
        F = state.laplace_transform(f, "t", "s")
        assert "note" in F.extras


class TestNumericIntegrate:
    def test_gaussian_over_real_line(self, state):
        f = state.introduce_expression("exp(-x**2)")
        result = state.numeric_integrate(f, "x", "-oo", "oo", precision=30)
        assert abs(value(state, result) - sympy.sqrt(sympy.pi).evalf(40)) < sympy.Float("1e-28")
        assert result.extras["precision"] == 30
        assert float(result.extras["error_estimate"]) < 1e-25

    def test_finite_bounds_and_reference(self, state):
        upper = state.introduce_expression("pi")
        f = state.introduce_expression("sin(x)")
        result = state.numeric_integrate(f, "x", "0", f"@{upper}")
        assert abs(value(state, result) - 2) < 1e-13

    def test_free_symbols_rejected(self, state):
        f = state.introduce_expression("exp(-y*x**2)")
        assert "free symbols other than x: y" in state.numeric_integrate(f, "x", "0", "1")

    def test_precision_bounds(self, state):
        f = state.introduce_expression("x")
        assert "precision must be" in state.numeric_integrate(f, "x", "0", "1", precision=0)


class TestRewrites:
    def test_rewrite_in_exp(self, state):
        f = state.introduce_expression("cosh(x)")
        x = state.local_vars["x"]
        assert value(state, state.rewrite_expression(f, "exp")) == sympy.exp(x) / 2 + sympy.exp(-x) / 2

    def test_rewrite_unknown_target(self, state):
        f = state.introduce_expression("cosh(x)")
        assert "not a SymPy function" in state.rewrite_expression(f, "notafunction")

    def test_rewrite_without_rule_notes_it(self, state):
        f = state.introduce_expression("x**2")
        assert state.rewrite_expression(f, "cos").extras["note"] == "The expression is unchanged."

    def test_expand_log_respects_assumptions(self, state):
        f = state.introduce_expression("log(x*y)")
        assert state.expand_log_expression(f).extras.get("note") == "The expression is unchanged."
        forced = state.expand_log_expression(f, force=True)
        x, y = state.local_vars["x"], state.local_vars["y"]
        assert value(state, forced) == sympy.log(x) + sympy.log(y)

    def test_trigsimp(self, state):
        f = state.introduce_expression("sin(x)**4 - 2*cos(x)**2*sin(x)**2 + cos(x)**4")
        x = state.local_vars["x"]
        assert value(state, state.trigsimp_expression(f)) == sympy.cos(4 * x) / 2 + sympy.Rational(1, 2)

    def test_powsimp(self, state):
        f = state.introduce_expression("x**a * x**2")
        assert value(state, state.powsimp_expression(f)) == state.local_vars["x"] ** (state.local_vars["a"] + 2)

    def test_nsimplify(self, state):
        third = state.introduce_expression("0.333333333333333")
        assert value(state, state.nsimplify_expression(third)) == sympy.Rational(1, 3)
        pi = state.introduce_expression("3.14159265358979")
        assert value(state, state.nsimplify_expression(pi, constants=["pi"])) == sympy.pi


class TestSubstituteValues:
    def test_several_at_once(self, state):
        f = state.introduce_expression("x**2 + y")
        result = state.substitute_values(f, {"x": "3", "y": "1/2"})
        assert value(state, result) == sympy.Rational(19, 2)

    def test_simultaneous(self, state):
        f = state.introduce_expression("x - 2*y")
        result = state.substitute_values(f, {"x": "y", "y": "x"})
        x, y = state.local_vars["x"], state.local_vars["y"]
        assert value(state, result) == y - 2 * x

    def test_values_can_reference_results(self, state):
        f = state.introduce_expression("x + 1")
        two = state.introduce_expression("1 + 1")
        assert value(state, state.substitute_values(f, {"x": f"@{two}"})) == 3

    def test_function_application_target(self, state):
        state.introduce_function("f")
        expr = state.introduce_expression("f(x)**2 + 1")
        assert value(state, state.substitute_values(expr, {"f(x)": "2"})) == 5

    def test_unknown_symbol(self, state):
        f = state.introduce_expression("x + 1")
        assert "not a symbol in this session" in state.substitute_values(f, {"z": "1"})
