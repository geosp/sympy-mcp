"""
Equivalence checking for check_equivalence.

First tries to prove a - b == 0 symbolically (simplify, then a fixed list of
rewrites). If that fails, or the only proof relied on a rewrite that ignores
branch cuts, evaluates both sides at random points chosen to satisfy each
symbol's assumptions.
"""

import random
from typing import Any, Callable, Dict, List, Optional, Tuple

import sympy
from sympy.core.function import AppliedUndef

# (method name, transformation, sound for all values of the symbols?)
REWRITES: List[Tuple[str, Callable[[Any], Any], bool]] = [
    ("rewrite(exp)", lambda e: e.rewrite(sympy.exp), True),
    ("expand_log(force=True)", lambda e: sympy.expand_log(e, force=True), False),
    ("trigsimp", sympy.trigsimp, True),
    ("expand", sympy.expand, True),
    ("together", sympy.together, True),
]

PRECISION = 30            # significant digits for numeric evaluation
RELATIVE_TOLERANCE = 1e-10
SAMPLE_ATTEMPTS = 10      # tries per requested sample (singular points are skipped)
SEED = 0                  # fixed, so a check gives the same answer every time


def _elements(value: Any) -> List[Any]:
    if isinstance(value, sympy.MatrixBase):
        return list(value)
    return [value]


def _prove_zero(expr: Any) -> Optional[Tuple[str, bool]]:
    """Return (method, sound) for the first method that reduces expr to 0, else None."""
    if expr == 0 or sympy.simplify(expr) == 0:
        return "simplify", True
    for name, transform, sound in REWRITES:
        try:
            rewritten = transform(expr)
            if rewritten == 0 or sympy.simplify(rewritten) == 0:
                return name, sound
        except Exception:
            continue
    return None


def _candidate(symbol: sympy.Symbol, rng: random.Random) -> Any:
    """A random exact value in the category the symbol's assumptions describe."""
    def magnitude() -> sympy.Rational:
        return sympy.Rational(rng.randint(100, 3000), 1000)

    def signed(value: Any) -> Any:
        if symbol.is_positive or symbol.is_nonnegative:
            return value
        if symbol.is_negative or symbol.is_nonpositive:
            return -value
        return value if rng.random() < 0.5 else -value

    if symbol.is_zero:
        return sympy.Integer(0)
    if symbol.is_integer:
        return signed(sympy.Integer(rng.randint(1, 9)))
    if symbol.is_rational:
        return signed(sympy.Rational(rng.randint(1, 30), rng.randint(1, 7)))
    if symbol.is_irrational:
        return signed(magnitude() * sympy.sqrt(2))
    if symbol.is_transcendental:
        return signed(magnitude() * sympy.pi)
    if symbol.is_imaginary:
        return signed(magnitude()) * sympy.I
    if symbol.is_extended_real:
        return signed(magnitude())
    return signed(magnitude()) + signed(magnitude()) * sympy.I


def _satisfies(value: Any, symbol: sympy.Symbol) -> bool:
    for fact, expected in symbol.assumptions0.items():
        actual = getattr(value, f"is_{fact}", None)
        if actual is not None and actual != expected:
            return False
    return True


def _sample_point(symbols: List[sympy.Symbol], rng: random.Random) -> Optional[Dict[Any, Any]]:
    point = {}
    for symbol in symbols:
        for _ in range(50):
            value = _candidate(symbol, rng)
            if _satisfies(value, symbol):
                point[symbol] = value
                break
        else:
            return None
    return point


def _evaluate(expr: Any, point: Dict[Any, Any]) -> Optional[sympy.Expr]:
    value = sympy.N(expr, PRECISION, subs=point)
    if not value.is_number or value.has(sympy.nan, sympy.zoo, sympy.oo, -sympy.oo):
        return None
    return value


def _numeric_check(
    pairs: List[Tuple[Any, Any]], samples: int
) -> Dict[str, Any]:
    """Compare each (a, b) element pair at random points."""
    symbols = sorted(
        set().union(*(sympy.sympify(a - b).free_symbols for a, b in pairs)), key=str
    )
    rng = random.Random(SEED)
    max_abs = sympy.Float(0)
    max_rel = sympy.Float(0)
    checked = 0
    for _ in range(samples * SAMPLE_ATTEMPTS):
        if checked >= samples:
            break
        point = _sample_point(symbols, rng)
        if point is None:
            return {"status": "unsampleable"}
        values = [(_evaluate(a, point), _evaluate(b, point)) for a, b in pairs]
        if any(va is None or vb is None for va, vb in values):
            continue  # singular point; try another
        checked += 1
        for va, vb in values:
            abs_err = abs(va - vb)
            rel_err = abs_err / max(1, abs(va), abs(vb))
            if rel_err > RELATIVE_TOLERANCE:
                return {
                    "status": "mismatch",
                    "counterexample": {str(s): str(v) for s, v in point.items()},
                    "value_a": str(va),
                    "value_b": str(vb),
                }
            max_abs = max(max_abs, abs_err)
            max_rel = max(max_rel, rel_err)
        if not symbols:
            break  # a constant only needs one evaluation
    if checked == 0:
        return {"status": "no_valid_points"}
    return {
        "status": "match",
        "samples": checked,
        "max_error": str(sympy.N(max_abs, 3)),
        "max_relative_error": str(sympy.N(max_rel, 3)),
    }


def check_equivalence(a: Any, b: Any, numeric_samples: int = 20) -> Dict[str, Any]:
    """Decide whether a and b are equal. Returns a dict with a `verdict` field.

    Verdicts: proved_equal, numerically_equal, not_equal, inconclusive.
    """
    if isinstance(a, sympy.Rel) or isinstance(b, sympy.Rel):
        return {
            "verdict": "inconclusive",
            "reason": "check_equivalence compares expressions, not equations. "
                      "Compare lhs - rhs of each equation instead.",
        }
    a_elements, b_elements = _elements(a), _elements(b)
    if isinstance(a, sympy.MatrixBase) != isinstance(b, sympy.MatrixBase) or (
        isinstance(a, sympy.MatrixBase) and a.shape != b.shape
    ):
        return {"verdict": "not_equal", "reason": "The operands have different shapes."}
    pairs = list(zip(a_elements, b_elements))

    # 1. Symbolic proof, element by element
    methods: List[str] = []
    all_sound = True
    proved = True
    for ea, eb in pairs:
        found = _prove_zero(sympy.sympify(ea - eb))
        if found is None:
            proved = False
            break
        if found[0] not in methods:
            methods.append(found[0])
        all_sound = all_sound and found[1]
    if proved and all_sound:
        return {"verdict": "proved_equal", "method": ", ".join(methods)}

    # 2. Numeric spot checks
    if any(sympy.sympify(ea - eb).has(AppliedUndef) for ea, eb in pairs):
        numeric = {"status": "unsampleable_functions"}
    elif numeric_samples <= 0:
        numeric = {"status": "skipped"}
    else:
        numeric = _numeric_check(pairs, numeric_samples)

    if numeric["status"] == "mismatch":
        result = {"verdict": "not_equal", **{k: v for k, v in numeric.items() if k != "status"}}
        if proved:
            result["note"] = (
                f"{', '.join(methods)} reduces the difference to 0, but that rewrite ignores "
                "branch cuts and does not hold at the counterexample."
            )
        return result
    if proved:
        result = {
            "verdict": "proved_equal",
            "method": ", ".join(methods),
            "caveat": "expand_log(force=True) assumes log(a*b) = log(a) + log(b), "
                      "which only holds on principal branches (e.g. positive arguments).",
        }
        if numeric["status"] == "match":
            result["numeric_samples"] = numeric["samples"]
        return result
    if numeric["status"] == "match":
        return {
            "verdict": "numerically_equal",
            "samples": numeric["samples"],
            "max_error": numeric["max_error"],
            "max_relative_error": numeric["max_relative_error"],
            "note": "No symbolic proof found; equal to within tolerance at every sample point.",
        }
    reasons = {
        "unsampleable_functions": "No symbolic proof found, and the expressions contain undefined "
                                  "functions, so they cannot be evaluated numerically.",
        "unsampleable": "No symbolic proof found, and no values satisfy the symbols' assumptions.",
        "no_valid_points": "No symbolic proof found, and every sample point was singular.",
        "skipped": "No symbolic proof found, and numeric_samples is 0.",
    }
    return {"verdict": "inconclusive", "reason": reasons[numeric["status"]]}
