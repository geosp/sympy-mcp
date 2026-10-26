"""
Bosonic operator algebra (quantum feature), built on sympy.physics.quantum.

Operators on different modes (different names) are treated as independent,
i.e. they commute.
"""

from typing import TYPE_CHECKING, Any, Dict

import sympy
from sympy.physics.quantum import AntiCommutator, Bra, Commutator, Dagger, InnerProduct, Ket, qapply
from sympy.physics.quantum.boson import BosonCoherentBra, BosonCoherentKet, BosonOp
from sympy.physics.quantum.operatorordering import normal_order, normal_ordered_form

from sympy_mcp.operations import OperationError, guard, stored

if TYPE_CHECKING:
    from sympy_mcp.state import SymPyState

# Names available in every expression string
NAMESPACE: Dict[str, Any] = {
    "Dagger": Dagger,
    "Commutator": Commutator,
    "AntiCommutator": AntiCommutator,
    "BosonOp": BosonOp,
    "BosonCoherentKet": BosonCoherentKet,
    "BosonCoherentBra": BosonCoherentBra,
    "Ket": Ket,
    "Bra": Bra,
    "InnerProduct": InnerProduct,
    "qapply": qapply,
    "normal_order": normal_order,
    "normal_ordered_form": normal_ordered_form,
}

ORDERING_MODES = ("symbol", "commute")


def _ordered_form(expr: Any) -> Any:
    """The same operator, rewritten in normal order using [a, a†] = 1."""
    return normal_ordered_form(sympy.expand(expr), independent=True)


@guard("introducing operator")
def introduce_boson_operator(state: "SymPyState", name: str) -> str:
    if not name.isidentifier():
        raise OperationError(f"'{name}' is not a valid name.")
    operator = BosonOp(name)
    state.local_vars[name] = operator
    state.user_symbols[name] = operator
    return name


@guard("normal ordering")
def normal_order_expression(state: "SymPyState", expr_key: str, mode: str):
    expr = stored(state, expr_key)
    if mode == "symbol":
        result = normal_order(sympy.expand(expr))
    elif mode == "commute":
        result = _ordered_form(expr)
    else:
        raise OperationError(f"mode must be one of: {', '.join(ORDERING_MODES)}.")
    return state._result(state._store(result))


@guard("evaluating commutator")
def evaluate_commutator(state: "SymPyState", expr_a: str, expr_b: str):
    try:
        a = state._resolve_operand(expr_a)
        b = state._resolve_operand(expr_b)
    except KeyError as e:
        raise OperationError(e.args[0])
    result = _ordered_form(Commutator(a, b).doit())
    return state._result(state._store(result))


@guard("applying operators")
def quantum_apply(state: "SymPyState", expr_key: str):
    return state._result(state._store(qapply(sympy.expand(stored(state, expr_key)))))


@guard("computing coherent-state expectation value")
def coherent_state_expectation(state: "SymPyState", expr_key: str, operator_name: str, alpha: str):
    """<alpha| X |alpha> for the coherent state of `operator_name`'s mode.

    X is first rewritten in normal order (using [a, a†] = 1), after which
    <alpha| f(a†, a) |alpha> = f(conjugate(alpha), alpha) exactly.
    """
    expr = stored(state, expr_key)
    operator = state.local_vars.get(operator_name)
    if not isinstance(operator, BosonOp) or not operator.is_annihilation:
        raise OperationError(
            f"'{operator_name}' is not a bosonic annihilation operator. Create it with introduce_boson_operator."
        )
    eigenvalue = state._parse(alpha)
    ordered = _ordered_form(expr)
    result = ordered.subs(Dagger(operator), sympy.conjugate(eigenvalue)).subs(operator, eigenvalue)
    remaining = sorted({str(op) for op in result.atoms(BosonOp)})
    if remaining:
        raise OperationError(
            f"Operators of other modes remain ({', '.join(remaining)}); this tool takes the "
            "expectation value in a coherent state of one mode only."
        )
    return state._result(state._store(sympy.expand(result)), normal_ordered=str(ordered))
