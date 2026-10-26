"""
Rewriting and substitution operations (expressions feature).
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

import sympy

from sympy_mcp.operations import OperationError, guard, stored
from sympy_mcp.parsing import SAFE_GLOBALS

if TYPE_CHECKING:
    from sympy_mcp.state import SymPyState


def _unchanged_note(before: Any, after: Any) -> Dict[str, str]:
    return {"note": "The expression is unchanged."} if before == after else {}


@guard("rewriting expression")
def rewrite_expression(state: "SymPyState", expr_key: str, target: str):
    expr = stored(state, expr_key)
    function = SAFE_GLOBALS.get(target) if not target.startswith("_") else None
    if function is None or not callable(function):
        raise OperationError(
            f"'{target}' is not a SymPy function. Use a name such as exp, cos, sin, tan, "
            "log, sqrt, gamma, factorial, Piecewise or Heaviside."
        )
    result = expr.rewrite(function)
    return state._result(state._store(result), **_unchanged_note(expr, result))


@guard("expanding logarithms")
def expand_log_expression(state: "SymPyState", expr_key: str, force: bool):
    expr = stored(state, expr_key)
    result = sympy.expand_log(expr, force=force)
    return state._result(state._store(result), **_unchanged_note(expr, result))


@guard("simplifying trigonometric expression")
def trigsimp_expression(state: "SymPyState", expr_key: str):
    expr = stored(state, expr_key)
    result = sympy.trigsimp(expr)
    return state._result(state._store(result), **_unchanged_note(expr, result))


@guard("combining powers")
def powsimp_expression(state: "SymPyState", expr_key: str, force: bool):
    expr = stored(state, expr_key)
    result = sympy.powsimp(expr, force=force)
    return state._result(state._store(result), **_unchanged_note(expr, result))


@guard("finding a closed form")
def nsimplify_expression(
    state: "SymPyState",
    expr_key: str,
    constants: Optional[List[str]],
    tolerance: Optional[float],
    rational: bool,
):
    expr = stored(state, expr_key)
    parsed_constants = [state._parse(c) for c in (constants or [])]
    result = sympy.nsimplify(expr, constants=parsed_constants, tolerance=tolerance, rational=rational)
    return state._result(state._store(result))


@guard("during substitution")
def substitute_values(state: "SymPyState", expr_key: str, substitutions: Dict[str, str]):
    if not substitutions:
        raise OperationError("substitutions is empty.")
    expr = stored(state, expr_key)
    namespace = state._parse_dict()
    mapping = {}
    for target, value in substitutions.items():
        if target.isidentifier() and target not in namespace:
            raise OperationError(f"'{target}' is not a symbol in this session. Introduce it first.")
        mapping[state._parse(target)] = state._parse(value)
    # Simultaneous, so {"x": "y", "y": "x"} swaps x and y
    result = expr.subs(mapping, simultaneous=True)
    return state._result(state._store(result))
