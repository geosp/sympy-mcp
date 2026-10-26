"""
Matrix operations (linear_algebra feature).
"""

from typing import TYPE_CHECKING, Any

import sympy

from sympy_mcp.operations import OperationError, guard, stored

if TYPE_CHECKING:
    from sympy_mcp.state import SymPyState


def _matrix(state: "SymPyState", key: str) -> sympy.MatrixBase:
    value = stored(state, key)
    if not isinstance(value, sympy.MatrixBase):
        raise OperationError(f"'{key}' is not a matrix.")
    return value


def _square(state: "SymPyState", key: str) -> sympy.MatrixBase:
    matrix = _matrix(state, key)
    if not matrix.is_square:
        raise OperationError(f"'{key}' is not square (shape {matrix.shape}).")
    return matrix


def _store_matrix(state: "SymPyState", value: Any):
    key = state._next_matrix_key()
    state.expressions[key] = value
    return state._result(key)


@guard("multiplying matrices")
def multiply(state: "SymPyState", a_key: str, b_key: str):
    a, b = _matrix(state, a_key), _matrix(state, b_key)
    if a.shape[1] != b.shape[0]:
        raise OperationError(f"Cannot multiply shapes {a.shape} and {b.shape}.")
    return _store_matrix(state, a * b)


@guard("computing matrix power")
def power(state: "SymPyState", matrix_key: str, exponent: str):
    matrix = _square(state, matrix_key)
    return _store_matrix(state, matrix ** state._parse(exponent))


@guard("computing matrix exponential")
def exponential(state: "SymPyState", matrix_key: str):
    return _store_matrix(state, _square(state, matrix_key).exp())


@guard("computing trace")
def trace(state: "SymPyState", matrix_key: str):
    return state._result(state._store(_square(state, matrix_key).trace()))


@guard("transposing matrix")
def transpose(state: "SymPyState", matrix_key: str):
    return _store_matrix(state, _matrix(state, matrix_key).T)


@guard("computing adjoint")
def adjoint(state: "SymPyState", matrix_key: str):
    return _store_matrix(state, _matrix(state, matrix_key).adjoint())


@guard("computing commutator")
def commutator(state: "SymPyState", a_key: str, b_key: str):
    a, b = _square(state, a_key), _square(state, b_key)
    if a.shape != b.shape:
        raise OperationError(f"Cannot take the commutator of shapes {a.shape} and {b.shape}.")
    return _store_matrix(state, a * b - b * a)


@guard("computing rank")
def rank(state: "SymPyState", matrix_key: str):
    return state._result(state._store(sympy.Integer(_matrix(state, matrix_key).rank())))


@guard("computing nullspace")
def nullspace(state: "SymPyState", matrix_key: str):
    basis = _matrix(state, matrix_key).nullspace()
    return state._result(state._store(basis), dimension=len(basis))
