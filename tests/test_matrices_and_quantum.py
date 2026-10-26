import json

import pytest
import sympy
from sympy.physics.quantum import Dagger
from sympy.physics.quantum.boson import BosonCoherentKet

from sympy_mcp.shared.enums import Assumption
from sympy_mcp.state import SymPyState


def value(state, result):
    assert not result.startswith("Error"), result
    return state.expressions[result.key]


@pytest.fixture
def state():
    return SymPyState()


class TestMatrixOperations:
    def test_multiply(self, state):
        a = state.create_matrix([["1", "2"], ["3", "4"]])
        b = state.create_matrix([["0", "1"], ["1", "0"]])
        assert value(state, state.matrix_multiply(a, b)) == sympy.Matrix([[2, 1], [4, 3]])

    def test_multiply_shape_mismatch(self, state):
        a = state.create_matrix([["1", "2"]])
        assert "Cannot multiply" in state.matrix_multiply(a, a)

    def test_power_integer_and_symbolic(self, state):
        state.intro("n", [Assumption.INTEGER, Assumption.POSITIVE], [])
        a = state.create_matrix([["1", "1"], ["0", "1"]])
        assert value(state, state.matrix_power(a, "3")) == sympy.Matrix([[1, 3], [0, 1]])
        n = state.local_vars["n"]
        assert value(state, state.matrix_power(a, "n")) == sympy.Matrix([[1, n], [0, 1]])

    def test_exp_of_rotation_generator(self, state):
        state.intro("theta", [Assumption.REAL], [])
        a = state.create_matrix([["0", "theta"], ["-theta", "0"]])
        th = state.local_vars["theta"]
        result = sympy.simplify(value(state, state.matrix_exp(a)))
        assert result == sympy.Matrix([[sympy.cos(th), sympy.sin(th)], [-sympy.sin(th), sympy.cos(th)]])

    def test_trace_transpose_rank(self, state):
        a = state.create_matrix([["1", "2"], ["2", "4"]])
        assert value(state, state.matrix_trace(a)) == 5
        assert value(state, state.matrix_rank(a)) == 1
        b = state.create_matrix([["1", "2", "3"]])
        assert value(state, state.matrix_transpose(b)) == sympy.Matrix([[1], [2], [3]])

    def test_adjoint_is_conjugate_transpose(self, state):
        a = state.create_matrix([["1", "I"], ["0", "2"]])
        assert value(state, state.matrix_adjoint(a)) == sympy.Matrix([[1, 0], [-sympy.I, 2]])

    def test_pauli_commutator(self, state):
        sx = state.create_matrix([["0", "1"], ["1", "0"]])
        sy = state.create_matrix([["0", "-I"], ["I", "0"]])
        sz = sympy.Matrix([[1, 0], [0, -1]])
        assert value(state, state.matrix_commutator(sx, sy)) == 2 * sympy.I * sz

    def test_nullspace(self, state):
        a = state.create_matrix([["1", "2"], ["2", "4"]])
        result = state.matrix_nullspace(a)
        assert value(state, result) == [sympy.Matrix([[-2], [1]])]
        assert result.extras["dimension"] == 1

    def test_not_a_matrix(self, state):
        state.intro("x", [], [])
        e = state.introduce_expression("x")
        assert "is not a matrix" in state.matrix_trace(e)

    def test_non_square(self, state):
        a = state.create_matrix([["1", "2"]])
        assert "not square" in state.matrix_exp(a)


@pytest.fixture
def boson():
    state = SymPyState()
    assert state.introduce_boson_operator("a") == "a"
    state.intro("alpha", [], [])
    return state


class TestQuantum:
    def test_operator_in_expressions(self, boson):
        expr = boson.introduce_expression("a*Dagger(a)")
        a = boson.local_vars["a"]
        assert boson.expressions[expr] == a * Dagger(a)

    def test_commutators(self, boson):
        assert value(boson, boson.evaluate_commutator("a", "Dagger(a)")) == 1
        a = boson.local_vars["a"]
        assert value(boson, boson.evaluate_commutator("a", "Dagger(a)**2")) == 2 * Dagger(a)

    def test_independent_modes_commute(self, boson):
        boson.introduce_boson_operator("b")
        assert value(boson, boson.evaluate_commutator("a", "Dagger(b)")) == 0

    def test_normal_order_modes(self, boson):
        expr = boson.introduce_expression("a*Dagger(a)")
        a = boson.local_vars["a"]
        assert value(boson, boson.normal_order_expression(expr, "symbol")) == Dagger(a) * a
        assert value(boson, boson.normal_order_expression(expr, "commute")) == Dagger(a) * a + 1
        assert "mode must be" in boson.normal_order_expression(expr, "other")

    def test_quantum_apply(self, boson):
        expr = boson.introduce_expression("a*BosonCoherentKet(alpha)")
        alpha = boson.local_vars["alpha"]
        assert value(boson, boson.quantum_apply(expr)) == alpha * BosonCoherentKet(alpha)

    def test_normal_ordered_coherent_expectation(self, boson):
        """<alpha| :(a + a^dagger)^2: |alpha> = (alpha + conjugate(alpha))^2"""
        x2 = boson.introduce_expression("(a + Dagger(a))**2")
        normal = boson.normal_order_expression(x2, "symbol")
        expectation = boson.coherent_state_expectation(normal.key, "a", "alpha")
        verdict = json.loads(boson.check_equivalence(expectation.key, "(alpha + conjugate(alpha))**2"))
        assert verdict["verdict"] == "proved_equal"

    def test_coherent_expectation_without_normal_ordering(self, boson):
        # <alpha|(a + a^dagger)^2|alpha> = (alpha + conjugate(alpha))^2 + 1, from a a^dagger = a^dagger a + 1
        x2 = boson.introduce_expression("(a + Dagger(a))**2")
        expectation = boson.coherent_state_expectation(x2, "a", "alpha")
        verdict = json.loads(boson.check_equivalence(expectation.key, "(alpha + conjugate(alpha))**2 + 1"))
        assert verdict["verdict"] == "proved_equal"

    def test_coherent_expectation_rejects_other_modes(self, boson):
        boson.introduce_boson_operator("b")
        expr = boson.introduce_expression("Dagger(a)*b")
        assert "other modes remain" in boson.coherent_state_expectation(expr, "a", "alpha")

    def test_coherent_expectation_needs_operator(self, boson):
        expr = boson.introduce_expression("alpha")
        assert "not a bosonic annihilation operator" in boson.coherent_state_expectation(expr, "alpha", "1")
