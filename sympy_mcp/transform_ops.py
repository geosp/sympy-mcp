"""
Integral transforms and numeric integration (calculus feature).

Conventions are SymPy's:
  Fourier  F(k) = ∫ f(x) exp(-2 pi i x k) dx
  Laplace  F(s) = ∫_0^oo f(t) exp(-s t) dt
"""

from typing import TYPE_CHECKING, Any, Dict

import mpmath
import sympy
from sympy.core.function import AppliedUndef
from sympy.integrals.transforms import IntegralTransform

from sympy_mcp.operations import OperationError, guard, stored, symbol

if TYPE_CHECKING:
    from sympy_mcp.state import SymPyState

MAX_PRECISION = 1000


def _unevaluated_note(value: Any) -> Dict[str, str]:
    if isinstance(value, IntegralTransform) or value.has(IntegralTransform):
        return {"note": "SymPy could not compute this transform in closed form; the result is unevaluated."}
    return {}


@guard("computing Fourier transform")
def fourier_transform(state: "SymPyState", expr_key: str, var_name: str, k_name: str, inverse: bool):
    expr = stored(state, expr_key)
    var, k = symbol(state, var_name), symbol(state, k_name)
    if inverse:
        result = sympy.inverse_fourier_transform(expr, var, k)
    else:
        result = sympy.fourier_transform(expr, var, k)
    return state._result(state._store(result), **_unevaluated_note(result))


@guard("computing Laplace transform")
def laplace_transform(state: "SymPyState", expr_key: str, t_name: str, s_name: str):
    expr = stored(state, expr_key)
    t, s = symbol(state, t_name), symbol(state, s_name)
    transformed = sympy.laplace_transform(expr, t, s)
    if isinstance(transformed, tuple):
        result, abscissa, conditions = transformed
        extras = {"convergence_abscissa": str(abscissa), "conditions": str(conditions)}
    else:
        result, extras = transformed, {}
    return state._result(state._store(result), **extras, **_unevaluated_note(result))


@guard("computing inverse Laplace transform")
def inverse_laplace_transform(state: "SymPyState", expr_key: str, s_name: str, t_name: str):
    expr = stored(state, expr_key)
    s, t = symbol(state, s_name), symbol(state, t_name)
    result = sympy.inverse_laplace_transform(expr, s, t)
    return state._result(state._store(result), **_unevaluated_note(result))


def _mp_bound(value: Any, dps: int) -> Any:
    if value == sympy.oo:
        return mpmath.inf
    if value == -sympy.oo:
        return -mpmath.inf
    if not value.is_number or value.free_symbols:
        raise OperationError(f"Integration bound '{value}' is not a number.")
    number = sympy.N(value, dps + 5)
    if not number.is_real:
        raise OperationError(f"Integration bound '{value}' is not real.")
    return mpmath.mpf(str(number))


@guard("during numeric integration")
def numeric_integrate(
    state: "SymPyState", expr_key: str, var_name: str, lower: str, upper: str, precision: int
):
    if not 1 <= precision <= MAX_PRECISION:
        raise OperationError(f"precision must be between 1 and {MAX_PRECISION} digits.")
    expr = stored(state, expr_key)
    var = symbol(state, var_name)
    others = sorted(str(s) for s in sympy.sympify(expr).free_symbols - {var})
    if others:
        raise OperationError(
            f"The integrand has free symbols other than {var_name}: {', '.join(others)}. "
            "Substitute values for them first (e.g. with substitute_values)."
        )
    if expr.has(AppliedUndef):
        raise OperationError("The integrand contains undefined functions, which can't be evaluated numerically.")
    # lambdify prints names into generated code, so integrate over a fresh dummy variable
    dummy = sympy.Dummy("x")
    expr = expr.subs(var, dummy)
    with mpmath.workdps(precision + 5):
        a = _mp_bound(state._parse(lower), precision)
        b = _mp_bound(state._parse(upper), precision)
        func = sympy.lambdify(dummy, expr, "mpmath")
        value, error = mpmath.quad(func, [a, b], error=True)
        if isinstance(value, mpmath.mpc):
            result = sympy.Float(str(value.real), precision) + sympy.I * sympy.Float(str(value.imag), precision)
        else:
            result = sympy.Float(str(value), precision)
        error_estimate = mpmath.nstr(error, 3)
    return state._result(state._store(result), precision=precision, error_estimate=error_estimate)
