import json

import pytest
import sympy

from sympy_mcp.shared.enums import Assumption
from sympy_mcp.state import SymPyState


@pytest.fixture
def raychaudhuri():
    """theta' = -theta**2/2 - R (null Raychaudhuri equation with constant focusing R > 0)."""
    state = SymPyState()
    state.intro("U", [], [])
    state.intro("R", [Assumption.POSITIVE], [])
    state.introduce_function("theta")
    ode = state.introduce_equation("Derivative(theta(U), U)", "-theta(U)**2/2 - R")
    return state, ode


class TestInitialConditions:
    def test_raychaudhuri_with_initial_condition(self, raychaudhuri):
        state, ode = raychaudhuri
        result = state.dsolve_ode(ode, "theta", ics={"theta(0)": "0"})
        U, R = state.local_vars["U"], state.local_vars["R"]
        expected = -sympy.sqrt(2 * R) * sympy.tan(sympy.sqrt(R / 2) * U)

        solution = state.expressions[result.key]
        assert sympy.simplify(solution.rhs - expected) == 0

        rhs_key = result.extras["rhs_key"]
        assert sympy.simplify(state.expressions[rhs_key] - expected) == 0
        series = state.expressions[rhs_key].series(U, 0, 5)
        assert series == -R * U - R**2 * U**3 / 6 + sympy.O(U**5)

    def test_rhs_key_chains_into_series_tool(self, raychaudhuri):
        state, ode = raychaudhuri
        result = state.dsolve_ode(ode, "theta", ics={"theta(0)": "0"})
        series = state.series_expansion(result.extras["rhs_key"], "U", "0", 5)
        U, R = state.local_vars["U"], state.local_vars["R"]
        assert series.extras["series"] == str(-R * U - R**2 * U**3 / 6 + sympy.O(U**5))

    def test_derivative_condition_prime_shorthand(self):
        state = SymPyState()
        state.intro("x", [], [])
        state.introduce_function("y")
        ode = state.introduce_expression("Derivative(y(x), x, 2) + y(x)")
        result = state.dsolve_ode(ode, "y", ics={"y(0)": "0", "y'(0)": "1"})
        assert state.expressions[result.extras["rhs_key"]] == sympy.sin(state.local_vars["x"])

    def test_derivative_condition_expression_form(self):
        state = SymPyState()
        state.intro("x", [], [])
        state.introduce_function("y")
        ode = state.introduce_expression("Derivative(y(x), x, 2) + y(x)")
        result = state.dsolve_ode(ode, "y", ics={"y(0)": "1", "y(x).diff(x).subs(x, 0)": "0"})
        assert state.expressions[result.extras["rhs_key"]] == sympy.cos(state.local_vars["x"])

    def test_condition_on_unknown_function(self):
        state = SymPyState()
        state.intro("x", [], [])
        state.introduce_function("y")
        ode = state.introduce_expression("Derivative(y(x), x) - y(x)")
        result = state.dsolve_ode(ode, "y", ics={"z'(0)": "1"})
        assert "does not appear" in result

    def test_without_ics_unchanged(self):
        state = SymPyState()
        state.intro("x", [], [])
        state.introduce_function("f")
        ode = state.introduce_expression("Derivative(f(x), x) - f(x)")
        result = state.dsolve_ode(ode, "f")
        assert result == "f{\\left(x \\right)} = C_{1} e^{x}"
        assert str(state.expressions[result.extras["rhs_key"]]) == "C1*exp(x)"

    def test_implicit_solution_has_no_rhs_key(self):
        from sympy_mcp import odes
        x = sympy.Symbol("x")
        y = sympy.Function("y")
        stored = []
        implicit = sympy.Eq(x**2 + y(x) ** 2, sympy.Symbol("C1"))
        extras = odes.rhs_extras(implicit, lambda v: stored.append(v) or "k")
        assert extras["rhs_key"] is None
        assert "Implicit" in extras["note"]
        assert stored == []

    def test_system_with_initial_conditions(self):
        state = SymPyState()
        state.intro("t", [], [])
        state.introduce_function("f")
        state.introduce_function("g")
        a = state.introduce_equation("Derivative(f(t), t)", "g(t)")
        b = state.introduce_equation("Derivative(g(t), t)", "-f(t)")
        result = state.dsolve_system([a, b], ["f", "g"], ics={"f(0)": "0", "g(0)": "1"})
        t = state.local_vars["t"]
        assert state.expressions[result.extras["rhs_keys"]["f"]] == sympy.sin(t)
        assert state.expressions[result.extras["rhs_keys"]["g"]] == sympy.cos(t)


class TestVerifyOdeSolution:
    def test_verify_stored_solution(self, raychaudhuri):
        state, ode = raychaudhuri
        result = state.dsolve_ode(ode, "theta", ics={"theta(0)": "0"})
        assert json.loads(state.verify_ode_solution(result.key, expr_key=ode)) == {
            "verified": True, "residual": "0"
        }

    def test_verify_claimed_rhs_expression(self, raychaudhuri):
        state, ode = raychaudhuri
        verdict = json.loads(state.verify_ode_solution(
            "-sqrt(2*R)*tan(sqrt(R/2)*U)", expr_key=ode, func_name="theta"
        ))
        assert verdict["verified"] is True

    def test_wrong_solution_is_rejected(self, raychaudhuri):
        state, ode = raychaudhuri
        verdict = json.loads(state.verify_ode_solution(
            "-sqrt(2*R)*tanh(sqrt(R/2)*U)", expr_key=ode, func_name="theta"
        ))
        assert verdict["verified"] is False
        assert verdict["residual"] != "0"

    def test_verify_system(self):
        state = SymPyState()
        state.intro("t", [], [])
        state.introduce_function("f")
        state.introduce_function("g")
        a = state.introduce_equation("Derivative(f(t), t)", "g(t)")
        b = state.introduce_equation("Derivative(g(t), t)", "-f(t)")
        result = state.dsolve_system([a, b], ["f", "g"])
        verdict = json.loads(state.verify_ode_solution(result.key, expr_keys=[a, b]))
        assert verdict == {"verified": True, "residuals": ["0", "0"]}

    def test_rhs_requires_func_name(self, raychaudhuri):
        state, ode = raychaudhuri
        assert "func_name" in state.verify_ode_solution("U", expr_key=ode)

    def test_exactly_one_of_expr_key_and_expr_keys(self, raychaudhuri):
        state, ode = raychaudhuri
        assert state.verify_ode_solution("U", expr_key=ode, expr_keys=[ode]).startswith("Error")
        assert state.verify_ode_solution("U").startswith("Error")
