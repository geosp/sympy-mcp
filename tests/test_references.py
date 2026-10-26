import pytest
import sympy

from sympy_mcp.parsing import substitute_references
from sympy_mcp.shared.enums import Assumption
from sympy_mcp.state import EINSTEINPY_AVAILABLE, SymPyState


@pytest.fixture
def state():
    state = SymPyState()
    state.intro("x", [Assumption.REAL], [])
    state.intro("y", [], [])
    return state


class TestSubstituteReferences:
    def test_reference_becomes_bound_placeholder(self):
        text, bindings = substitute_references("2*@expr_0 + 1", {"expr_0": 5}, {})
        assert text == "2*_ref_expr_0 + 1"
        assert bindings == {"_ref_expr_0": 5}

    def test_binary_at_is_left_alone(self):
        for text in ["A@B", "A @B", "(A)@B", "m[0]@B"]:
            assert substitute_references(text, {"B": 1}, {}) == (text, {})

    def test_unknown_reference_raises(self):
        with pytest.raises(ValueError, match="Unknown reference '@expr_9'"):
            substitute_references("@expr_9", {}, {})

    def test_placeholder_does_not_shadow_namespace(self):
        text, bindings = substitute_references("@e", {"e": 1}, {"_ref_e": "taken"})
        assert text == "_ref_e_"
        assert bindings == {"_ref_e_": 1}


class TestExpressionReferences:
    def test_introduce_expression_with_references(self, state):
        a = state.introduce_expression("x**2 - 1")
        b = state.introduce_expression("(x - 1)*(x + 1)")
        diff = state.introduce_expression(f"@{a} - @{b}")
        assert sympy.expand(state.expressions[diff]) == 0

    def test_reference_keeps_symbol_identity(self, state):
        a = state.introduce_expression("x + y")
        key = state.introduce_expression(f"@{a} * x")
        assert state.expressions[key].free_symbols == {state.local_vars["x"], state.local_vars["y"]}

    def test_reference_without_canonicalize(self, state):
        a = state.introduce_expression("x + 1")
        key = state.introduce_expression(f"@{a} + @{a}", canonicalize=False)
        assert sympy.simplify(state.expressions[key] - 2 * (state.local_vars["x"] + 1)) == 0

    def test_named_expression_reference(self, state):
        state.introduce_expression("x**3", expr_var_name="cube")
        key = state.introduce_expression("diff(@cube, x)")
        assert state.expressions[key] == 3 * state.local_vars["x"] ** 2

    def test_unknown_reference_is_an_error(self, state):
        with pytest.raises(ValueError, match="Unknown reference"):
            state.introduce_expression("@expr_42 + 1")

    def test_introduce_equation_with_references(self, state):
        a = state.introduce_expression("sin(x)**2 + cos(x)**2")
        b = state.introduce_expression("1")
        key = state.introduce_equation(f"@{a}", f"@{b}")
        eq = state.expressions[key]
        assert sympy.simplify(eq.lhs - eq.rhs) == 0

    def test_matrix_multiplication_operator_still_works(self, state):
        key = state.introduce_expression("Matrix([[1, 0], [0, 2]])@Matrix([[3], [4]])")
        assert state.expressions[key] == sympy.Matrix([[3], [8]])


class TestReferencesInOtherTools:
    def test_substitute_with_expression_replacement(self, state):
        target = state.introduce_expression("x**2 + y")
        repl = state.introduce_expression("y + 1")
        key = state.substitute_expression(target, "x", f"@{repl} * 2")
        y = state.local_vars["y"]
        assert sympy.expand(state.expressions[key] - ((2 * y + 2) ** 2 + y)) == 0

    def test_substitute_with_stored_key_unchanged(self, state):
        target = state.introduce_expression("x**2")
        repl = state.introduce_expression("y")
        key = state.substitute_expression(target, "x", repl)
        assert state.expressions[key] == state.local_vars["y"] ** 2

    def test_substitute_unknown_key_still_errors(self, state):
        target = state.introduce_expression("x**2")
        result = state.substitute_expression(target, "x", "expr_99")
        assert "not found" in result

    def test_create_matrix_with_reference(self, state):
        a = state.introduce_expression("x + 1")
        key = state.create_matrix([[f"@{a}", "0"], ["0", f"2*@{a}"]])
        x = state.local_vars["x"]
        assert state.expressions[key] == sympy.Matrix([[x + 1, 0], [0, 2 * x + 2]])

    def test_integrate_bounds_with_reference(self, state):
        upper = state.introduce_expression("2")
        integrand = state.introduce_expression("x")
        key = state.integrate_expression(integrand, "x", "0", f"@{upper}")
        assert state.expressions[key] == 2

    def test_limit_point_with_reference(self, state):
        point = state.introduce_expression("1")
        expr = state.introduce_expression("(x**2 - 1)/(x - 1)")
        key = state.limit_expression(expr, "x", f"@{point}")
        assert state.expressions[key] == 2

    def test_vector_field_with_reference(self, state):
        state.create_coordinate_system("C")
        comp = state.introduce_expression("@C.x**2")  # coordinate systems are stored too
        key = state.create_vector_field("C", f"@{comp}", "0", "0")
        div = state.calculate_divergence(key)
        assert str(state.expressions[div]) == "2*C.x"

    @pytest.mark.skipif(not EINSTEINPY_AVAILABLE, reason="EinsteinPy library is not available")
    def test_custom_metric_with_reference(self, state):
        lapse = state.introduce_expression("1 - 2/r")
        key = state.create_custom_metric([[f"-@{lapse}", "0"], ["0", f"1/@{lapse}"]], ["t", "r"])
        assert key.startswith("metric_custom_")
        assert str(state.expressions[key][0, 0]) == "-1 + 2/r"
