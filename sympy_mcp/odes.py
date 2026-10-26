"""
Helpers for the ODE tools: initial conditions and solution right-hand sides.
"""

import re
from typing import Any, Callable, Dict, List, Optional

import sympy
from sympy.core.function import AppliedUndef

# f'(0), f''(a), ... : derivative of order len(primes) of f at a point
PRIME_CONDITION = re.compile(r"^\s*([A-Za-z_]\w*)('+)\((.+)\)\s*$")


def parse_ics(
    ics: Dict[str, str], equations: List[Any], parse: Callable[[str], Any]
) -> Dict[Any, Any]:
    """Turn {"f(0)": "1", "f'(0)": "0"} into the dict dsolve's `ics` expects.

    Keys are either expressions such as "f(0)" or "f(x).diff(x).subs(x, 0)",
    or the prime shorthand "f'(0)", whose independent variable is taken from
    the function's application in the equations.
    """
    conditions: Dict[Any, Any] = {}
    for lhs, rhs in ics.items():
        match = PRIME_CONDITION.match(lhs)
        if match:
            name, primes, point = match.groups()
            applications = sorted(
                {a for eq in equations for a in eq.atoms(AppliedUndef) if a.func.__name__ == name},
                key=str,
            )
            if not applications:
                raise ValueError(
                    f"Initial condition '{lhs}': function '{name}' does not appear in the equations."
                )
            application = applications[0]
            if len(application.args) != 1 or not application.args[0].is_Symbol:
                raise ValueError(
                    f"Initial condition '{lhs}': '{name}' must be a function of one variable."
                )
            var = application.args[0]
            condition = application.diff(var, len(primes)).subs(var, parse(point))
        else:
            condition = parse(lhs)
        conditions[condition] = parse(rhs)
    return conditions


def explicit_rhs(solution: Any) -> Optional[Any]:
    """The right-hand side of f(x) = rhs, or None for an implicit solution."""
    if isinstance(solution, sympy.Eq) and isinstance(solution.lhs, AppliedUndef):
        return solution.rhs
    return None


def rhs_extras(solution: Any, store: Callable[[Any], str]) -> Dict[str, Any]:
    """Store each explicit right-hand side; return the payload fields describing them."""
    if isinstance(solution, list):
        keys = []
        for branch in solution:
            rhs = explicit_rhs(branch)
            keys.append(store(rhs) if rhs is not None else None)
        return {"rhs_keys": keys}
    rhs = explicit_rhs(solution)
    if rhs is None:
        return {
            "rhs_key": None,
            "note": "Implicit solution: SymPy could not solve for the function explicitly.",
        }
    return {"rhs_key": store(rhs), "rhs": str(rhs), "rhs_latex": sympy.latex(rhs)}


def system_rhs_extras(solution: Any, store: Callable[[Any], str]) -> Dict[str, Any]:
    """For a system: {"rhs_keys": {function name: key}} for each explicit solution."""
    solutions = solution if isinstance(solution, list) else [solution]
    keys: Dict[str, Optional[str]] = {}
    for eq in solutions:
        rhs = explicit_rhs(eq)
        if rhs is not None:
            keys[eq.lhs.func.__name__] = store(rhs)
    return {"rhs_keys": keys}
